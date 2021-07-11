from typing import Set
import logging
import asyncio
import os

import discord
import random

PROB = 1/200
SELF_ID = 863831962081951784
ADMIN_ID = 402456897812168705
LOG_CHANNEL = 863852571458142278
FOR_REAL = True
COUNTDOWN = 10

KICKSET: Set[int] = set()

def save_kickset() -> None:
    global KICKSET
    with open("kickset.txt", "w") as ks:
        ks.write("\n".join(str(x) for x in KICKSET))

def load_kickset() -> None:
    global KICKSET
    if not os.path.isfile("kickset.txt"):
        return
    with open("kickset.txt", "r") as ks:
        KICKSET = set(int(x) for x in ks.read().split("\n"))

load_kickset()

api_logger = logging.getLogger("discord")
api_logger.setLevel(logging.INFO)

fhandler = logging.FileHandler("discord.log")
fhandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

api_logger.addHandler(fhandler)


app_logger = logging.getLogger("banner")
app_logger.setLevel(logging.INFO)

fhandler = logging.FileHandler("app.log")
fhandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
app_logger.addHandler(fhandler)

shandler = logging.StreamHandler()
shandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
app_logger.addHandler(shandler)


intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

IS_BANNING = False

@client.event
async def on_message(msg: discord.Message):
    global IS_BANNING

    if msg.author.id == SELF_ID:
        return

    if msg.type == discord.MessageType.new_member:
        return

    if IS_BANNING:
        return

    app_logger.info(f"{msg.author.name!r} sent {msg.content!r}")
    if random.random() < PROB:
        IS_BANNING = True

        if not isinstance(msg.channel, discord.TextChannel):
            app_logger.warn("message outside textchannel")
            return

        guild = msg.channel.guild
        members = guild.members
        members = [
            member
            for member in members
            if not member.id == SELF_ID and not member.id == ADMIN_ID
        ]
        if len(members) == 0:
            return
        member = random.choice(members)

        ban_word = "ban"
        banned_word = "banned"
        Banned_word = "Banned"
        if member.id == 354579932837445635:
            ban_word = "bean"
            banned_word = "beaned"
            Banned_word = "Beaned"

        if member.id not in KICKSET:
            ban_word = "kick"
            banned_word = "kicked"
            Banned_word = "Kicked"
            app_logger.info(f"Kicking {member}...")
        else:
            app_logger.info(f"Banning {member}...")

        reply = await msg.reply(f"<@{member.id}> will be {banned_word} in {COUNTDOWN} seconds...")

        async def countdown() -> None:
            global IS_BANNING
            try:
                for i in range(COUNTDOWN, -1, -1):
                    await reply.edit(content=f"<@{member.id}> will be {banned_word} in {i} seconds...")
                    await asyncio.sleep(1)

                if FOR_REAL:
                    try:
                        if member.id not in KICKSET:
                            await member.kick(reason=f"Message by {member} ({msg.id})")
                            KICKSET.add(member.id)
                        else:
                            await member.ban(reason=f"Message by {member} ({msg.id})", delete_message_days=0)
                    except discord.errors.Forbidden as _:
                        await reply.edit(content=f"Could not {ban_word} <@{member.id}> :pensive:")
                        return

                await reply.delete()
                app_logger.info(f"banned {member}...")
                log_channel = guild.get_channel(LOG_CHANNEL)
                if log_channel is None or not isinstance(log_channel, discord.TextChannel):
                    app_logger.warning("aaaa log is gone :(")
                    return

                await log_channel.send(
                    content=f"<@{member.id}> has been {banned_word}",
                    embed=discord.Embed(
                        title=f"{Banned_word} by {msg.author.name}",
                        description=f"{msg.content}",
                        url=f"{msg.to_reference().jump_url}",
                        colour=discord.Colour.red(),
                    )
                )
            finally:
                IS_BANNING = False
                save_kickset()

        asyncio.create_task(countdown())


if __name__ == "__main__":
    with open("token.txt", "r") as tok_file:
        token = tok_file.read().strip()

    app_logger.info("starting..,")

    client.run(token)
