from readmdict import MDX, MDD
import random,re
from bs4 import BeautifulSoup
import json
import os
regex = re.compile(r'[a-z]*[āáǎàōóǒòêēéěèīíǐìūúǔùǖǘǚǜüńňǹɑɡ]+[a-z]*')
# text = "Thǐs ís à pìnyin abóut shá"
# m = regex.findall(text)
# print(m)

mdx = MDX('./data/小学馆日中第二版.mdx')
# 71844 只有汉字
# items = mdx.items()

# print(next(items)[0].decode())
# for i  in range(500):
#     i =next(items)
#     print(i[0].decode())
# for i  in range(10):
#     i =next(items)
#     print(i[0].decode())
#     print(i[1].decode())
kata=re.compile('[\u30a1-\u30f6]')
kanji=re.compile('[\u4e00-\u9fa5]')
muti=re.compile(r'(\S\S){2}')
numstart=re.compile('[1-9]\s')

def init():
    files=os.listdir('.')
    kanjiInWords={}
    if not 'findkanji.txt' in files:
        with open('findkanji.txt','w+') as f:
            json.dump({},f)
init()


def getwords(word):
    with open('history.txt','a+') as f:
        f.write('%s!!'%word)
    items = mdx.items()
    words={}
    for i in items:
        w=i[0].decode()
        if word in w:
            meaning=i[1].decode()
            if(meaning.startswith('@')):
                continue
            words[w]=meaning
    if len(words)==1:
        with open('words.txt','a+') as f:
            f.write('%s!!'%word)
    return words

def getExactword(word):
    items = mdx.items()
    words={}
    for i in items:
        w=i[0].decode()
        if word == w:
            return i[1].decode()
    return 'getExactword error!'

## search for kanji which is started
def getwordsfirst(word):
    # 【位】
    with open('historyfirst.txt','a+') as f:
        f.write('%s!!'%word)
    items = mdx.items()
    sign='【%s'% word
    print(sign)
    words={}
    for i in items:
        w=i[0].decode()
        if sign in w or w.startswith(word):
            # print(w)
            meaning=i[1].decode()
            if(meaning.startswith('@')):
                continue
            words[w]=meaning
    return words
#### get randm word list
def getrandmnum(start,stop,listlen):

    number=[]
    for i in range(listlen):
        # 3.生成随机数
        num = random.randint(start, stop)
        # 4.添加到列表中
        number.append(num)
    return number


def getrandmwords(listlen=50):
    items = mdx.items()
    words={}
    nums=getrandmnum(500, 70223,listlen)
    for num,key in enumerate(items):
        if num in nums:
            print(key[0].decode())
            words[key[0].decode()]=key[1].decode()
        if(num>70223):
            break
    return words

def getAllKata():
    items = mdx.items()
    words={}
    for i in items:
        w=i[0].decode()
        if kata.search(w):
            meaning=i[1].decode()
            if(meaning.startswith('@')):
                continue
            words[w]=meaning
    return words


def getWordshasexample():
    items = mdx.items()
    words=[]
    for i in items:
        w=i[0].decode()
        meaning=i[1].decode()
        if '¶' in meaning and not '囲み' in w:
            words.append(w)
    return words

def getmeanings(word):
    wm=getwords(word)
    soup = BeautifulSoup(wm[word], 'html.parser')
    s=soup.get_text().split('\n')
    meanings=[i for i in s if numstart.search(i)]
    
    if len(meanings)==0:
        return regex.sub('',s[2])
    else:
        return regex.sub('','<br>'.join(meanings) )

def getOneExample(word):
    meaning=getExactword(word)
    # print(meaning)
    examples=[]
    lines=meaning.split('<br>')
    for l in lines:
        if '¶' in l:
            examples.append(l)
    # print(word,type(examples),getmeanings(word))
    return word,regex.sub('',examples[random.randint(0,len(examples)-1)]),getmeanings(word)

def getExamples(num=10):
    nums=getrandmnum(0,41910,num)
    wordlist=getWordshasexample()
    examples=[]
    for i in nums:
        examples.append(getOneExample(wordlist[i]))
    return examples


def getSingle():
    items = mdx.items()
    words={}
    for i in items:
        w=i[0].decode()
        if not '【' in w:
            meaning=i[1].decode()
            if(meaning.startswith('@')):
                continue
            words[w]=meaning
    return words

def getMultimeaning():
    items = mdx.items()
    words={}
    for i in items:
        w=i[0].decode()
        meaning=i[1].decode()
        if '☞' in meaning:
            words[w]=meaning
    return words

def getDifficultKanji():
    items = mdx.items()
    words={}
    for i in items:
        w=i[0].decode()
        meaning=i[1].decode()
        if(meaning.startswith('@')):
            words[w]=meaning
    return words
def getAllHira():
    items = mdx.items()
    words={}
    for i in items:
        w=i[0].decode()
        meaning=i[1].decode()
        # if not '☞' in meaning and not '【' in w :
        if not kata.search(w) and not kanji.search(w):
            # if(meaning.startswith('@')):
            #     continue
            words[w]=meaning
    return words

def getrepeated():
    items = mdx.items()
    words={}
    for i in items:
        w=i[0].decode()
        meaning=i[1].decode()
        # if not '☞' in meaning and not '【' in w :
        if w[0:2]==w[2:4]:
            # if(meaning.startswith('@')):
            #     continue
            words[w]=meaning
    return words

#####################
# Find kanji in examples
def findsKanjisInExamples(kanji):
    items = mdx.items()
    words=[]
    for i in items:
        w=i[0].decode()
        meaning=i[1].decode()
        if kanji in meaning:
            words.append(w)

        # if w[0:2]==w[2:4]:
        #     # if(meaning.startswith('@')):
        #     #     continue
        #     words[w]=meaning
    return words
def getwordsfromlist(words):
    items = mdx.items()
    words1={}
    for i in items:
        w=i[0].decode()
        meaning=i[1].decode()
        if w in words:
            words1[w]=meaning
    return words1

def getkanjiwords(kanji):

    text=''
    kanjiInWords={}
    words=[]
    with open('findkanji.txt','r+') as f:
        # text=f.read()
    
        kanjiInWords=json.load(f)
    if kanji in kanjiInWords:
        words=kanjiInWords[kanji]
    else:
        words=findsKanjisInExamples(kanji)
        kanjiInWords[kanji]=words
        with open('findkanji.txt','w+') as f:
            json.dump(kanjiInWords,f)

    return getwordsfromlist(words)
if __name__ == "__main__":
    # a=getrepeated()
    # for i in  a:
    #     print(i)
    #     print(a[i])
    # print(len(a))
    # print(a['囲み-野球'])

    # a=getExamples(10)
    # for i in a:
    #     print(i[0])
    #     print(i[1][0])
    #     print()

    # wordlist=getWordshasexample()
    # print(getwords(wordlist[0]))
    # with open('aa.html','w+') as f:
    #     f.write(getwords(wordlist[0]))

    # w1='かける【掛ける・架ける・懸ける】'
    # w1='はたらきかける【働きかける】'
    # wm=getwords(w1)
    # soup = BeautifulSoup(wm[w1], 'html.parser')
    # s=soup.get_text().split('\n')
    # print(len(s))
    
    # for i in s:
    #     print(i)
    #     print('---')
    # meanings=[i for i in s if numstart.search(i)]
    # print('meanings',len(meanings),'<br>'.join(meanings))
    # if len(meanings)==0:
    #     print(s[2])

    # getOneExample(w1)
    # e=getExamples()
    # print(e)

    # for i in range(30):
    #     print(random.randint(0,3))

    print(getkanjiwords('吃不饱'))


# lists=getTest()
# print(len(lists))

# getOneExample('どっぷり（と）')

# print(getwordsfirst('位').keys())
# getrandmwords()

### enumerate
# for num,key in enumerate(items):
#         print(num,key[0].decode())



    