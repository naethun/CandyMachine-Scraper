import requests, re
from bs4 import BeautifulSoup
import asyncio
import discord
from discord.ext import commands

client = discord.Client()

client = commands.Bot(command_prefix = '!')

@client.event
async def on_ready():
    activity_string = '{} servers'.format(len(client.guilds))
    await client.change_presence(
        activity = discord.Activity(
            type = discord.ActivityType.playing, 
            name = "Scraping CMIDs..."
        )
    )
    print('We have logged in as {0.user}'.format(client))

def pageJavaScript(page_html, url):
    #list all the scripts tagS
    all_script_tags = page_html.find_all("script")

    #filtering Internal and External JavaScript of page_html
    external_js = list(filter(lambda script:script.has_attr("src"), all_script_tags))
    internal_js = list(filter(lambda script: not script.has_attr("src"), all_script_tags))

    jsFiles = []
    #internal JavaScript
    for js_code in internal_js:
        jsFiles.append(js_code.string)

    # External JavaScript
    for  script_tag in external_js:
        suburl = script_tag.get("src")
        r = requests.get(url + suburl)
        src = r.text
        jsFiles.append(src)
    
    return jsFiles
#OTE0OTYwMDg0NjEyODM3Mzc2.YaUo-w._g_6gqMEACveTjW3ZOhKGX4saHY
def searchKey(srcs):
    possibleKeys = set()
    for src in srcs:
        possibleKeys.update(re.findall('REACT_APP_CANDY_MACHINE_ID[\'":]{1,3}([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44})"', src))
        possibleKeys.update(re.findall('candyMachineId[\'":]{1,3}([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44})"', src))
    possibleKeys = list(possibleKeys)
    return possibleKeys

@client.command()
async def scrape(ctx, *, content):
    url = content

    response = requests.get(url)

    page_html = BeautifulSoup(response.text, 'html.parser')

    srcs = pageJavaScript(page_html, url)
    
    keys = searchKey(srcs)

    for key in keys:
        await ctx.send("Found a CMID: " + key)

@scrape.error
async def scrape_error (ctx, error):
    if isinstance(error, commands.BadArgument, commands.MissingRequiredArgument):
        await ctx.send('Not a Candy Machine website.')

client.run('OTcxOTAwMzY2MTgwNDc4OTc2.YnROwA.5JnrsBilcTwC9ELgrt-KuUCHSPY')