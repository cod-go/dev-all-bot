import os

from rules import WELCOME, ABOUT, COMMANDS, ADMS

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(WELCOME.format(member.name))


@client.event
async def on_message(message):
    member = message.author

    if member == client.user:
        return

    if message.content in COMMANDS:
        await member.create_dm()
    else:
        return

    if message.content == '/regras':
        await member.dm_channel.send(WELCOME.format(message.author.name))

    elif message.content == '/sobre':
        await member.dm_channel.send(ABOUT)
    
    elif message.content == '/adms':
        await member.dm_channel.send(ADMS)

    elif message.content == '/help':
        response = 'Comandos registrados do sistema: \n'
        for command in COMMANDS:
            response += command+'\n'
        await member.dm_channel.send(response)

client.run(TOKEN)
