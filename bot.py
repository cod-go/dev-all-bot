import os
import datetime

from rules import WELCOME, ABOUT, COMMANDS, ADMS

from discord.ext import commands
from dotenv import load_dotenv

import databaser

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='/')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(WELCOME.format(member.name))


@bot.command(name='regras', help='Envia as regras do servidor no privado do usuário')
async def regras(ctx):
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send(WELCOME.format(ctx.author.name))


@bot.command(name='adms', help='Informações sobre os administradores do servidor')
async def adms(ctx):
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send(ADMS)


@bot.command(name='sobre', help='Informações sobre o servidor')
async def sobre(ctx):
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send(ABOUT)


@bot.command(name='ajuda', help='Informações sobre os comandos do DevAllBot')
async def ajuda(ctx):
    await ctx.author.create_dm()
    response = 'Comandos registrados do sistema: \n'
    for command in COMMANDS:
        response += command+'\n'
    await ctx.author.dm_channel.send(response)


@bot.command(name='canal', help='Comando para enviar mensagem a todos os membros do servidor')
@commands.has_role('adm')
async def canal(ctx, message):
    # Define a resposta como tudo a partir do '/canal '
    response = message

    # Percorre a lista de servidores ao qual o bot faz part, e encotra a que está no arquivo .env
    guild = None
    for g in bot.guilds:
        if g.name == GUILD:
            guild = g
            break

    # Percorre a lista de membros do servidor
    for member in guild.members:
        # Ignora o bot na lista de usuários
        if member != bot.user:
            # Tenta enviar uma mensagem privada
            try:
                await member.create_dm()
                await member.dm_channel.send(response)
            except:
                print(member.name)


@bot.command(name='poll')
async def poll(ctx, poll_name, option=None):
    databaser.cursor.execute(f"select titulo from votacoes where titulo='{poll_name}'")
    titulo_votacao = databaser.cursor.fetchone()

    if titulo_votacao is not None:
        # Verifica se possui uma opção para voto
        if option is not None:
            # Testando se a opção do voto existe
            databaser.cursor.execute(f"select opcao from alternativas where votacao='{poll_name}' and opcao='{option}'")
            opcao_votacao = databaser.cursor.fetchone()
            if opcao_votacao is not None:
                # Registrando voto
                databaser.cursor.execute(f"insert into votos(nome, opcao, votacao) "
                                         f"values ('{ctx.author.name}','{option}','{poll_name}')")
                databaser.conn.commit()
                await ctx.send("Voto computado com sucesso ;)")
        # Verifica se foi passado alguma opção de voto
        else:
            response = f"Votação {poll_name}\n"
            # Consulta as informações sobre as opções
            databaser.cursor.execute(f"select opcao from alternativas where votacao='{poll_name}'")
            opcoes = databaser.cursor.fetchall()
            for opcao in opcoes:
                databaser.cursor.execute(f"select count(*) from votos where votacao='{poll_name}' and opcao='{opcao[0]}'")
                total = databaser.cursor.fetchone()
                response += f"{opcao[0]} - {total[0]}\n"
            await ctx.send(response)
    else:
        await ctx.send("Não há nenhuma votação com o título informado :/")


@bot.command(name='new-poll')
@commands.has_role('adm')
async def new_poll(ctx, poll_name, *options):
    # Registrando pergunta
    databaser.cursor.execute(f"insert into votacoes(titulo) values ('{poll_name}')")
    databaser.conn.commit()
    for opcao in options:
        # Registrando opções
        databaser.cursor.execute(f"insert into alternativas(opcao, votacao) "
                                 f"values ('{opcao}', '{poll_name}')")
        databaser.conn.commit()
    await ctx.send("Votação registrada com sucesso")


@bot.command(name='cronograma')
async def cronograma(ctx):
    response = "Cronograma\n"
    databaser.cursor.execute("SELECT titulo, orador, data FROM cronogramas")
    cronogramas = databaser.cursor.fetchall()
    for row in cronogramas:
        data = datetime.datetime.strptime(row[2], '%Y-%m-%d').date()
        data = data.strftime('%d/%m/%Y')
        response += f'- {row[0]} - {row[1]} - {data}\n'
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send(response)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Você não têm permissão para usar esse comando :/')

bot.run(TOKEN)
