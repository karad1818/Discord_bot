import discord
import os
import requests
import hashlib
import random
import json
import time
import xml.etree.ElementTree as ET
import re

client = discord.Client() 
started = 0
global_word = "ab"
user_hint = 0
user = dict()
word_list = []
d = requests.get("https://www.mit.edu/~ecprice/wordlist.10000")
word_str = d.content.decode('utf-8')
word_list = word_str.split("\n")

def comman(msg):
  x = ""
  ok = 0
  for i in msg:
    if i==" " and ok == 0:
      x=""
      ok = 1
    else:
      x = x + i

  url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+x
  j = requests.get(url).json()
  # print(type(j))
  return j

def get_def(msg):
  j = comman(msg)
  ans = []
  if 'message' in j:
    return j['message']
  else:
    j = j[0]
    ans.append("Word : " + j['word'])
    m = j['meanings'][0]['definitions']
    for i in m:
      ans.append(i['definition'])
  ans_str = ""
  cnt = 1;
  for i in ans:
    ans_str = ans_str + "--> " + i + "\n"
    cnt = cnt + 1
    if cnt >= 10:
      break 
  return ans_str

def get_syn(msg):
  j = comman(msg)
  ans = []
  if 'message' in j:
    return j['message']
  else:
    j = j[0]
    m = j['meanings'][0]['definitions']
    for i in m:
      for j in i['synonyms']:
        ans.append(j)
  ans_str = ""
  cnt = 1;
  for i in ans:
    ans_str = ans_str + i + "  |  "
    cnt = cnt + 1
    if cnt>25:
      break;
  return ans_str


def get_pro(msg):
  j = comman(msg)
  ans = []
  if 'message' in j:
    return j['message']
  else:
    j = j[0]
    m = j['phonetics'][0]
    ans.append(m['audio'])
    ans.append(m['text'])
  ans_str = ""
  ans_str = ans_str + "Audio : " + ans[0] + "\n"
  ans_str = ans_str + "IPA : " + ans[1]
  return ans_str

def get_word_definition(msg):
  ans = get_def(msg)
  global global_word 
  if ans == "Sorry pal, we couldn't find definitions for the word you were looking for.":
    return ""
  else:
    ok = 0
    temp = ""
    for i in ans:
      if i == '\n' and ok == 0:
        ok = 1
        global_word = temp
        temp = ""
      else:
        temp += i
    Word = ""
    for i in global_word:
      if i==":" or  i==" ":
        Word = ""
      else:
        Word += i
    global_word = Word
    return temp

def start_game():
  r = random.randint(0,9995)
  defi = ""
  while True:
    word = word_list[r]
    if len(word) < 2:
      continue
    msg = str(word)
    defi = get_word_definition(msg)
    if defi != "":
      break
  return defi

def check(msg):
  global global_word
  if msg.lower() == global_word.lower():
    return "Correct !!!"

def get_help():
  ans = ""
  ans = ans + "1. !def  <word> : it'll give the definition of that word\n"
  ans = ans + "2. !syn  <word> : it'll give the synonyms of that word\n"
  ans = ans + "3. !pro  <word> : it'll give the audiofile of pronunciation as well as gives the international phonetic spelling\n"
  ans = ans + "4. !start : to start the game\n"
  ans = ans + "5. !hint : you've 3 hint for every round\n"
  ans = ans + "6. !ans : it'll give the answer to the question\n"
  ans = ans + "7. !skip : to skip 1 round\n"
  return ans

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name=" !help "))
  print("Hello : {0.user}".format(client))

@client.event
async def on_message(msg):
  global started
  global user_hint
  if msg.author == client.user:
    return 
  if msg.content.startswith('!def'):
    await msg.channel.send(get_def(msg.content))
  elif msg.content.startswith('!syn'):
    await msg.channel.send(get_syn(msg.content))
  elif msg.content.startswith('!pro'):
    await msg.channel.send(get_pro(msg.content))
  elif msg.content.startswith('!help'):
    await msg.channel.send(get_help())
  elif msg.content.startswith('!ans'):
    started = 0
    await msg.channel.send(global_word)
  elif msg.content.startswith('!hint'):
    if user_hint == 3:
      await msg.channel.send("Sorry , Your hints finished")
    else :
      user_hint += 1
      p_hint = ""
      if user_hint == 1:
        hint = []
        hint.append(global_word[0])
        for i in range(1,len(global_word),1):
          hint.append("  *  ")
        for i in hint:
          p_hint += i
        await msg.channel.send(p_hint)
      elif user_hint == 2:
        hint = []
        hint.append(global_word[0])
        for i in range(1,len(global_word)-1,1):
          hint.append("  *  ")
        hint.append("  " + global_word[-1])
        for i in hint:
          p_hint += i
        await msg.channel.send(p_hint)
      else :
        hint = []
        for i in range(0,len(global_word),1):
          if i&1 :
            hint.append("  *  ")
          else:
            hint.append("  " + global_word[i])
        for i in hint:
          p_hint += i
        await msg.channel.send(p_hint)  

  elif (msg.content.startswith('!skip') == 0) and (started == 1 or msg.content.startswith('!start')):
    if started == 0:
      started = 1
      user_hint = 0
      await msg.channel.send(start_game())
    else:
      if check(msg.content) == "Correct !!!":
        started = 0
        author = msg.author.name
        if author in user:
          user[author] = user[author] + 1
        else:
          user[author] = 1
        score  = ""
        for i,j in user.items():
          score = score + i + "   :    " + str(j) + "\n"
        user_hint = 0
        await msg.channel.send("Correct !!!")
        await msg.channel.send(score)
  elif msg.content.startswith('!skip'):
    started = 0
    await msg.channel.send("Game Ended")
  
client.run(os.getenv('TOKEN'))
