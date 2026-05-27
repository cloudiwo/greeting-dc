import discord
from discord.ext import commands
import wavelink

TOKEN = "TOKEN"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="?",
    intents=intents
)

@bot.event
async def on_ready():

    print(bot.user)

    node = wavelink.Node(
        uri="http://lava-v4.ajieblogs.eu.org:80",
        password="https://dsc.gg/ajidevserver"
    )

    await wavelink.Pool.connect(
        client=bot,
        nodes=[node]
    )

    print("Lavalink connected")

@bot.command()
async def play(ctx, *, search):

    if not ctx.author.voice:

        return await ctx.send(
            "Join VC dulu"
        )

    player = ctx.voice_client

    if not player:

        player = await ctx.author.voice.channel.connect(
            cls=wavelink.Player
        )

    tracks = await wavelink.Playable.search(
        search
    )

    if not tracks:

        return await ctx.send(
            "Lagu tidak ditemukan"
        )

    track = tracks[0]

    await player.play(track)

    await ctx.send(
        f"Now playing: {track.title}"
    )

bot.run(TOKEN)
