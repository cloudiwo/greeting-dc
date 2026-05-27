from elevenlabs.client import ElevenLabs
import discord
from discord.ext import commands
import asyncio

TOKEN = "TOKEN_DISCORD"
ELEVEN_API = "API_KEY_ELEVEN"

VOICE_CHANNEL_ID = 123456789

client = ElevenLabs(
    api_key=ELEVEN_API
)

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

async def speak(text):

    audio = client.text_to_speech.convert(
        text=text,
        voice_id="21m00Tcm4TlvDq8ikWAM",
        model_id="eleven_multilingual_v2"
    )

    with open("voice.mp3", "wb") as f:
        for chunk in audio:
            f.write(chunk)

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
