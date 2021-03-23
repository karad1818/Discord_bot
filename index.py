import discord
import random
import requests
import hashlib
import json
import html
import cv2 as cv
import numpy as np
from PIL import Image as im
import urllib.request
from discord.ext import commands
import os
from keep_alive import keep_alive

# Global Stuff that do everything 1 Time

word_list = []
d = requests.get("https://www.mit.edu/~ecprice/wordlist.10000")
word_str = d.content.decode('utf-8')
word_list = word_str.split("\n")

started = 0
user_score = dict()
remained_hint = 0

ok = 0
collage = 0
stegno = 0

with urllib.request.urlopen("https://opentdb.com/api.php?amount=50&type=multiple") as url:
    data = json.loads(url.read().decode())
user = {}
ArrChoice = []
act_user = "NONE"
rnd = 0
cnt = 0
quiz_checker = 0
# Dictionary Started

class Dictionary:

  def __init__(self, msg):
    self.msg = msg

  def do_request(self):
    url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/" + self.msg
    j = requests.get(url).json()
    return j

  def get_def(self):
    j = self.do_request()
    ans = []
    if isinstance(j,dict):
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

  def get_syn(self):
    j = self.do_request()
    ans = []
    if isinstance(j,dict):
      return j['message']
    else:
      j = j[0]
      m = j['meanings'][0]['definitions']
      for i in m:
        if 'synonyms' in i:
          for j in i['synonyms']:
            ans.append(j)

    if len(ans) <= 0:
      return "No synonyms found...."

    ans_str = ""
    cnt = 1;
    for i in ans:
      ans_str = ans_str + i + "  |  "
      cnt = cnt + 1
      if cnt>25:
        break;
    return ans_str

  def get_pro(self):
    j = self.do_request()
    ans = []
    if isinstance(j,dict):
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

# Dictionary Ended

# Hang Man Started

class hangman:
  word = ""
  def get_word_definition(self,msg : str):
    d = Dictionary(msg)
    ans = d.get_def()
    if ans == "Sorry pal, we couldn't find definitions for the word you were looking for.":
      return ""
    else:
      ok = 0
      temp = ""
      for i in ans:
        if i == '\n' and ok == 0:
          ok = 1
          self.word = temp
          temp = ""
        else:
          temp += i
      Word = ""
      for i in self.word:
        if i==":" or  i==" ":
          Word = ""
        else:
          Word += i
      self.word = Word
      return temp

  def start_game(self):
    r = random.randint(0,9995)
    defi = ""
    while True:
      word = word_list[r]
      if len(word) < 2:
        continue
      msg = str(word)
      defi = self.get_word_definition(msg)
      if defi != "":
        break
    return defi
  
  def check(self,msg):
    print(self.word)
    if msg.lower() == self.word.lower():
      return "Correct !!!"

  def answer(self):
    return self.word
  
  def hint(self,h):
    p_hint = ""
    hint = []
    if h == 0:
      return "Your hints finished"
    if h == 3:
      hint.append(self.word[0])
      for i in range(1,len(self.word),1):
        hint.append("  *  ")
    elif h == 2:
      hint.append(self.word[0])
      for i in range(1,len(self.word)-1,1):
        hint.append("  *  ")
      hint.append("  " + self.word[-1])
    else :
      for i in range(0,len(self.word),1):
        if i&1 :
          hint.append("  *  ")
        else:
          hint.append("  " + self.word[i])
    for i in hint:
      p_hint += i
    return p_hint

#Hangman ended

# image processing started
class image_processing:

  def url_to_image(self,url):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Referer': 'https://cssspritegenerator.com',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive'}
    req = urllib.request.Request(url,headers=hdr)
    resp = urllib.request.urlopen(req)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv.imdecode(image, cv.IMREAD_UNCHANGED)
    return image

  def save_img(self,img,name):
    img = im.fromarray(img)
    img.save(name)

  def get_and_save_image(self,msg,name):
    #global collage ,stegno
    global ok,collage
    if len(msg.attachments) == 0:
      collage = 0
      # stegno = 0
      ok = 0
      return "Not a Valid File"
    x = msg.attachments[0].url
    y = self.url_to_image(x)
    self.save_img(y,name)
    return ""
  
  def black_and_white(self,img):
    img = cv.cvtColor(img,cv.COLOR_RGB2GRAY)
    return img

  def edge_detection(self,img):
    canny = cv.Canny(cv.cvtColor(img,cv.COLOR_RGB2GRAY),0,255)
    return canny

  def smoothning(self,img,x):
    img = cv.GaussianBlur(img,(x,x),0)
    return img

  def sharpening(self,img):
    new_filter = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    img = cv.filter2D(img,-1,new_filter)
    return img

  def add_filter(self,img,prob):
    output = np.zeros(img.shape,np.uint8)
    thres = 1 - prob 
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            rdn = random.random()
            if rdn < prob:
                output[i][j] = 0
            elif rdn > thres:
                output[i][j] = 255
            else:
                output[i][j] = img[i][j]
    return output

  def sketch(self,img , col):
    sketch_gray, sketch_color = cv.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
    return (sketch_color if col else sketch_gray)

  def stylized(self,img):
    img = cv.stylization(img, sigma_s=60, sigma_r=0.07)
    return img

  def frame(self,img,x):
    img = cv.copyMakeBorder(img,x,x,x,x,cv.BORDER_CONSTANT,value=[255,0,0])
    return img

  def merge_and_create(self,a,b,c,d):
    a = cv.resize(a,(250,250))
    b = cv.resize(b,(250,250))
    c = cv.resize(c,(250,250))
    d = cv.resize(d,(250,250))
    first = np.vstack([a,b])
    second = np.vstack([c,d])
    final = np.hstack([first,second])
    cv.imwrite('x.png',final)
    return cv.imread('x.png')
  
  def encryption(self,a,b):
    a = cv.resize(a,(600,600))
    b = cv.resize(b,(600,600))
    for i in range(b.shape[0]): 
      for j in range(b.shape[1]): 
        for l in range(3): 
          v1 = format(a[i][j][l], '08b') 
          v2 = format(b[i][j][l], '08b') 
          v3 = v1[:4] + v2[:4]  
          a[i][j][l]= int(v3, 2)
    cv.imwrite('x.png',a)
    return cv.imread('x.png')

  def decryption(self,img):
    width = img.shape[0] 
    height = img.shape[1] 
    img1 = np.zeros((width, height, 3), np.uint8) 
    img2 = np.zeros((width, height, 3), np.uint8) 
        
    for i in range(width): 
      for j in range(height): 
        for l in range(3): 
          v1 = format(img[i][j][l], '08b') 
          v2 = v1[:4] + chr(random.randint(0, 1)+48) * 4
          v3 = v1[4:] + chr(random.randint(0, 1)+48) * 4
          img1[i][j][l]= int(v2, 2) 
          img2[i][j][l]= int(v3, 2)
    cv.imwrite('e.png',img1)
    cv.imwrite('d.png',img2)

    return cv.imread('e.png') , cv.imread('d.png')

#image processing ended

# global functions
def Score_calculator(user:str):
  global user_score
  if user in user_score:
    user_score[user] += 1
  else:
    user_score[user] = 1
  score = ""
  for i,j in user_score.items():
    score = score + str(i) + "   :    " + str(j) + "\n"
  return score

client = commands.Bot(command_prefix="!")

# create some global object
h = hangman()
i = image_processing()

@client.command(name='def')
async def get_definitions(ctx,*,args : str):
  msg = "{}".format(''.join(args))
  d = Dictionary(msg)
  await ctx.send(d.get_def())

@client.command(name='syn')
async def get_synonyms(ctx,*,args : str):
  msg = "{}".format(''.join(args))
  d = Dictionary(msg)
  await ctx.send(d.get_syn())

@client.command(name='pro')
async def get_pronunciation(ctx,*,args : str):
  msg = "{}".format(''.join(args))
  d = Dictionary(msg)
  await ctx.send(d.get_pro())

@client.command(name='start')
async def get_word_for_game(ctx):
  global started,remained_hint
  started = 1
  remained_hint = 3
  await ctx.send(h.start_game())

@client.command(name='hint')
async def give_hint(ctx):
  global remained_hint,started
  if started == 0:
    await ctx.send("No game started...")
  else:
    await ctx.send(h.hint(remained_hint))
    if remained_hint > 0:
      remained_hint -= 1

@client.command(name='ans')
async def give_ans(ctx):
  global started
  started = 0
  await ctx.send(h.answer())

@client.command(name='image')
async def image_enable(ctx):
  global ok
  ok = 1
  await ctx.send("Upload Image.....")

@client.command(name='collage')
async def multi_image_enable(ctx):
  global collage
  collage = 4
  await ctx.send("Upload 4 images here ....")

@client.command(name='stegno')
async def stegno_enable(ctx):
  global stegno
  stegno = 1
  await ctx.send("What do you wanna do ?? [e : encryption, d : decryption]")

@client.command(name='quiz')
async def quiz_enable(ctx):
  global quiz_checker , Arrchoice , rnd , cnt
  quiz_checker = 1
  ArrChoice.clear()
  rnd = random.randint(0, 49)
  Question = html.unescape(data['results'][rnd]['question'])
  await ctx.send("Question: " + Question)
  ArrChoice.append(html.unescape(data['results'][rnd]['correct_answer']))
  for i in range (0, 3):
    ArrChoice.append(html.unescape(data['results'][rnd]['incorrect_answers'][i]))
  random.shuffle(ArrChoice)
  option = "A"
  for word in ArrChoice:
    await ctx.send(chr(ord(option) + cnt) + ") " + word)
    cnt += 1
  cnt = 0


@client.event
async def on_message(msg):
  if msg.author.id == client.user.id:
    return 

  global started,ok,collage,stegno,quiz_checker,ArrChoice,user_score

  if started == 1:
    if h.check(msg.content) == "Correct !!!":
      await msg.channel.send("Correct !!!")
      started = 0
      await msg.channel.send(Score_calculator(msg.author.name))

  if ok > 0:
    if ok == 1:
      p = i.get_and_save_image(msg,'x.png')
      if p != "":
        ok = 0
      else:
        feature = "Which filter/feature you wanna apply(Write 1/2/3..) ??\n 1. Black and White\n 2. Filter\n 3. Blur\n 4. Edge detection\n 5. Sharpening\n 6. Gray Sketch\n 7. Colour Sketch\n 8. Stylization\n 9. Frame"
        await msg.channel.send(feature)
        ok = 2
    elif ok == 2:
      img = cv.imread('x.png')
      if msg.content == "1":
        img = i.black_and_white(img)
      elif msg.content == "2":
        img = i.add_filter(img,0.05)
      elif msg.content == "3":
        img = i.smoothning(img,5)
      elif msg.content == "4":
        img = i.edge_detection(img)
      elif msg.content == "5":
        img = i.sharpening(img)
      elif msg.content == "6":
        img = i.sketch(img,0)
      elif msg.content == "7":
        img = i.sketch(img,1)
      elif msg.content == "8":
        img = i.stylized(img)
      elif msg.content == "9":
        img = i.frame(img,50)
      i.save_img(img,'x.png')
      await msg.channel.send(file=discord.File('x.png'))
      ok = 0

  if collage > 0:
    if collage == 4:
      p = i.get_and_save_image(msg,'a.png')
      collage -= 1
    elif collage == 3:
      p = i.get_and_save_image(msg,'b.png')
      collage -= 1
    elif collage == 2:
      p = i.get_and_save_image(msg,'c.png')
      collage -= 1
    elif collage == 1:
      p = i.get_and_save_image(msg,'d.png')
      collage -= 1
    if collage == 0:
      a = cv.imread('a.png')
      b = cv.imread('b.png')
      c = cv.imread('c.png')
      d = cv.imread('d.png')
      img = i.merge_and_create(a,b,c,d)
      i.save_img(img,'x.png')
      await msg.channel.send(file=discord.File('x.png'))

  if stegno > 0:
    if stegno == 1:
      if msg.content == "e":
        stegno = 5
        await msg.channel.send("Upload 2 Images that you wanna encrypt....(It'll take 2/3 minutes so be patient)")
      else:
        stegno = 3
        await msg.channel.send("Upload Image that you wanna decrypt..(It'll take 2/3 minutes so be patient)")
    elif (stegno == 5 or stegno == 4):
      #encryption
      if stegno == 5:
        p1 = i.get_and_save_image(msg,'e.png')
        stegno -= 1
      else:
        p2 = i.get_and_save_image(msg,'d.png')
        img = i.encryption(cv.imread('e.png'),cv.imread('d.png'))
        i.save_img(img,'x.png')
        await msg.channel.send(file=discord.File('x.png'))
        stegno = 0
    elif stegno == 3:
      #decryption
      p = i.get_and_save_image(msg,'d.png')
      a , b = i.decryption(cv.imread('d.png'))
      i.save_img(a,'e.png')
      i.save_img(b,'d.png')
      await msg.channel.send(file=discord.File('e.png'))
      await msg.channel.send(file=discord.File('d.png'))
      stegno = 0
    
  if quiz_checker == 1:
    answer_given = str(msg.content)
    answer_given = answer_given.upper()
    if answer_given == 'A' or answer_given == 'B' or answer_given == 'C' or answer_given == 'D':
      curr_ans = str(html.unescape(data['results'][rnd]['correct_answer']))
      username = str(msg.author).split("#")[0]
      if not username in user_score:
        user_score[username] = 0
      usr_ans = ArrChoice[ord(msg.content.upper()) - 65]
      if curr_ans == usr_ans:
        await msg.channel.send("Correct!")
        user_score[username] += 1
        ArrChoice.clear()
        quiz_checker = 0
      else:
        await msg.channel.send("Incorrect!")
        await msg.channel.send("Correct Answer is " + curr_ans)
        ArrChoice.clear()
        quiz_checker = 0
    
  await client.process_commands(msg)

keep_alive()
client.run(os.getenv('TOKEN'))
