'''discord bot'''
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True          # Required to see members in a server
intents.message_content = True  # Required to read message content
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    '''check if bot online'''
    print('Bot Online!')

@bot.event
async def on_message(message):
    '''This function runs every time a message is sent'''
    # don't answer itself
    if message.author == bot.user:
        return

    mes = message.content
    if mes == 'ping':
        await message.channel.send('Pong!')
    elif mes == '1':
        await message.channel.send('Correct!')

    await bot.process_commands(message) # check if all condition is not met

bot.run(token)
