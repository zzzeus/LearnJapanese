from flask import Flask,render_template,send_file,jsonify,send_from_directory,flash, request, redirect, url_for,make_response
import wordapi
import os
import urllib
from html.parser import HTMLParser
from werkzeug.utils import secure_filename

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