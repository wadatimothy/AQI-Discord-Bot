import discord
from discord.ext import commands
from API_code import *

NOMINATIM_F_URL = 'https://nominatim.openstreetmap.org/search?'
PURPLEAIR_URL = 'https://www.purpleair.com/data.json'

TOKEN = 'Replace with Disc Token'
GUILD = 'Replace with Disc server name'

bot = commands.Bot(command_prefix='!')

@bot.command(name='speak')
async def i_speak(ctx):
    await ctx.send('Hello sir.')

@bot.command(name='rng')
async def rng(ctx, bot_num: int, top_num: int):
    await ctx.send(random.randint(bot_num, top_num))

@bot.command(name='AQI')
async def get_aqi(ctx, city, state):
    location = ' '.join(city.split('_')) + ', ' + state
    aqi = find_aqi(location)
    await ctx.send(aqi)


@bot.command(name='FindAQI')
async def get_aqi(ctx, city, state):
    location = ' '.join(city.split('_')) + ', ' + state
    await ctx.send(location)



bot.run(TOKEN)
