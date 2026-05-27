import discord
from discord.ext import commands
import asyncio
import edge_tts
import random
import os

TOKEN = "TOKEN_DISCORD"

VOICE_CHANNEL_ID = 123456789

# =========================
# Discord setup
# =========================

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

voice_client = None

# =========================
# Random voice
# =========================

voices = [
    "id-ID-ArdiNeural",
    "id-ID-GadisNeural",
]

# =========================
# Random welcome text
# =========================

welcome_messages = [
    "Halo {name}, selamat datang",
    "Yo {name}, akhirnya join juga",
    "Welcome {name}",
    "Hai {name}, semoga betah ya",
    "Mantap {name} baru masuk voice",
    "Halo bang {name}",
    "Waduh ada {name} nih",
    "{name} telah datang",
    "Selamat datang kembali {name}",
    "Hai hai {name}"
]

# =========================
# Bot ready
# =========================

@bot.event
async def on_ready():
    global voice_client

    print(f"Login sebagai {bot.user}")

    channel = bot.get_channel(VOICE_CHANNEL_ID)

    if channel is None:
        print("Voice channel tidak ditemukan")
        return

    voice_client = await channel.connect()

    print("Bot masuk voice channel")

# =========================
# Speak function
# =========================

async def speak(text):

    global voice_client

    if voice_client is None:
        return

    # tunggu audio selesai
    while voice_client.is_playing() or voice_client.is_paused():
        await asyncio.sleep(0.5)

    # hapus file lama
    if os.path.exists("voice.mp3"):
        os.remove("voice.mp3")

    # pilih voice random
    selected_voice = random.choice(voices)

    # generate TTS
    communicate = edge_tts.Communicate(
        text=text,
        voice=selected_voice,
        rate="+10%",
        pitch="+2Hz"
    )

    await communicate.save("voice.mp3")

    # play audio
    voice_client.play(
        discord.FFmpegPCMAudio("voice.mp3")
    )

# =========================
# Detect user join VC
# =========================

@bot.event
async def on_voice_state_update(member, before, after):

    if member.bot:
        return

    # user join VC
    if before.channel is None and after.channel is not None:

        text = random.choice(
            welcome_messages
        ).format(
            name=member.display_name
        )

        print(f"Memutar suara: {text}")

        await speak(text)

# =========================
# Run bot
# =========================

bot.run(TOKEN)
