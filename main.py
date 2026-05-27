import edge_tts
import os
import discord
from discord.ext import commands
import asyncio

TOKEN = ""

VOICE_CHANNEL_ID = 1493993071728267301

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None

@bot.event
async def on_ready():
    global voice_client

    channel = bot.get_channel(VOICE_CHANNEL_ID)

    voice_client = await channel.connect()

    print("Bot online")

import edge_tts
import os

async def speak(text):

    if os.path.exists("voice.mp3"):
        os.remove("voice.mp3")

    communicate = edge_tts.Communicate(
        text=text,
        voice="id-ID-ArdiNeural",
        rate="+10%"
    )

    await communicate.save("voice.mp3")

    while voice_client.is_playing():
        await asyncio.sleep(1)

    voice_client.play(
        discord.FFmpegPCMAudio("voice.mp3")
    )

@bot.event
async def on_voice_state_update(member, before, after):

    if member.bot:
        return

    if before.channel is None and after.channel is not None:

        await speak(
            f"Halo {member.display_name}, selamat datang"
        )

bot.run(TOKEN)
