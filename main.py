import discord
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
