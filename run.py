from flask import Flask,render_template,send_file,jsonify,send_from_directory,flash, request, redirect, url_for,make_response
import wordapi
import os
import urllib
from html.parser import HTMLParser
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)


UPLOAD_FOLDER='/Users/zeus/Downloads'
ALLOWED_EXTENSIONS=set(['txt','pdf','png','mp4','avi','jpg'])
# @app.route("/")
# def hello():
#     return "Hello World!<a href='/base'>base</a>"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/base")
def base():
    return render_template('base.html')

@app.route("/")
def home():
    return render_template('home.html',title='Learning')

# learn page
###########################word
@app.route("/learn/kanji")
def FindKanjiPage():
    return render_template('./learn/querykanjipage.html',title='Kanji in examples')

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

################# Data api
@app.route("/html/word/<word>")
def getwordhtml(word):
    if len(word)==0:
        return jsonify({'data':'error!!!'})
    if word.endswith('--'):
        wordlist= wordapi.getwordsfirst(word[:-2])
    else:
        wordlist=wordapi.getwords(word)
    print(len(wordlist))
    data=render_template('./learn/wordlist.html',num=len(wordlist),words=wordlist,word=word)
    return jsonify({'data':data})

@app.route("/html/kanji/word/<word>")
def getkanjiwordhtml(word):
    if len(word)==0:
        return jsonify({'data':'error!!!'})

    wordlist=wordapi.getkanjiwords(word)
    print(len(wordlist))
    data=render_template('./learn/wordlist.html',num=len(wordlist),words=wordlist,word=word)
    return jsonify({'data':data})

@app.route("/html/randm/<int:length>")
def getrandmwordhtml(length):
    wordlist=wordapi.getrandmwords(length)
    data=render_template('./learn/wordlist.html',num=len(wordlist),words=wordlist)
    return jsonify({'data':data})

def getrandmwordhtml():
    wordlist=wordapi.getrandmwords()
    return render_template('./learn/wordlist.html',words=wordlist)

############################# upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/upload', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('./learn/upload.html',title='upload')

@app.route('/file-upload', methods=['POST'])
@app.route('/upload', methods=['POST'])
def upload():
    # print('Upload start....',request.form)
    file = request.files['file']
    # print('Upload start1111....','file')
    save_path = os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    current_chunk = int(request.form['dzchunkindex'])

    # If the file already exists it's ok if we are appending to it,
    # but not if it's new file that would overwrite the existing one
    if os.path.exists(save_path) and current_chunk == 0:
        # 400 and 500s will tell dropzone that an error occurred and show an error
        return make_response(('File already exists', 400))
    print('Uploading....','file')
    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except OSError:
        # log.exception will include the traceback so we can see what's wrong 
        print('Could not write to file')
        return make_response(("Not sure why,"
                              " but we couldn't write the file to disk", 500))

    total_chunks = int(request.form['dztotalchunkcount'])

    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
            print(f"File {file.filename} was completed, "
                      f"but has a size mismatch."
                      f"Was {os.path.getsize(save_path)} but we"
                      f" expected {request.form['dztotalfilesize']} ")
            return make_response(('Size mismatch', 500))
        else:
            print(f'File {file.filename} has been uploaded successfully')
    else:
        print(f'Chunk {current_chunk + 1} of {total_chunks} '
                  f'for file {file.filename} complete')

    return make_response(("Chunk upload successful", 200))

############################# api
@app.route("/api/word/<word>")
def getwordapi(word):
    wordlist=wordapi.getwords(word)
    return wordlist

@app.route("/api/randm/<int:length>")
def getrandmwordapi(length):
    wordlist=wordapi.getrandmwords(length)
    return wordlist

@app.route("/api/downloadfile/<path:filepath>")
def getvideopai(filepath):
    filepath1='/Users/zeus/Downloads/%s'%filepath
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


############################################# File player
@app.route('/video/<path:videopath>')
def getvideo(videopath):
    # print(videopath)
    videopath='/'+videopath
    return send_file(HTMLParser().unescape(videopath),conditional=True,as_attachment=True,mimetype='video/x-msvideo')

@app.route('/play/<path:videopath>')
def getplayvideo(videopath):
    # print(videopath)
    return render_template('play.html',title='Play',videourl='/video/'+videopath,type=os.path.splitext(videopath)[-1][1:])

@app.route('/videopages')
def getfolderlist():
    folderlist={'Download':'/Users/zeus/Downloads/','Video':'/Users/zeus/Movies/'}
    if os.path.exists('/Volumes/LENOVO_USB_HDD/'):
        folderlist['HDD']='/Volumes/LENOVO_USB_HDD/'
    for i in folderlist:
        folderlist[i]='/videopages'+folderlist[i]
    print(folderlist)
    return render_template('videopages.html',title='Pages',pages=folderlist)

@app.route('/videopages/<path:folderpath>')
def getvideolist(folderpath):
    folderpath='/'+folderpath
    fs=[os.path.join(folderpath,i) for i in os.listdir(folderpath)]
    videos=[{'name':os.path.basename(i),'path':'/play'+i} for i in fs if i.lower().endswith('.flv') or i.lower().endswith('.mp4') or i.lower().endswith('.mkv')]
    folders=[{'name':os.path.basename(i),'path':'/videopages'+i} for i in fs if os.path.isdir(i)]
    return render_template('folderpage.html',title='Videos',videos=videos,folders=folders)
################################################# Timer
# import time,os,sched,datetime
# schedule = sched.scheduler(time.time,time.sleep)
# def perform_command(cmd,inc):
#   os.system(cmd)
#   print('task')
# def timming_exe(cmd,inc=60):
#   schedule.enter(inc,0,perform_command,(cmd,inc))
#   schedule.run()
# clocktime=datetime.time(22,50,0,0)
# today=datetime.datetime.now()
# logouttime=datetime.datetime.combine(today,clocktime)
# datetime.date.today()
# seconds=(logouttime-today).total_seconds()
# # if seconds>0:
# #     timming_exe('open -a "/Applications/Google Chrome.app" http://neelab.elec.fit.ac.jp/sotu_comm/logout.php',(logouttime-today).total_seconds())
# def logout():
#     os.system('open -a "/Applications/Google Chrome.app" http://neelab.elec.fit.ac.jp/sotu_comm/logout.php')
# from threading import Timer
# Timer(seconds,logout).start()

# return example
@app.route("/learn/newexamples")
def getNewExamplePage():
    examplelist=wordapi.getExamples(20)
    examplelist=[(n,i) for n,i in enumerate(examplelist)]
    with open('examples.txt','a+') as f:
        f.write(json.dumps(examplelist))
        f.write('---')
    return render_template('./learn/examples.html',title='New Examples',examplelist=examplelist)
@app.route("/learn/examples/list")
def getExampleList():
    if not os.path.exists('examples.txt'):
        return redirect("/learn/newexamples")

    with open('examples.txt','r+') as f:
        txt=f.read()
    if len(txt)==0:
        return redirect("/learn/newexamples")
    examples=txt.split('---')
    examples=examples[:-1]
    num= [i+1 for i in range(len(examples))]
    return render_template('./learn/exampleslist.html',num=num)
@app.route("/learn/examples/<int:num>")
def getExamplePage1(num):
    if not os.path.exists('examples.txt'):
        return redirect('/learn/newexamples')

    with open('examples.txt','r+') as f:
        txt=f.read()
    if len(txt)==0 :
        return redirect('/learn/newexamples')

    examples=txt.split('---')
    examples=examples[:-1]
    if len(examples) < num:
         return redirect('/learn/newexamples')
    examplelist=json.loads(examples[num-1])
    return render_template('./learn/examples.html',title='Examples %s'%(num),examplelist=examplelist)
app.run('0.0.0.0',debug=True)