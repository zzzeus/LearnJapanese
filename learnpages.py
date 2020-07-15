from flask import Flask,render_template,send_file,jsonify,send_from_directory,flash, request, redirect, url_for,make_response
import wordapi
import os
import urllib
from html.parser import HTMLParser
from werkzeug.utils import secure_filename

# learn page
###########################word
@app.route("/learn/word")
def getwordpage():
    return render_template('./learn/dictpage.html',title='Words')

@app.route("/learn")
def getlearnpage():
    return render_template('./learn/learnpage.html',title='Learning')

@app.route("/learn/test")
def getwordtestpage():
    return render_template('./learn/testwords.html',title='Test words',wordlist=getrandmwordhtml())

@app.route("/learn/kata")
def getkatawordtestpage():
    wordlist=wordapi.getAllKata()
    
    wordlist={k: wordlist[k] for k in list(wordlist.keys())[0:50]}
    return render_template('./learn/listpage.html',title='Kata words',words=wordlist,noprevious='true',nonext='false',prelink='#',nextlink='/learn/kata/1')
@app.route("/learn/kata/<int:page>")
def getkatawordtestpage1(page):
    wordlist=wordapi.getAllKata()
    islast=(len(wordlist)-50*(page)<=50)
    wordlist={k: wordlist[k] for k in list(wordlist.keys())[page*50+0:page*50+50]}
    # wordlist=wordlist[page*50+0:page*50+50]
    prelink='/learn/kata/%s'%(page-1)
    nextlink='/learn/kata/%s'%(page+1)
    nonext='false'  
    noprevious='false'
    if page==0:
        noprevious='ture'
        prelink='/learn/kata'
        nonext='false'

    elif page==islast:
        nonext='true'
        nextlink='/learn/kata'
    print(nextlink,len(wordlist))
    data=render_template('./learn/listpage.html',title='Kata words',words=wordlist,noprevious=noprevious,nonext=nonext,prelink=prelink,nextlink=nextlink)
    return data

@app.route('/learn/query')
def queryword():
    return render_template('./learn/query.html',title='Dict')

@app.route('/learn/query/<word>')
def queryword1(word):
    if word==1 or len(word)==0:
        return render_template('./learn/query.html',title='Dict')
    if word.endswith('--'):
        wordlist= wordapi.getwordsfirst(word[:-2])
    else:
        wordlist=wordapi.getwords(word)
    print(len(wordlist))
    # data=render_template('./learn/wordlist.html',num=len(wordlist),words=wordlist,word=word)
    return render_template('./learn/query.html',title='Dict',num=len(wordlist),words=wordlist,word=word)

@app.route('/learn/history')
def getHistory():
    with open('history.txt','r+') as f:
        text=f.read()
    history=[{'name':i,'path':''} for i in text.split('!!')[:-1]]
    return render_template('./learn/history.html',title='history',history=history)

# return example
@app.route("/learn/example")
def getExamplePage():
    examplelist=wordapi.getExamples(20)
    return render_template('./learn/examples.html',title='Examples',examplelist=examplelist)