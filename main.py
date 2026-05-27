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
# Queue system
# =========================

tts_queue = asyncio.Queue()

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
    "Selamat datang {name}",
    "Hai {name}, dari mana aja ",
    "Mantap {name} baru masuk voice",
    "Halo guys {name} basru masuk nih",
    "Waduh ada {name} nih",
    "{name} telah datang",
    "Selamat datang kembali {name}",
    "Hai hai {name}"
]

# =========================
# Ensure voice connection
# =========================

async def ensure_voice():

    global voice_client

    channel = bot.get_channel(
        VOICE_CHANNEL_ID
    )

    if channel is None:
        return

    if voice_client is None or not voice_client.is_connected():

        try:
            voice_client = await channel.connect(
                reconnect=True,
                timeout=60
            )

            print("Bot masuk voice channel")

        except Exception as e:
            print("Voice error:", e)

# =========================
# Speak function
# =========================

async def speak(text):

    global voice_client

    await ensure_voice()

    if voice_client is None:
        return

    # tunggu audio selesai
    while voice_client.is_playing() or voice_client.is_paused():
        await asyncio.sleep(0.5)

    # hapus file lama
    if os.path.exists("voice.mp3"):
        os.remove("voice.mp3")

    selected_voice = random.choice(
        voices
    )

    communicate = edge_tts.Communicate(
        text=text,
        voice=selected_voice,
        rate="+10%",
        pitch="+2Hz"
    )

    await communicate.save("voice.mp3")

    voice_client.play(
        discord.FFmpegPCMAudio("voice.mp3")
    )

# =========================
# Queue worker
# =========================

async def tts_worker():

    await bot.wait_until_ready()

    while not bot.is_closed():

        text = await tts_queue.get()

        try:

            # delay sebelum ngomong
            delay = random.randint(2, 5)

            print(f"Delay {delay} detik")

            await asyncio.sleep(delay)

            await speak(text)

        except Exception as e:
            print("TTS Error:", e)

        tts_queue.task_done()

# =========================
# Bot ready
# =========================

@bot.event
async def on_ready():

    print(f"Login sebagai {bot.user}")

    bot.loop.create_task(
        tts_worker()
    )

# =========================
# Detect join VC
# =========================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if member.bot:
        return

    # user join VC
    if before.channel is None and after.channel is not None:

        text = random.choice(
            welcome_messages
        ).format(
            name=member.display_name
        )

        print(f"Queue suara: {text}")

        await tts_queue.put(text)

# =========================
# Run bot
# =========================

bot.run(TOKEN)
