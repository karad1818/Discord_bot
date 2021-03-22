import discord
import random
import html
import os
import cv2 as cv
import numpy as np
import matplotlib as mlt
import requests
import hashlib
import json
import urllib.request
from PIL import Image as im
from PIL import ImageOps
from keep_alive import keep_alive

# funtion for dictionary
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
  if 'msg' in j:
    return j['msg']
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
  if 'msg' in j:
    return j['msg']
  else:
    j = j[0]
    m = j['meanings'][0]['definitions']
    for i in m:
      if 'synonyms' in i:
        for j in i['synonyms']:
          ans.append(j)
      else:
        return "No Synonyms found.."
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
  if 'msg' in j:
    return j['msg']
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
  ans = ans + "7. !quiz : to play General Knowledge Quiz\n"
  ans = ans + "8. !leader : to display leaderboard"
  return ans

#fucntions for image
def url_to_image(url):
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

def save_img(img,name):
  img = im.fromarray(img)
  img.save(name)

def get_and_save_image(msg,name):
  if len(msg.attachments) == 0:
    return "Invalid File / You need to upload an Image"
  x = msg.attachments[0].url
  y = url_to_image(x)
  save_img(y,name)
  return ""

def black_and_white(img):
  img = cv.cvtColor(img,cv.COLOR_RGB2GRAY)
  return img

def edge_detection(img):
  canny = cv.Canny(cv.cvtColor(img,cv.COLOR_RGB2GRAY),0,255)
  return canny

def smoothning(img,x):
  img = cv.GaussianBlur(img,(x,x),0)
  return img

def sharpening(img):
  new_filter = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
  img = cv.filter2D(img,-1,new_filter)
  return img

def add_filter(img,prob):
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

def sketch(img , col):
  sketch_gray, sketch_color = cv.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
  return (sketch_color if col else sketch_gray)

def stylized(img):
  img = cv.stylization(img, sigma_s=60, sigma_r=0.07)
  return img

def frame(img,x):
  img = cv.copyMakeBorder(img,x,x,x,x,cv.BORDER_CONSTANT,value=[255,0,0])
  return img

def merge_and_create(a,b,c,d):
  a = cv.resize(a,(250,250))
  b = cv.resize(b,(250,250))
  c = cv.resize(c,(250,250))
  d = cv.resize(d,(250,250))
  first = np.vstack([a,b])
  second = np.vstack([c,d])
  final = np.hstack([first,second])
  cv.imwrite('x.png',final)
  return cv.imread('x.png')

def encryption(a,b):
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

def decryption(img):
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
              


client = discord.Client() 
#global variable for image
ok = 0
f = 0
collage = 0
stegno = 0

#global variable for dictionary
started = 0
global_word = "ab"
user_hint = 0
user = dict()
word_list = []
d = requests.get("https://www.mit.edu/~ecprice/wordlist.10000")
word_str = d.content.decode('utf-8')
word_list = word_str.split("\n")

#global variable for quiz
with urllib.request.urlopen("https://opentdb.com/api.php?amount=50&type=multiple") as url:
    data = json.loads(url.read().decode())
user = {}
ArrChoice = []
act_user = "NONE"
client = discord.Client()
rnd = 0
cnt = 0
timedel = 0

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name=" !image_help , !help , !quiz"))
  print("Hello : {0.user}".format(client))

@client.event
async def on_message(msg):
  global started
  global user_hint
  global ok
  global f
  global collage,stegno
  global timedel
  global act_user
  global ArrChoice
  global rnd
  global cnt
  if msg.author == client.user:
    return 
  if msg.content.startswith('!leader'):
    for name in user:
      await msg.channel.send(str(name) + " --> " + str(user[name]))
    return
  elif msg.content.startswith('!image_help'):
    ans_str = "1. !image : for 1 image processing\n2. !multiimage : for creating collage\n3. !stegno : for encryption and decryption"
    await msg.channel.send(ans_str)
  elif msg.content.startswith('!multiimage') or collage > 0:
    if collage == 0:
      await msg.channel.send("Add Four Images To Create Collage")
      collage = 4
    elif collage == 4:
      p = get_and_save_image(msg,'a.png')
      collage -= 1
    elif collage == 3:
      p = get_and_save_image(msg,'b.png')
      collage -= 1
    elif collage == 2:
      p = get_and_save_image(msg,'c.png')
      collage -= 1
    elif collage == 1:
      p = get_and_save_image(msg,'d.png')
      collage -= 1
    if collage == 0:
      a = cv.imread('a.png')
      b = cv.imread('b.png')
      c = cv.imread('c.png')
      d = cv.imread('d.png')
      img = merge_and_create(a,b,c,d)
      save_img(img,'x.png')
      await msg.channel.send(file=discord.File('x.png'))
  elif (msg.content.startswith("!stegno") or stegno):
    if stegno == 0 :
      await msg.channel.send("What do you wanna do ?? [e : encryption, d : decryption]")
      stegno = 1
    elif (stegno == 5 or stegno == 4):
      #encryption
      if stegno == 5:
        p1 = get_and_save_image(msg,'e.png')
        stegno -= 1
      else:
        p2 = get_and_save_image(msg,'d.png')
        img = encryption(cv.imread('e.png'),cv.imread('d.png'))
        save_img(img,'x.png')
        await msg.channel.send(file=discord.File('x.png'))
        stegno = 0
    elif stegno == 3:
      #decryption
      p = get_and_save_image(msg,'d.png')
      a , b = decryption(cv.imread('d.png'))
      save_img(a,'e.png')
      save_img(b,'d.png')
      await msg.channel.send(file=discord.File('e.png'))
      await msg.channel.send(file=discord.File('d.png'))
      stegno = 0
    else:
      if msg.content == "e":
        stegno = 5
        await msg.channel.send("Upload 2 Images that you wanna encrypt....(It'll take 2/3 minutes so be patient)")
      else:
        stegno = 3
        await msg.channel.send("Upload Image that you wanna decrypt..(It'll take 2/3 minutes so be patient)")
  elif msg.content.startswith('!image'):
    ok = 1
    await msg.channel.send("Upload an image here.....")
  elif ok == 1:
    p = get_and_save_image(msg,'x.png')
    feature = "Which filter/feature you wanna apply(Write 1/2/3..) ??\n 1. Black and White\n 2. Filter\n 3. Blur\n 4. Edge detection\n 5. Sharpening\n 6. Gray Sketch\n 7. Colour Sketch\n 8. Stylization\n 9. Frame"
    if p != "":
      await msg.channel.send(p)
    else:
      await msg.channel.send(feature)
      ok = 0
      f = 1
  elif f == 1:
    img = cv.imread('x.png')
    ok = 0
    f = 0
    if msg.content == "1":
      img = black_and_white(img)
    elif msg.content == "2":
      img = add_filter(img,0.05)
    elif msg.content == "3":
      img = smoothning(img,5)
    elif msg.content == "4":
      img = edge_detection(img)
    elif msg.content == "5":
      img = sharpening(img)
    elif msg.content == "6":
      img = sketch(img,0)
    elif msg.content == "7":
      img = sketch(img,1)
    elif msg.content == "8":
      img = stylized(img)
    elif msg.content == "9":
      img = frame(img,50)
    save_img(img,'x.png')
    await msg.channel.send(file=discord.File('x.png'))
  
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

  elif (started == 1 or msg.content.startswith('!start')):
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

  elif msg.content.startswith('!quiz'):
    ArrChoice.clear()
    rnd = random.randint(0, 49)
    Question = html.unescape(data['results'][rnd]['question'])
    await msg.channel.send("Question: " + Question)
    ArrChoice.append(html.unescape(data['results'][rnd]['correct_answer']))
    for i in range (0, 3):
      ArrChoice.append(html.unescape(data['results'][rnd]['incorrect_answers'][i]))
    random.shuffle(ArrChoice)
    option = "A"
    for word in ArrChoice:
      await msg.channel.send(chr(ord(option) + cnt) + ") " + word)
      cnt += 1
    cnt = 0
    return
  answer_given = str(msg.content)
  answer_given = answer_given.upper()
  if len(answer_given) != 1:
    return
  if answer_given != 'A' and answer_given != 'B' and answer_given != 'C' and answer_given != 'D':
    return
  curr_ans = str(html.unescape(data['results'][rnd]['correct_answer']))
  username = str(msg.author).split("#")[0]
  if not username in user:
    user[username] = 0
  usr_ans = ArrChoice[ord(msg.content.upper()) - 65]
  if curr_ans == usr_ans:
    await msg.channel.send("Correct!")
      #Score Calculation
    user[username] += 1
    ArrChoice.clear()
    return
  await msg.channel.send("Incorrect!")
  await msg.channel.send("Correct Answer is " + curr_ans)
  ArrChoice.clear()
  
keep_alive()
client.run(os.getenv('TOKEN'))
