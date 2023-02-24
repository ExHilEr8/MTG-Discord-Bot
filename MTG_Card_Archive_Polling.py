from email.policy import default
import os, requests, json
from numpy import true_divide
import SQL_Interaction
import time
from mysql.connector import Error

from requests import get

sets = ['isd', 'm11', 'm12', 'nph', 'som', 'mbs', 'dka', 'avr']


defaultprice = {
    "common" : 1,
    "uncommon" : 2,
    "rare" : 3,
    "mythic" : 5,
    "is_Planeswalker": 8
}

def newSet(setstr):
    req = requests.get('https://api.scryfall.com/sets/' + setstr)
    data = req.json()
    urireq = requests.get(str(data['search_uri'])).json()

    with open(f'MTG Discord Bot\\MTG SET JSONs\\{setstr}.json', 'w+') as f:
        json.dump(urireq, f, indent = 4)

def addCard(name: str):
    try:
        if(name == ''): return
        if(SQL_Interaction.card_exists_in_DB(name)): return
        
        nameformatforlink = name.replace(' ', '+')
        cardobj = requests.get('https://api.scryfall.com/cards/named?exact=' + nameformatforlink).json()
        
        if(cardobj['set_type'] == 'token'): return
        
        colour = ''
        for colourident in cardobj['color_identity']:
            colour += colourident
            
        filename = name + '.jpg'             
        if '/' in filename:
            filename = filename.replace('/', '')
        
        officialid = cardobj['id']
        cardset = cardobj['set']
        
        imgpath = 'MTG Discord Bot\\cardfaces\\' + filename
        
        if 'image_uris' in cardobj:
            img_data = requests.get(cardobj['image_uris']['normal']).content

        else:
            img_data = requests.get(cardobj['card_faces'][0]['image_uris']['normal']).content
        
        with open(imgpath, 'wb') as handler:
            handler.write(img_data)
        
        isArtifact = False
            
        if 'Artifact' in cardobj['type_line']:
            isArtifact = True
            
        rarity = cardobj['rarity']
        
        isPlaneswalker = False
        
        if 'Planeswalker' in cardobj['type_line']:
            isPlaneswalker = True
        
        if (isPlaneswalker == True):
            price = defaultprice["is_Planeswalker"]
        else:
            price = defaultprice[rarity]
            
        cardtuple = (name, price, colour, filename, officialid, cardset, isArtifact, rarity, isPlaneswalker)   
            
        SQL_Interaction.card_addDB(cardtuple)
        
        time.sleep(0.5)
        
    except Error as err:
        print('Card name ' + name + ' \n' + err)
    

def addSet():
    cardlistfordb = []

    for mtgset in sets:
        req = requests.get('https://api.scryfall.com/sets/' + mtgset)
        data = req.json()
        urireq = requests.get(str(data['search_uri'])).json()

        with open(f'MTG Discord Bot\\MTG SET JSONs\\{mtgset}.json', 'w+') as f:
            json.dump(urireq, f, indent = 4)

        data = urireq['data']

        for cardobj in data:
            name = cardobj['name']
            
            colour = ''
            for colourident in cardobj['color_identity']:
                colour += colourident
                
            filename = name + '.jpg'             
            if '/' in filename:
                filename = filename.replace('/', '')
            
            officialid = cardobj['id']
            cardset = cardobj['set']
            
            imgpath = 'MTG Discord Bot\\cardfaces\\' + filename
            
            if 'image_uris' in cardobj:
                img_data = requests.get(cardobj['image_uris']['normal']).content

            else:
                img_data = requests.get(cardobj['card_faces'][0]['image_uris']['normal']).content
                                
            with open(imgpath, 'wb') as handler:
                handler.write(img_data)
            
            cardlistfordb.append((name, colour, filename, officialid, cardset))
            time.sleep(0.1)
            print(f'Requested card image {name} successful:')
        
        
    SQL_Interaction.card_addlistDB(cardlistfordb)
    
    
def trashupdatelmao(sqlcolumnname : str, jsonobjectparam):
    for mtgset in sets:
        with open(f'MTG Discord Bot\\MTG Set JSONs\\{mtgset}.json', 'r') as f:
                data = json.load(f)['data']
                
                for cardobj in data:             
                    SQL_Interaction.card_update_column_withname(sqlcolumnname, cardobj['name'], cardobj[jsonobjectparam])