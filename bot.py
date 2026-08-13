import os
from datetime import time
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

ZEITZONE = ZoneInfo("Europe/Berlin")

OEFFNUNG = time(8, 0)
SCHLIESSUNG = time(22, 0)

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


def ist_geoeffnet():
    jetzt = discord.utils.utcnow().astimezone(ZEITZONE)
    uhrzeit = jetzt.time().replace(tzinfo=None)

    return OEFFNUNG <= uhrzeit < SCHLIESSUNG


async def server_oeffnen_oder_schliessen():

    for guild in bot.guilds:

        everyone = guild.default_role

        if ist_geoeffnet():

            # 🟢 SERVER ÖFFNEN
            await guild.edit(
                reason="Öffnungszeiten: 08:00–22:00"
            )

            for channel in guild.channels:

                if isinstance(channel, discord.abc.GuildChannel):

                    try:
                        await channel.set_permissions(
                            everyone,
                            send_messages=True,
                            reason="Server geöffnet"
                        )

                    except discord.Forbidden:
                        print(
                            f"Keine Berechtigung für: {channel.name}"
                        )

            print(f"🟢 {guild.name}: SERVER GEÖFFNET")

        else:

            # 🔴 SERVER SCHLIESSEN
            for channel in guild.channels:

                if isinstance(channel, discord.abc.GuildChannel):

                    try:
                        await channel.set_permissions(
                            everyone,
                            send_messages=False,
                            reason="Server geschlossen"
                        )

                    except discord.Forbidden:
                        print(
                            f"Keine Berechtigung für: {channel.name}"
                        )

            print(f"🔴 {guild.name}: SERVER GESCHLOSSEN")


@tasks.loop(minutes=1)
async def oeffnungszeiten_loop():

    try:
        await server_oeffnen_oder_schliessen()

    except Exception as e:
        print(f"Fehler bei der Öffnungszeit: {e}")


@oeffnungszeiten_loop.before_loop
async def vorbereitung():

    await bot.wait_until_ready()


@bot.event
async def on_ready():

    print(f"Bot gestartet: {bot.user}")

    await server_oeffnen_oder_schliessen()

    if not oeffnungszeiten_loop.is_running():
        oeffnungszeiten_loop.start()


bot.run(TOKEN)