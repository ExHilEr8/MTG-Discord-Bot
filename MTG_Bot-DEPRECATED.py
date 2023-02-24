from xmlrpc.client import Boolean
import discord
import os
import json
import time
import interactions
from matplotlib import testing
from quart import Quart
from quart import request
import SQL_Interaction
import MTG_Card_Archive_Polling
import asyncio

from dotenv import load_dotenv
from discord.ext import commands
from discord_components import DiscordComponents, ComponentsBot, Button, ButtonStyle

cart = {}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = int(os.getenv('DISCORD_SERVER'))

bot = discord.ext.commands.Bot("!", intents = discord.Intents.all())
    
@bot.event
async def on_ready():  
    server = bot.get_guild(SERVER)
    
    print(f'{bot.user} has connected to {server.name} ({server.id}).')
    
    members = '\n - '.join([member.name for member in server.members])
    print(f'Server Members:\n - {members}') 
    
    # await sendShopMessage('0x64781B02F2B511EC947100FF7F2DE5BC', 983109101905145916)
    
    button = Button(style = "1", custom_id="primary", label="Button")
    await bot.get_channel(983109101905145916).send("button message", components = [button])
    interaction = await bot.wait_for("button_click")
    await interaction.respond(content = "Success!")


async def shopAddNewFromDB():
    newidlist = SQL_Interaction.card_get_new_shop_items()
    
    for id in newidlist:
        realid = getUUIDString(id)
        for channel in getCorrespondingChannels(realid):
            await sendShopMessage(realid, channel)

def newCart(discord_user_id):
    if discord_user_id not in cart:
        cart[discord_user_id] = []

# Check for quantity in DB then call addToCart if quantity is sufficient, return False else
def addToCartSafe(card_id, discord_user_id, quant = 1) -> bool:
    if(SQL_Interaction.card_get_shop_quantity_from_id(card_id) >= quant):
        
        addToCart(card_id, discord_user_id, quant)
        return True    
    
    return False
    
# Unsafe addToCart - Doesnt check for quantity in DB
def addToCart(card_id, discord_user_id, quant):
    
    if discord_user_id not in cart:
        newCart(discord_user_id)
    
    for _ in range(quant):
        cart[discord_user_id].append(card_id)
        SQL_Interaction.decrement_card(card_id)

def removeFromCartSafe(card_id, discord_user_id, quant = 1) -> bool:
    cardcount = cart[discord_user_id].count(card_id)
    
    if(quant > cardcount):
        quant = cardcount
    
    removeFromCart(card_id, discord_user_id, quant)
    
    return True

def removeFromCart(card_id, discord_user_id, quant):
    for _ in range(quant):
        cart[discord_user_id].remove(card_id)
        SQL_Interaction.increment_card(card_id)
    
def varyAccount(mod: int, account: int) -> bool:
    with open('MTG Discord Bot\\bank.json', 'r') as f:
        bank = json.load(f)
        
    with open('MTG Discord Bot\\bank.json', 'w+') as f:
        if(bank[str(account)] + mod < 0):
            return False
        else:
            bank[str(account)] += mod
        
        json.dump(bank, f, indent=4)
        
    return True

    
async def shopSyncWithDB():
    return
    

async def shopRemoveEmpties():
    idlist = SQL_Interaction.card_get_empty_shop_card_ids()
    
    for id in idlist:
        realid = getUUIDString(id['card_id'])
        iddata = SQL_Interaction.card_get_shop_info_from_id(realid)
        
        channellist = getCorrespondingChannels(realid)
        messagelist = getMessageIdListFromStr(iddata['discord_message_id'])
        
        for channelid in channellist:
            channel = bot.get_channel(channelid)
            
            for messageid in messagelist:
                try:
                    message = await channel.fetch_message(messageid)
                    await message.delete()
                except:
                    pass
                    
        SQL_Interaction.card_del_message_id_with_id(realid)

def getUUIDString(uuid):
    return '0x'+ (uuid.hex()).upper()
    

async def sendShopMessage(card_id, channel_id):
    name = SQL_Interaction.card_get_name_with_id(card_id)
    messagecontent = name
    filename = SQL_Interaction.card_get_filename_with_id(card_id)

    message = await bot.get_channel(channel_id).send(messagecontent, components = [Button(label='Add to Cart', style='1', custom_id='a' + card_id), Button(label='Remove from Cart', style = '4', custom_id='r' + card_id)], 
                                           file = discord.File('D:\\Python Projects\\MTG Discord Bot\\cardfaces\\' + filename))
    
    SQL_Interaction.card_update_message_id_with_id(card_id, str(message.id))

def createBank():
    bankdict = {}
    bankdict[121026144089800706] = 0
    bankdict[123768566016245760] = 0
    bankdict[123536697769197569] = 0
    bankdict[189945110908108800] = 0
    
    with open('MTG Discord Bot\\bank.json', 'w') as f:
        json.dump(bankdict, f, indent = 4)


async def delShopMessage(card_id, message_id, channel_id):
    msg = await bot.get_channel(channel_id).fetch_message(message_id)
    await msg.delete()
    SQL_Interaction.card_del_message_id_with_id(card_id)

def getCorrespondingChannels(card_id) -> list:
    channeldata = SQL_Interaction.card_get_related_channel_data_from_id(card_id)
    channellist = []
    rarity = channeldata['card_rarity']
    
    with open('MTG Discord Bot\\mtgchannelvalues.json', 'r') as f:
        channeldict = json.load(f)
        
        if(channeldata['card_is_planeswalker'] == 1):
            channellist.append(channeldict['planeswalker']['mythic'])
            return channellist
        
        if(channeldata['card_is_artifact'] == 1):
            channellist.append(channeldict['artifact'][rarity])
            
        if(channeldata['card_colour'] == ''):
            channellist.append(channeldict['colourless'][rarity])
            return channellist
        
        for c in list(channeldata['card_colour']):
            channellist.append(channeldict[c][rarity])
                
    return channellist

def getMessageIdListFromStr(stringlist: str) -> list:
    messagelist = []
    
    stringlist = stringlist.split()
    
    for s in stringlist:
        s = s.replace(' ', '')
        messagelist.append(s)
    
    return messagelist

def getMessageIdStrFromList(messageidlist: list) -> str:
    return ' '.join(messageidlist)

app = Quart(__name__)

@app.route('/addcards', methods = ['POST'])
async def addcards():
    req = await request.form
    
    cardlist = list(req.values())
    
    for card in cardlist:
        if not (SQL_Interaction.card_exists_in_DB(card)):
            MTG_Card_Archive_Polling.addCard(card)
    
    print(cardlist)
    
    SQL_Interaction.increment_cardsDB(cardlist)
    SQL_Interaction.card_get_shop_quantities()
    print(cardlist)     
    await shopAddNewFromDB()
    return 'Response successful'

@app.route('/synccards', methods = ['GET'])
async def synccards():
    SQL_Interaction.card_refresh_shop()
    await shopRemoveEmpties()
    return 'Shop quantities reset: syncing on table load'

bot.loop.create_task(app.run_task())

bot.run(TOKEN)