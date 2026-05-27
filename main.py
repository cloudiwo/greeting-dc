import discord
from discord.ext import commands, tasks
from gtts import gTTS
import asyncio
import os
import random

TOKEN = "TOKEN_BOT_LU"

# ID SERVER & VOICE CHANNEL
GUILD_ID = 1234567890123
VOICE_CHANNEL_ID = 1234567890123

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None

# =========================
# RANDOM SAPAAN
# =========================
WELCOME_MESSAGES = [
    "Halo {name}, selamat datang di voice chat.",
    "Yo {name}, akhirnya join juga.",
    "Selamat datang {name}, jangan lupa ngopi.",
    "Halo bosku {name}.",
    "Waduh ada {name}, rame nih.",
]

LEAVE_MESSAGES = [
    "Yah {name} keluar.",
    "Dadah {name}.",
    "{name} left the voice channel.",
]

# =========================
# CONNECT ULANG OTOMATIS
# =========================
@tasks.loop(seconds=15)
async def auto_reconnect():
    global voice_client

    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(VOICE_CHANNEL_ID)

    if voice_client is None or not voice_client.is_connected():
        try:
            voice_client = await channel.connect()
            print("Reconnect berhasil")
        except:
            pass

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    global voice_client

    print(f"Login sebagai {bot.user}")

    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(VOICE_CHANNEL_ID)

    try:
        voice_client = await channel.connect()
        print("Bot masuk voice")
    except:
        print("Sudah connect")

    auto_reconnect.start()

# =========================
# PLAY TTS
# =========================
async def play_tts(text):
    global voice_client

    if voice_client is None:
        return

    filename = "tts.mp3"

    tts = gTTS(text=text, lang="id")
    tts.save(filename)

    while voice_client.is_playing():
        await asyncio.sleep(1)

    voice_client.play(
        discord.FFmpegPCMAudio(
            filename,
            options="-loglevel panic"
        )
    )

    while voice_client.is_playing():
        await asyncio.sleep(1)

    os.remove(filename)

# =========================
# DETEKSI JOIN/LEAVE
# =========================
@bot.event
async def on_voice_state_update(member, before, after):

    if member.bot:
        return

    # JOIN
    if before.channel is None and after.channel is not None:

        text = random.choice(WELCOME_MESSAGES).format(
            name=member.display_name
        )

        await play_tts(text)

    # LEAVE
    elif before.channel is not None and after.channel is None:

        text = random.choice(LEAVE_MESSAGES).format(
            name=member.display_name
        )

        await play_tts(text)

# =========================
# COMMAND PING
# =========================
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# =========================
# COMMAND JOIN MANUAL
# =========================
@bot.command()
async def join(ctx):

    global voice_client

    if ctx.author.voice:

        channel = ctx.author.voice.channel

        if voice_client is None:
            voice_client = await channel.connect()
        else:
            await voice_client.move_to(channel)

        await ctx.send("Masuk voice.")

# =========================
# COMMAND LEAVE
# =========================
@bot.command()
async def leave(ctx):

    global voice_client

    if voice_client:
        await voice_client.disconnect()
        voice_client = None

    await ctx.send("Keluar voice.")

# =========================
# RUN
# =========================
bot.run(TOKEN)
