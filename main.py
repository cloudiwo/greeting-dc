import discord
from discord.ext import commands
from discord import app_commands

import asyncio
import edge_tts
import yt_dlp
import random
import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# =====================================
# CONFIG
# =====================================

TOKEN = "TOKEN_DISCORD"

VOICE_CHANNEL_ID = 123456789

SPOTIFY_CLIENT_ID = "CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "CLIENT_SECRET"

# =====================================
# SPOTIFY
# =====================================

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

# =====================================
# DISCORD SETUP
# =====================================

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

voice_client = None

# =====================================
# MUSIC QUEUE
# =====================================

music_queue = []

is_playing = False

# =====================================
# TTS QUEUE
# =====================================

tts_queue = asyncio.Queue()

# =====================================
# RANDOM VOICES
# =====================================

voices = [
    "id-ID-ArdiNeural",
    "id-ID-GadisNeural"
]

# =====================================
# RANDOM WELCOME MESSAGE
# =====================================

welcome_messages = [
    "Halo {name}, selamat datang",
    "Welcome {name}",
    "Yo {name}, akhirnya join juga",
    "Hai {name}, semoga betah ya",
    "Waduh ada {name} nih",
    "Halo bang {name}",
    "Mantap {name} baru join",
    "Selamat datang kembali {name}",
    "Hai hai {name}",
    "{name} telah datang"
]

# =====================================
# ENSURE VOICE
# =====================================

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

            print("Bot masuk voice")

        except Exception as e:
            print(e)

# =====================================
# TTS SPEAK
# =====================================

async def speak(text):

    global voice_client

    await ensure_voice()

    if voice_client is None:
        return

    while voice_client.is_playing():
        await asyncio.sleep(1)

    if os.path.exists("voice.mp3"):
        os.remove("voice.mp3")

    selected_voice = random.choice(voices)

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

# =====================================
# TTS WORKER
# =====================================

async def tts_worker():

    await bot.wait_until_ready()

    while not bot.is_closed():

        text = await tts_queue.get()

        try:

            delay = random.randint(2, 5)

            await asyncio.sleep(delay)

            await speak(text)

        except Exception as e:
            print(e)

        tts_queue.task_done()

# =====================================
# YOUTUBE AUDIO
# =====================================

async def get_audio_source(url):

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

        return info["url"], info.get("title")

# =====================================
# PLAY NEXT SONG
# =====================================

async def play_next():

    global is_playing

    if len(music_queue) == 0:

        is_playing = False
        return

    is_playing = True

    url = music_queue.pop(0)

    stream_url, title = await get_audio_source(url)

    ffmpeg_options = {
        "before_options":
            "-reconnect 1 "
            "-reconnect_streamed 1 "
            "-reconnect_delay_max 5",
        "options": "-vn"
    }

    source = discord.FFmpegPCMAudio(
        stream_url,
        **ffmpeg_options
    )

    def after_play(error):
        asyncio.run_coroutine_threadsafe(
            play_next(),
            bot.loop
        )

    voice_client.play(
        source,
        after=after_play
    )

    print(f"Now playing: {title}")

# =====================================
# SPOTIFY LINK SUPPORT
# =====================================

async def spotify_to_youtube(url):

    track = sp.track(url)

    name = track["name"]

    artist = track["artists"][0]["name"]

    query = f"{name} {artist} audio"

    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            query,
            download=False
        )

        return info["entries"][0]["webpage_url"]

# =====================================
# BOT READY
# =====================================

@bot.event
async def on_ready():

    print(f"Login sebagai {bot.user}")

    await ensure_voice()

    bot.loop.create_task(
        tts_worker()
    )

    try:

        synced = await bot.tree.sync()

        print(f"Slash synced: {len(synced)}")

    except Exception as e:
        print(e)

# =====================================
# JOIN VC DETECT
# =====================================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if member.bot:
        return

    if before.channel is None and after.channel is not None:

        text = random.choice(
            welcome_messages
        ).format(
            name=member.display_name
        )

        await tts_queue.put(text)

# =====================================
# /PLAY
# =====================================

@bot.tree.command(
    name="play",
    description="Play music"
)
async def play(
    interaction: discord.Interaction,
    url: str
):

    global is_playing

    await interaction.response.defer()

    await ensure_voice()

    if "spotify.com" in url:
        url = await spotify_to_youtube(url)

    music_queue.append(url)

    await interaction.followup.send(
        "Lagu masuk queue"
    )

    if not is_playing:
        await play_next()

# =====================================
# /SKIP
# =====================================

@bot.tree.command(
    name="skip",
    description="Skip song"
)
async def skip(
    interaction: discord.Interaction
):

    if voice_client and voice_client.is_playing():

        voice_client.stop()

        await interaction.response.send_message(
            "Skip lagu"
        )

# =====================================
# /STOP
# =====================================

@bot.tree.command(
    name="stop",
    description="Stop music"
)
async def stop(
    interaction: discord.Interaction
):

    global music_queue
    global is_playing

    music_queue.clear()

    is_playing = False

    if voice_client:
        voice_client.stop()

    await interaction.response.send_message(
        "Music stopped"
    )

# =====================================
# /QUEUE
# =====================================

@bot.tree.command(
    name="queue",
    description="Show queue"
)
async def queue(
    interaction: discord.Interaction
):

    if len(music_queue) == 0:

        await interaction.response.send_message(
            "Queue kosong"
        )

        return

    text = "\n".join(
        [
            f"{i+1}. {song}"
            for i, song in enumerate(music_queue)
        ]
    )

    await interaction.response.send_message(
        f"Queue:\n{text}"
    )

# =====================================
# /LEAVE
# =====================================

@bot.tree.command(
    name="leave",
    description="Disconnect bot"
)
async def leave(
    interaction: discord.Interaction
):

    global voice_client

    if voice_client:

        await voice_client.disconnect()

        voice_client = None

    await interaction.response.send_message(
        "Bot keluar VC"
    )

# =====================================
# RUN BOT
# =====================================

bot.run(TOKEN)
