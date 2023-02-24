import os
from typing import Tuple
import mysql
import mysql.connector
from mysql.connector import Error
import pandas as pd
from dotenv import load_dotenv

ALLOW_DATABASE_CONSTRUCTION = False

load_dotenv()
HOST = os.getenv('SQL_HOST')
USER = os.getenv('SQL_USER')
PASSWD = os.getenv('SQL_PASSWD')
DB = os.getenv('SQL_DB')

# TODO Use python enums to represent the different editable columns 

# Enum holder for valid columns in the SQL database
class SQLColumn:
    NAME = 'card_name'
    PRICE = 'card_price'
    COLOUR = 'card_colour'
    SHOP_QUANTITY = 'card_shop_quantity'
    EXISTS_IN_SHOP = 'card_exists_in_shop'
    IS_RESERVED = 'card_is_reserved'
    RESERVED_TO_USER = 'card_reserved_to_user'

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            passwd=user_password,
            database=db_name
        )
        print('MySQL Database connection successful.')
    except Error as err:
        print(f'Error: {err}')
        
    return connection

connection = create_db_connection(HOST, USER, PASSWD, DB)


def create_database(connection, query):
    if(ALLOW_DATABASE_CONSTRUCTION):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            print('Database created successfully.')
        except Error as err:
            print(f'Error: {err}')

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query, None)
        connection.commit()
    except Error as err:
        print(f'Error: {err}')
    
def card_update_column_withid(col, id : int, newval):
    updatequery = """
    UPDATE cards
    SET {0} = %s
    WHERE card_id = %s;
    """.format(col)
    try:
        cursor = connection.cursor()
        cursor.execute(updatequery, (newval, id))
        connection.commit()
    except Error as err:
        print(f'Error: {err}')

def card_update_column_withname(col, name, newval):
    updatequery = """
    UPDATE cards
    SET {0} = %s
    WHERE card_name = %s;
    """.format(col)
    try:
        print(name)
        cursor = connection.cursor()
        cursor.execute(updatequery, (newval, name))
        connection.commit()
    except Error as err:
        print(f'Error: {err}')

def increment_cardsDB(cardlist: list):
    for card in cardlist:    
        updatequery = """
        UPDATE cards
        SET card_shop_quantity = card_shop_quantity + 1  
        WHERE card_name = %s;
        """
        
        try:
            cursor = connection.cursor()
            cursor.execute(updatequery, (card,))
            connection.commit()
        except Error as err:
            print(f'Error: {err}')
            
def increment_card(card_id):   
    cursor = connection.cursor()
    
    updatequery = """
    UPDATE cards
    SET card_shop_quantity = card_shop_quantity + 1  
    WHERE card_id = {id};
    """.format(id=card_id)
    
    try:
        cursor.execute(updatequery)
        connection.commit()
    except Error as err:
        print(f'Error: {err}')

def decrement_card(card_id):   
    cursor = connection.cursor()
    
    updatequery = """
    UPDATE cards
    SET card_shop_quantity = card_shop_quantity - 1  
    WHERE card_id = {id};
    """.format(id=card_id)
    
    try:
        cursor.execute(updatequery)
        connection.commit()
    except Error as err:
        print(f'Error: {err}')

def card_addlistDB(cardlist):
    cursor = connection.cursor()
    
    for entry in cardlist:       
        addquery = """
            INSERT INTO cards
            VALUES(DEFAULT, %s, 0, %s, %s, 0, 0, 0, NULL, %s, %s, NULL, %s, %s, %s);
        """
        ## Values: Name, Colour, Image Filename, Official MTG ID, MTG Set, Is Artifact, Rarity, Is Planeswalker
        
        try:
            # entry in cardlist is a tuple containing the valid information
            cursor.execute(addquery, entry)
            connection.commit()
        except Error as err:
            print(f'Error: {err}')

    return

def card_addDB(card):
    cursor = connection.cursor()
    
    addquery = """
        INSERT INTO cards
        VALUES(DEFAULT, %s, %s, %s, %s, 0, 0, 0, NULL, %s, %s, NULL, %s, %s, %s);
    """
    ## VALUES: Name, Price, Colour, Image Filename, Official MTG ID, MTG Set, Is Artifact, Rarity, Is Planeswalker
    
    try:
        # card is a tuple containing the valid information
        cursor.execute(addquery, card)
        connection.commit()
        print('Added ' + card[0] + ' to DB.')
    except Error as err:
        print(f'Error for card {card[0]}: {err}')

def card_get_shop_quantities():
    cursor = connection.cursor(dictionary=True, buffered = True)
    cursor.execute("SELECT card_name, card_shop_quantity FROM cards")
    
    i = 0
    
    for row in cursor:
        if(row['card_shop_quantity'] > 0):
            print("{Name} : {Quant}".format(Name=row['card_name'], Quant=row['card_shop_quantity']))
            i += row['card_shop_quantity']
    
    print(i)
    
def delete_duplicates():
    cursor = connection.cursor(dictionary=True, buffered = True)
    cursor.execute("SELECT card_name, card_id FROM cards")
    
    delcursor = connection.cursor(dictionary=True, buffered = True)
    
    for row in cursor:
        for anotherrow in cursor:
            if(row['card_name'] == anotherrow['card_name']):
                delcursor.execute("DELETE FROM cards WHERE card_name = {cardname} AND card_id <> {cardid}".format(cardname = row['card_name'], cardid = row['card_name']))
                print('Deleted extra ' + {row['card_name']})

def card_exists_in_DB(name: str):
    cursor = connection.cursor(dictionary=True, buffered = True)
    cursor.execute("SELECT card_name FROM cards")
    
    if(cursor == None): return False
    
    for row in cursor:
        if(row['card_name'] == name):
            return True
    
    return False

def card_get_name_with_id(id) -> str:
    cursor = connection.cursor(dictionary=True, buffered = True)
    cursor.execute("SELECT card_name FROM cards WHERE card_id = {fid}".format(fid=id))
    
    for row in cursor:
        return row['card_name']

def card_get_id_with_name(name):
    cursor = connection.cursor(dictionary=True, buffered = True)
    cursor.execute("SELECT card_id FROM cards WHERE card_name = %s", (name,))
    
    for row in cursor:
        return row['card_id']

def card_refresh_shop():
    cursor = connection.cursor()

    shopquantquery = """
        UPDATE cards
        SET card_shop_quantity = 0;
    """
    
    try:
        # entry in cardlist is a tuple containing the valid information
        cursor.execute(shopquantquery)
        connection.commit()
    except Error as err:
        print(f'Error: {err}')
        
def card_get_filename_with_id(card_id):
    cursor = connection.cursor(dictionary=True, buffered = True)
    cursor.execute("SELECT card_image_filename FROM cards WHERE card_id = {id}".format(id=card_id))
    
    alldicts = cursor.fetchall()
    cardimagedict = next(iter(alldicts))
    
    return cardimagedict['card_image_filename']


def card_get_new_shop_items() -> list:
    cursor = connection.cursor(dictionary=True, buffered = True)
    cursor.execute("SELECT card_id FROM cards WHERE card_shop_quantity > 0 AND discord_message_id IS NULL")
    
    cardiddict = cursor.fetchall()
    cardidlist = []
    
    for iddict in cardiddict:
        cardidlist.append(iddict['card_id'])
    
    return cardidlist

def card_get_update_shop_items() -> list:
    cursor = connection.cursor(dictionary=True, buffered = True)
    cursor.execute("SELECT card_id FROM cards WHERE card_shop_quantity > 0 AND discord_message_id IS NOT NULL")
    
    cardiddict = cursor.fetchall()
    cardidlist = []
    
    for iddict in cardiddict:
        cardidlist.append(iddict['card_id'])
    
    return cardidlist
        
def card_get_shop_info_from_id(card_id):
    cursor = connection.cursor(dictionary=True, buffered = True)
    
    query = """
        SELECT 
        card_name, 
        card_price, 
        card_colour, 
        card_image_filename, 
        card_shop_quantity, 
        card_exists_in_shop,
        card_is_artifact,
        card_rarity,
        card_is_planeswalker,
        discord_message_id
        FROM cards 
        WHERE card_id = {id};
    """.format(id=card_id)
    
    cursor.execute(query)
    
    returndict = cursor.fetchone()
    
    return returndict

def card_get_related_channel_data_from_id(card_id):
    cursor = connection.cursor(dictionary=True, buffered = True)
    
    query = """
        SELECT 
        card_colour, 
        card_is_artifact,
        card_rarity,
        card_is_planeswalker
        FROM cards 
        WHERE card_id = {id};
    """.format(id = card_id)
    
    cursor.execute(query)
    
    return next(iter(cursor))

def card_get_price_with_id(card_id):
    cursor = connection.cursor(dictionary=True, buffered = True)
    
    query = """
        SELECT card_price
        FROM cards 
        WHERE card_id = {id};
    """.format(id = card_id)
    
    cursor.execute(query)
    
    return next(iter(cursor))['card_price']

def card_get_colour_with_id(card_id):
    cursor = connection.cursor(dictionary=True, buffered = True)
    
    query = """
        SELECT card_colour
        FROM cards 
        WHERE card_id = {id};
    """.format(id = card_id)
    
    cursor.execute(query)
    
    return next(iter(cursor))['card_colour']

def card_update_message_id_with_id(card_id, messageid: str):
    cursor = connection.cursor(dictionary=True, buffered = True)

    currmessageid = card_get_message_id_with_id(card_id)
        
    # If message id in DB is empty
    if(currmessageid == None):
        appendedmessageid = messageid
    else:
        appendedmessageid = currmessageid + ' ' + messageid 
    
    updatediscordmessage = """
        UPDATE cards
        SET discord_message_id = '{newmessageid}'
        WHERE card_id = {dbcard_id};
    """.format(newmessageid = appendedmessageid, dbcard_id = card_id)
    
    try:
        # entry in cardlist is a tuple containing the valid information
        cursor.execute(updatediscordmessage)
        connection.commit()
    except Error as err:
        print(f'Error: {err}')
        
def card_get_message_id_with_id(card_id):
    cursor = connection.cursor(dictionary=True, buffered = True)
    
    query = """
        SELECT discord_message_id
        FROM cards 
        WHERE card_id = {id};
    """.format(id = card_id)
    
    cursor.execute(query)
    
    return next(iter(cursor))['discord_message_id']

def card_get_message_id_with_name(card_name):
    cursor = connection.cursor(dictionary=True, buffered=True)
    
    query = """
        SELECT discord_message_id
        FROM cards
        WHERE card_name = %s;
    """
    
    cursor.execute(query, (card_name,))
    
    return next(iter(cursor))['discord_message_id']

def card_del_message_id_with_id(card_id):
    cursor = connection.cursor(dictionary=True, buffered = True)
    
    query = """
        UPDATE cards
        SET discord_message_id = NULL 
        WHERE card_id = {id};
    """.format(id = card_id)
    
    try:
        cursor.execute(query)
        connection.commit()
    except Error as err:
        print(f'Error: {err}')
        
def card_get_shop_quantity_from_id(card_id) -> int:
    cursor = connection.cursor(dictionary=True, buffered = True)
    
    query = """
        SELECT card_shop_quantity
        FROM cards 
        WHERE card_id = {id};
    """.format(id = card_id)
    
    cursor.execute(query)
    
    returnitem = cursor.fetchone()
    
    return returnitem['card_shop_quantity']

def card_get_empty_shop_card_ids() -> tuple:
    cursor = connection.cursor(dictionary=True, buffered = True)
    
    query = """
        SELECT card_id
        FROM cards 
        WHERE card_shop_quantity = 0 AND discord_message_id IS NOT NULL;
    """
    
    cursor.execute(query)

    returndict = cursor.fetchall()
    
    return returndict

def card_get_modify_shop_card_ids():
    cursor = connection.cursor(dictionary=True, buffered = True)
    
    query = """
        SELECT card_id
        FROM cards 
        WHERE card_shop_quantity > 0 AND discord_message_id IS NOT NULL;
    """
    
    cursor.execute(query)

    returndict = cursor.fetchall()
    print(returndict)
    
    return returndict

## def get card data, def 