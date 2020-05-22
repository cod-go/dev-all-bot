import os

from rules import WELCOME, ABOUT, COMMANDS, ADMS

import discord
from dotenv import load_dotenv

import databaser

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

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

    if message.content in COMMANDS or '/canal' in message.content or '/poll' in message.content:
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

    elif message.content[:5] == '/poll':
        votacao = message.content[6:]
        votacao = votacao.split(" ")

        titulo = votacao[0]

        databaser.cursor.execute(f"select titulo from votacoes where titulo='{titulo}'")
        titulo_votacao = databaser.cursor.fetchone()

        if titulo_votacao is not None:
            # Verifica se possui uma opção para voto
            if len(votacao) > 1:
                voto = votacao[1]
                # Testando se a opção do voto existe
                databaser.cursor.execute(f"select opcao from alternativas where votacao='{titulo}' and opcao='{voto}'")
                opcao_votacao = databaser.cursor.fetchone()
                if opcao_votacao is not None:
                    # Registrando voto
                    databaser.cursor.execute(f"insert into votos(nome, opcao, votacao) "
                                             f"values ('{member.name}','{voto}','{titulo}')")
                    databaser.conn.commit()
            else:
                response = f"Votação {titulo}\n"
                # Consulta as informações sobre as opções
                databaser.cursor.execute(f"select opcao from alternativas where votacao='{titulo}'")
                opcoes = databaser.cursor.fetchall()
                for opcao in opcoes:
                    databaser.cursor.execute(f"select count(*) from votos where votacao='{titulo}' and opcao='{opcao[0]}'")
                    total = databaser.cursor.fetchone()
                    response += f"{opcao[0]} - {total[0]}\n"
                await message.channel.send(response)
        else:
            # Registrando pergunta
            databaser.cursor.execute(f"insert into votacoes(titulo) values ('{titulo}')")
            databaser.conn.commit()
            for opcao in votacao[1:]:
                # Registrando opções
                databaser.cursor.execute(f"insert into alternativas(opcao, votacao) "
                                         f"values ('{opcao}', '{titulo}')")
                databaser.conn.commit()

    # Verifica se a mensagem começa com /canal
    elif message.content[:6] == '/canal':
        # Define a resposta como tudo a partir do '/canal '
        response = message.content[7:]

        # Percorre a lista de servidores ao qual o bot faz part, e encotra a que está no arquivo .env
        guild = None
        for g in client.guilds:
            if g.name == GUILD:
                guild = g
                break

        # Percorre a lista de membros do servidor
        for member in guild.members:
            # Ignora o bot na lista de usuários
            if member != client.user:
                # Tenta enviar uma mensagem privada
                try:
                    await member.create_dm()
                    await member.dm_channel.send(response)
                except:
                    print(member.name)

client.run(TOKEN)
