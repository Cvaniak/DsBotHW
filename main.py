import discord
import os
from dotenv import load_dotenv
import ast
import operator as op
import requests
import json
from tinydb import TinyDB, Query
import atexit
load_dotenv()

# Delete files with rude words when program is off
@atexit.register
def goodbye():
    os.remove("profanity.txt")
    os.remove("wulgaryzmy.json")
    
# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

def eval_expr(expr):
    """
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    return eval_(ast.parse(expr, mode='eval').body)

def eval_(node):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")
    
    if message.content.startswith("$math "):
        try:
            result = eval_expr(message.content[6:])
            await message.channel.send(result)
        except:
            await message.channel.send("No ziomek, to nie jest wyrażenie matematyczne...")
    
    # Bad words test
    word_list = message.content.split(" ")
    if any(word in full_list for word in word_list):
        db_query = db.search(DSUser.name == message.author.name)
        if db_query:
            count_t = int(db_query[0]["count"])+1
            db.update({"count": count_t}, DSUser.name == message.author.name)
            await message.channel.send(F"Oj, oj już wisisz nam {message.author.name} całe {count_t}$!")
        else:
            db.insert({"name": message.author.name, "count": 1})
            await message.channel.send(F"No wiesz {message.author.name}, za takie słowa naliczam Ci dolca!")

    #For simple math only to not test everything
    if len(message.content) < 16:
        try:
            result = eval_expr(message.content)
            await message.channel.send(result)
        except:
            pass

if not os.path.isfile('wulgaryzmy.json'):
    r = requests.get("https://raw.githubusercontent.com/coldner/wulgaryzmy/master/wulgaryzmy.json")
    open('wulgaryzmy.json', "wb").write(r.content)
with open('wulgaryzmy.json') as wul_file:
    wul_list = json.load(wul_file)

if not os.path.isfile('profanity.txt'):
    r = requests.get("https://raw.githubusercontent.com/RobertJGabriel/Google-profanity-words/master/list.txt")
    open('profanity.txt', "wb").write(r.content)
with open("profanity.txt") as prof_file:
    prof_list = prof_file.read().splitlines()

full_list = prof_list + wul_list

db = TinyDB('db.json')
DSUser = Query()

client.run(os.getenv('TOKEN'))