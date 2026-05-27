import discord
from discord.ext import commands

import asyncio
import edge_tts
import random
import os
import wavelink

# =====================================
# CONFIG
# =====================================

TOKEN = "TOKEN_DISCORD"

VOICE_CHANNEL_ID = 123456789

# =====================================
# DISCORD SETUP
# =====================================

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="?",
    intents=intents
)

# =====================================
# LAVALINK CONFIG
# =====================================

LAVALINK_HOST = "http://lava-v4.ajieblogs.eu.org:80"
LAVALINK_PASSWORD = "https://dsc.gg/ajidevserver"

# =====================================
# PLAYER
# =====================================

music_queue = []

is_playing = False

# =====================================
# TTS
# =====================================

tts_queue = asyncio.Queue()

voices = [
    "id-ID-ArdiNeural",
    "id-ID-GadisNeural"
]

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
# GET PLAYER
# =====================================

async def get_player():

    channel = bot.get_channel(
        VOICE_CHANNEL_ID
    )

    if channel is None:
        return None

    player = channel.guild.voice_client

    if not player:

        player = await channel.connect(
            cls=wavelink.Player
        )

    return player

# =====================================
# TTS SPEAK
# =====================================

async def speak(text):

    player = await get_player()

    if player is None:
        return

    while player.playing:
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

    source = discord.FFmpegPCMAudio(
        "voice.mp3"
    )

    player.guild.voice_client.play(
        source
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
# PLAY NEXT
# =====================================

async def play_next(player):

    global is_playing

    if len(music_queue) == 0:

        is_playing = False
        return

    is_playing = True

    query = music_queue.pop(0)

    tracks = await wavelink.Playable.search(
        query
    )

    if not tracks:
        return

    track = tracks[0]

    await player.play(track)

    print(f"Now playing: {track.title}")

# =====================================
# BOT READY
# =====================================

@bot.event
async def on_ready():

    print(f"Login sebagai {bot.user}")

    node = wavelink.Node(
        uri=LAVALINK_HOST,
        password=LAVALINK_PASSWORD
    )

    await wavelink.Pool.connect(
        client=bot,
        nodes=[node]
    )

    print("Lavalink connected")

    await get_player()

    bot.loop.create_task(
        tts_worker()
    )

# =====================================
# TRACK END
# =====================================

@bot.event
async def on_wavelink_track_end(
    payload
):

    player = payload.player

    await play_next(player)

# =====================================
# JOIN DETECT
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
# PLAY COMMAND
# =====================================

@bot.command()
async def play(ctx, *, query):

    global is_playing

    player = await get_player()

    if player is None:

        return await ctx.send(
            "Voice channel tidak ditemukan"
        )

    music_queue.append(query)

    await ctx.send(
        f"Masuk queue: {query}"
    )

    if not player.playing and not is_playing:

        await play_next(player)

# =====================================
# SKIP
# =====================================

@bot.command()
async def skip(ctx):

    player = ctx.guild.voice_client

    if player and player.playing:

        await player.skip()

        await ctx.send(
            "Skip lagu"
        )

# =====================================
# STOP
# =====================================

@bot.command()
async def stop(ctx):

    global music_queue
    global is_playing

    player = ctx.guild.voice_client

    music_queue.clear()

    is_playing = False

    if player:

        await player.stop()

    await ctx.send(
        "Music stopped"
    )

# =====================================
# QUEUE
# =====================================

@bot.command()
async def queue(ctx):

    if len(music_queue) == 0:

        return await ctx.send(
            "Queue kosong"
        )

    text = "\n".join(
        [
            f"{i+1}. {song}"
            for i, song in enumerate(music_queue)
        ]
    )

    await ctx.send(
        f"Queue:\n{text}"
    )

# =====================================
# LEAVE
# =====================================

@bot.command()
async def leave(ctx):

    player = ctx.guild.voice_client

    if player:

        await player.disconnect()

    await ctx.send(
        "Bot keluar VC"
    )

# =====================================
# RUN
# =====================================

bot.run(TOKEN)
