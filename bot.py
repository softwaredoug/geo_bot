# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    print("Hello World!")
    print(message.content)
    print(message)
    if message.content.startswith('!quiz_me'):
        await message.channel.send('Hello!')
    if message.content.startswith('answer:'):
        await message.channel.send('Hello!')


client.run(TOKEN)
