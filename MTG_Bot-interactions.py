from inspect import trace
import traceback
import os
import json
import time
import interactions
from quart import Quart
from quart import request
import SQL_Interaction
import MTG_Card_Archive_Polling
import asyncio
from interactions.ext.get import get
import io
from interactions.client.models.component import _build_components

from dotenv import load_dotenv
from discord.ext import commands

cart = {}

shopPurge = False

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = int(os.getenv('DISCORD_SERVER'))

cardfacespath = 'D:\\Python Projects\\MTG Discord Bot\\cardfaces\\'
currenthost = None

bot = interactions.Client(token=TOKEN)
bot.load('interactions.ext.files')

@bot.event(name="on_interaction_create")
async def button_response(ctx):
    
    if not isinstance(ctx, interactions.CommandContext):
        responseid = ctx.custom_id.split(':')
        card_id = responseid[1]
        
        if(responseid[0] == 'add'):
            if(addToCartSafe(card_id, ctx.user.id, 1)):
                await updateCardMessageComponents(card_id)
                await ctx.send(content= 'Added ' + ctx.message.content + ' to cart.', ephemeral=True)
            else:
                await ctx.send(content= ctx.message.content + ' has no cards left in the shop.', ephemeral=True)
            
        elif(responseid[0] == 'rem'):
            if(removeFromCartSafe(card_id, ctx.user.id, 1)):
                await updateCardMessageComponents(card_id)
                await ctx.send(content= 'Removed ' + ctx.message.content + ' from cart.', ephemeral=True)
            else:
                await ctx.send(content= ctx.message.content + ' is not in your cart!', ephemeral=True)
            
        else: return
    
async def updateCardMessageComponents(cardid):
    messageidlist = getMessageIdListFromStr(SQL_Interaction.card_get_message_id_with_id(cardid))
    channelidlist = getCorrespondingChannels(cardid)
    
    for channelid in channelidlist:
        for messageid in messageidlist:
            try:
                message = await getMessage(channelid, messageid)
                databaseQuant = SQL_Interaction.card_get_shop_quantity_from_id(cardid)
                
                shopButtonLabel = message.components[0]['components'][0]['label'].split(': ')
                shopQuant = int(shopButtonLabel[1])
                
                if(databaseQuant != shopQuant):                  
                    components = _build_components(getCardButtonRow(cardid, databaseQuant))
                    await bot._http.edit_message(channel_id=channelid, message_id=messageid, payload={"components": components})
            except:
                pass

@bot.event
async def on_ready():  
    server = await get(bot, interactions.Guild, guild_id=955179339308232764)
    print(f'Bot has connected to {server.name} ({server.id}).')

@bot.command(
    name='account',
    description='Shows how much money you have',
    scope = SERVER,
)
async def command_bank(ctx: interactions.CommandContext):
    accountvalue = checkAccount(ctx.author.id)
    
    if(accountvalue == False):
        await ctx.send('Account doesnt exist. Ping Ex to get one :)', ephemeral = False)
    else:
        await ctx.send('Account: $' + accountvalue, ephemeral = False)    
    
@bot.command(
    name='status',
    description='Shows the bot status',
    scope = SERVER,
)
async def command_status(ctx: interactions.CommandContext):
    await ctx.send('Live!', ephemeral = False)
    
@bot.command(
    name='cartinfo',
    description='(Ephemeral) Shows you whats in your cart, the price of all items, and if you\'re able to afford them',
    scope = SERVER,
)
async def command_cartinfo(ctx: interactions.CommandContext):
    if ctx.author.id in cart:
        await ctx.send('Cards:' + 'Price:' + 'Can Afford: ', ephemeral = True)
    else:
        await ctx.send('Cart is empty.', ephemeral = True)

@bot.command(
    name='resetshop',
    description='Resets the current shop: empties all channels and DB',
    scope = SERVER,
)
async def command_resetshop(ctx: interactions.CommandContext):
    if ctx.author.id == 123536697769197569:
        await resetShop()
        await ctx.send('Shop reset.', ephemeral = True)
    else:
        await ctx.send('Access denied, bitch.')
        
@bot.command(
    name='varyaccount',
    description='Varies your account by the given number, can be a positive or negative amount',
    scope = SERVER,
    options = [
        interactions.Option(
            name='amount',
            description='Amount to vary by',
            type=interactions.OptionType.NUMBER, 
            required=True
        ),
        interactions.Option(
            name='user',
            description='User account to vary',
            type=interactions.OptionType.USER,
            required=False
        ),
    ],
)
async def command_varyaccount(ctx: interactions.CommandContext, amount: int, user: interactions.User):
    
    target = ctx.author
    
    if isinstance(user, interactions.User):
        target = user
    
    varyAccount(amount, target.id)
    
    if(amount >= 0):
        addorsub = 'Added'
    else:
        addorsub = 'Subtracted'
    
    if(checkAccount(target.id) == False):
        await ctx.send('User account does not exist.')
    else:
        await ctx.send(addorsub + ' $' + abs(amount) + ' from' + target.mention)
    
async def shopAddNewFromDB():
    newidlist = SQL_Interaction.card_get_new_shop_items()
    
    for id in newidlist:
        realid = getUUIDString(id)
        for channel in getCorrespondingChannels(realid):
            await sendShopMessage(realid, channel)

def newCart(discord_user_id):
    if discord_user_id not in cart:
        cart[str(discord_user_id)] = []
        
def resetCartsUnsafe():
    global cart
    cart = {}
    
def getCartTotal(discord_id):
    totalprice = 0
    
    for cardid in cart[discord_id]:
        totalprice += SQL_Interaction.card_get_price_with_id(cardid)
    
    return totalprice

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
    try:
        if discord_user_id in cart:
            cardcount = cart[discord_user_id].count(card_id)
        else: return False
    except:
        traceback.print_exc()
        return False
    
    if(cardcount == 0):
        return False
    
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
        backupBank = bank
        
    with open('MTG Discord Bot\\bank.json', 'w+') as f:
        try:
            if(bank[str(account)] + mod < 0):
                return False
            else:
                bank[str(account)] += mod
            
            json.dump(bank, f, indent=4)
        except:
            traceback.print_exc()
            with open('MTG Discord Bot\\bank.json', 'w') as backupf:
                json.dump(backupBank, backupf, indent = 4)
        
    return True

def checkAccount(discord_id):
    with open('MTG Discord Bot\\bank.json', 'r') as f:
        bank = json.load(f)
        backupBank = bank
        
        try:
            if discord_id in bank:
                return str(bank[discord_id])
            else:
                return False
        except:
            traceback.print_exc()
            with open('MTG Discord Bot\\bank.json', 'w') as backupf:
                json.dump(backupBank, backupf, indent = 4)
    
async def shopSyncWithDB():
    return

async def getMessage(cid, mid):
    message = await get(bot, interactions.Message, message_id=mid, channel_id=cid)
    return message

async def getChannel(cid):
    channel = await get(bot, interactions.Channel, channel_id=cid)
    return channel

async def getUniqueEmptiesFromCart(discord_id):
    uniquecards = []
    unique = True
    
    uniqueCart = cart[discord_id]
    parseCart = []
    
    # TODO Optimize by sorting the uniqueCart first, and then only check for uniqueness for each unique item in that list
    
    for nextCart in cart:
        if not uniqueCart == nextCart:
            parseCart.extend(nextCart)
    
    for currentCard in uniqueCart: 
        for compareCard in parseCart:
            if(currentCard == compareCard):
                unique = False
                break
        
        if(unique == True):
            uniquecards.append(id)

async def shopRemoveEmptiesFromCart():
    return

async def shopRemoveEmpties():
    idlist = SQL_Interaction.card_get_empty_shop_card_ids()
    
    for id in idlist:
        realid = getUUIDString(id['card_id'])
        
        reserved = False
        
        for cartlist in cart.values():
            if realid in cartlist:
                reserved = True
                break
                
            if reserved: break
        
        if not reserved:

            iddata = SQL_Interaction.card_get_shop_info_from_id(realid)
            
            channellist = getCorrespondingChannels(realid)
            messagelist = getMessageIdListFromStr(iddata['discord_message_id'])
            
            for channelid in channellist:
                for messageid in messagelist:
                    try:
                        message = await get(bot, interactions.Message, message_id=messageid, channel_id=channelid)
                        await message.delete()
                    except:
                        pass
                    
            SQL_Interaction.card_del_message_id_with_id(realid)

def getUUIDString(uuid):
    return '0x'+ (uuid.hex()).upper()
    

async def sendShopMessage(card_id, channel_id):
    try:
        name = SQL_Interaction.card_get_name_with_id(card_id)
        messagecontent = name + ' $' + str(SQL_Interaction.card_get_price_with_id(card_id))
        filename = SQL_Interaction.card_get_filename_with_id(card_id)
            
        imgpath = cardfacespath + filename
        
        img = open(imgpath, 'rb')
        _img = io.BytesIO(img.read())
        
        buttonrow = getCardButtonRow(card_id, SQL_Interaction.card_get_shop_quantity_from_id(card_id))
            
        channel = await getChannel(channel_id)
        message = await channel.send(messagecontent, components = buttonrow, files = [interactions.File(filename='image.jpg', fp=_img)])
        
        SQL_Interaction.card_update_message_id_with_id(card_id, str(message.id))
    except:
        try:
            print(card_id)
        except:
            print('Card id could not be printed.')
        traceback.print_exc()
        pass

def getCardButtonRow(card_id, quant):
    button1 = interactions.Button(
    style = interactions.ButtonStyle.PRIMARY,
    label = 'Add to Cart: ' + str(quant),
    custom_id='add:' + card_id
    )
    
    button2 = interactions.Button(
        style = interactions.ButtonStyle.DANGER,
        label = 'Remove from Cart',
        custom_id='rem:' + card_id
    )
    
    buttonrow = interactions.ActionRow(
        components=[button1, button2]
    )
    
    return buttonrow

def createBank():
    bankdict = {}
    bankdict[121026144089800706] = 100
    bankdict[123768566016245760] = 100
    bankdict[123536697769197569] = 100
    bankdict[189945110908108800] = 100
    
    with open('MTG Discord Bot\\bank.json', 'w') as f:
        json.dump(bankdict, f, indent = 4)


async def delShopMessage(card_id, msgid, channelid):
    message = await get(bot, interactions.Message, message_id=msgid, channel_id=channelid)
    await message.delete()
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

def resetShop():
    SQL_Interaction.card_refresh_shop()
    resetCartsUnsafe()

def cartIDsToNames(discord_id):
    namelist = []
    
    for cardid in cart[str(discord_id)]:
        namelist.append(SQL_Interaction.card_get_name_with_id(cardid))
    
    return namelist

async def addcardsDB(cardlist):
    for card in cardlist:
        if not (SQL_Interaction.card_exists_in_DB(card)):
            MTG_Card_Archive_Polling.addCard(card)
    
    SQL_Interaction.increment_cardsDB(cardlist)
    SQL_Interaction.card_get_shop_quantities()
    
    messagetoupdatelist = SQL_Interaction.card_get_update_shop_items()
    
    # for messageid in messagetoupdatelist:
    #     await updateCardMessageComponents(getUUIDString(messageid))
                
    print(cardlist)
    await shopAddNewFromDB()
    
    global shopPurge
    
    if(shopPurge == True):
        shopPurge = False
        await shopRemoveEmpties()

app = Quart(__name__)

@app.route('/addcards', methods = ['POST'])
async def addcardsTTS():
    req = await request.form
    
    cardlist = list(req.values())
    
    await addcardsDB(cardlist)
    
    return 'Cards added successfully.'

@app.route('/resetDB', methods = ['GET'])
async def resetDBTTS():
    global shopPurge
    shopPurge = True
    resetShop()
    return 'Shop quantities reset: syncing on table load'

@app.route('/getcart', methods = ['POST'])
async def getcartTTS():
    form = list(await request.form)
    discord_id = form[0]
    
    if discord_id in cart:
        price = getCartTotal(discord_id)
        accountTotal = int(checkAccount(discord_id))
        
        if(accountTotal >= price):
            varyAccount(-abs(price), discord_id)
            try:      
                return json.dumps(cartIDsToNames(discord_id))
            finally:
                del cart[discord_id]
        else:
            return (f'User ({discord_id}) cannot afford the cost of the cart: ${price}, missing $' + 
                        abs(accountTotal - price)), 400
    else: 
        return f'Cart does not exist. Discord user ID: {discord_id}', 400  

@app.route('/syncWithDB', methods = ['POST'])
async def syncWithDBTTS():  
    data = await request.form
    cardlist = list(data.values())
    
    await addcardsDB(cardlist)
    return "Success"

loop = asyncio.get_event_loop()

task2 = loop.create_task(app.run_task())
task1 = loop.create_task(bot.start())

gathered = asyncio.gather(task1, task2, loop=loop)
loop.run_until_complete(gathered)