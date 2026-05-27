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
bot.run(TOKEN)
