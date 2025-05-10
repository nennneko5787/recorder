import asyncio
import io
import os
import time
import wave
from collections import deque
from typing import Dict, Optional

import discord
import dotenv
import numpy as np
from discord import app_commands
from discord.ext import commands
from discord.ext.voice_recv import AudioSink, VoiceData, VoiceRecvClient, WaveSink
from discord.ext.voice_recv.silence import SilenceGenerator
from pydub import AudioSegment

dotenv.load_dotenv()
discord.opus._load_default()

BLACKLIST = [1130546409913995354, 1095588875411390587]


class MultiAudioSink(AudioSink):
    def __init__(self):
        super().__init__()
        self.user_buffers: Dict[int, io.BytesIO] = {}
        self.user_wave_sinks: Dict[int, WaveSink] = {}
        self.audio_queue: Dict[int, deque[VoiceData]] = {}
        self.sample_rate = 48000
        self.channels = 2
        self.running = True

    def wants_opus(self) -> bool:
        return False

    def _ensure_user(self, user: discord.User):
        uid = user.id
        if uid not in self.user_buffers and uid not in BLACKLIST:
            buf = io.BytesIO()
            self.user_buffers[uid] = buf
            self.user_wave_sinks[uid] = WaveSink(buf)
            self.audio_queue[uid] = deque()

    def write(self, user: Optional[discord.User], data: VoiceData) -> None:
        if user is None or user.bot or user.id in BLACKLIST:
            return
        self._ensure_user(user)
        self.audio_queue[user.id].append(data)

    async def run_timer(self, duration: float):
        frame_time = 0.02  # 20ms
        total_frames = int(duration / frame_time)
        silence_frame = bytes(1920 * 2)  # 2ch x 16bit = 2bytes/sample

        for _ in range(total_frames):
            if not self.running:
                break

            for uid in list(self.user_wave_sinks.keys()):
                sink = self.user_wave_sinks[uid]
                queue = self.audio_queue[uid]
                if queue:
                    data = queue.popleft()
                    sink.write(data.source, data)
                else:
                    sink.write(
                        None, VoiceData(source=None, pcm=silence_frame, packet=b"")
                    )

            await asyncio.sleep(frame_time)

    def cleanup(self):
        self.running = False

    def get_all_audio(self) -> Dict[int, bytes]:
        return {uid: buf.getvalue() for uid, buf in self.user_buffers.items()}

    def mix_audio(self, audio_data_dict: Dict[int, bytes]) -> Optional[bytes]:
        audio_arrays = []
        sample_rate = 0
        num_channels = 0
        sample_width = 0

        for audio_data in audio_data_dict.values():
            if len(audio_data) <= 44:
                continue

            with wave.open(io.BytesIO(audio_data), "rb") as wav_file:
                params = wav_file.getparams()
                sample_rate = params.framerate
                num_channels = params.nchannels
                sample_width = params.sampwidth

                frames = wav_file.readframes(params.nframes)
                audio_array = np.frombuffer(frames, dtype=np.int16)
                audio_arrays.append(audio_array)

        if not audio_arrays:
            return None

        max_length = max(len(arr) for arr in audio_arrays)
        padded_audio_arrays = [
            np.pad(arr, (0, max_length - len(arr)), "constant") for arr in audio_arrays
        ]
        mixed_audio = np.mean(padded_audio_arrays, axis=0).astype(np.int16)

        output_buffer = io.BytesIO()
        with wave.open(output_buffer, "wb") as output_wav:
            output_wav.setnchannels(num_channels)
            output_wav.setsampwidth(sample_width)
            output_wav.setframerate(sample_rate)
            output_wav.writeframes(mixed_audio.tobytes())

        output_buffer.seek(0)
        return output_buffer.read()


bot = commands.Bot([], intents=discord.Intents.default())


@bot.event
async def setup_hook():
    pass
    # await bot.tree.sync()


sink = MultiAudioSink()


@bot.tree.command(name="record")
async def recordCommand(
    interaction: discord.Interaction, seconds: app_commands.Range[int, 0] = 10
):
    await interaction.response.send_message("録音中...", ephemeral=True)
    channel = interaction.user.voice.channel

    sink = MultiAudioSink()
    vc = await channel.connect(cls=VoiceRecvClient)
    vc.listen(sink)

    await sink.run_timer(seconds)
    vc.stop_listening()
    await vc.disconnect()
    vc.cleanup()
    sink.cleanup()

    all_audio_data = sink.get_all_audio()
    combined = sink.mix_audio(all_audio_data)
    if combined:
        await bot.get_channel(1362131923136155842).send(
            file=discord.File(io.BytesIO(combined), "recorded.wav")
        )


@bot.tree.command(name="stop")
async def stopCommand(interaction: discord.Interaction):
    await interaction.guild.voice_client.disconnect()


bot.run(os.getenv("discord"))
