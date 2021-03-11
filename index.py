import discord
import os
import requests
import hashlib
import random
import json
import time

client = discord.Client()
def get_word(msg):
  s = ""
  for i in msg:
    if i==" ":
      s = ""
    else:
      s = s + i;
  print(s)
  url = "https://codeforces.com/api/user.info?handles="+str(s)
  r = requests.get(url)
  j = json.loads(r.text)
  dic = j['status']
  if dic == "FAILED":
    return "No User Like : " + str(s)
  print(dic)
  # return  1 if 'firstName' in j['result'][0] else 0
  f_name = j['result'][0]['firstName'] if 'firstName' in j['result'][0] else "NO FIRST NAME"
  l_name = j['result'][0]['lastName'] if 'lastName' in j['result'][0] else "NO LAST NAME"
  rating = j['result'][0]['rating'] if 'rating' in j['result'][0] else "NO RATING"
  maxRating = j['result'][0]['maxRating'] if 'maxRating' in j['result'][0] else "NO MAX RATING"
  ans = "first Name : "+ str(f_name) +"\n" + "last Name : " + str(l_name) + "\n" + "Rating : " + str(rating) + "\n" + "maxRating : " + str(maxRating) +"\n";
  return ans


@client.event
async def on_ready():
  print("Hello : {0.user}".format(client))

@client.event
async def on_message(msg):
  if msg.author == client.user:
    return 
  if msg.content.startswith('!rank'):
    await msg.channel.send(get_word(msg.content))

client.run('ODE2MTcyNTQwODI0OTExODgy.YD3F6Q.FTNB--0Zej4hBPR57BQBki18Jqo')
