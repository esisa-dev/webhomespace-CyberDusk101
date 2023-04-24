from flask import (
    Flask,
    render_template,
    url_for
    ,request,
    session,
    redirect,
    send_file
) 

import spwd
import crypt
import os
import shutil
import crypt
import time
import pwd



import logging

logging.basicConfig(filename='trackUser.log', level=logging.DEBUG)



app = Flask(__name__)



app.secret_key = 'webhomeadmin'
app.secret_key = os.urandom(24)


@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    print(response)#test
    return response

@app.route("/")
def home():
    logging.debug('A user just visited the home page')
    return render_template("index.html")

@app.route("/", methods=["POST"])
def login():
        username = request.form["username"]
        password = request.form["password"]
        try:
            spwd.getspnam(username)#type:ignore
        except KeyError:
            return "Invalid username or password"
        hashed_password = spwd.getspnam(username).sp_pwdp #type:ignore
        if not crypt.crypt(password, hashed_password) == hashed_password:#type:ignore
            return "Invalid username or password"
        session["username"] = username
        session["logged_in"] = True
        session["logged_out"] = False

        timeOfDirs = {}
        sizesOfFiles = {}
        timeOfFiles = {}
        dirs = []
        files = []
        
        logging.debug('A user just Connected '+ '{ '+ username + ' }')
        homeDirectory = pwd.getpwnam(session["username"]).pw_dir #type:ignore
        Space = space(homeDirectory)

        for item in os.listdir(homeDirectory):
            if os.path.isfile(os.path.join(homeDirectory, item)):
                files.append(item)
                sizesOfFiles[item] = round(os.path.getsize(os.path.join(homeDirectory, item)) / 1024)
                timeOfFiles[item] = time.ctime(os.path.getmtime(os.path.join(homeDirectory, item)))
                
        
        for item in os.listdir(homeDirectory):
            if os.path.isdir(os.path.join(homeDirectory, item)):
                dirs.append(item)
                timeOfDirs[item] = os.path.getmtime(os.path.join(homeDirectory, item))
       
        return render_template('greeting.html', username=username, homeDirectory=homeDirectory, files=files, dirs=dirs, space=Space,
                                sizesOfFiles=sizesOfFiles, timeOfFiles=timeOfFiles, timeOfDirs=timeOfDirs)




@app.errorhandler(Exception)
def error(exception):
    return render_template('error.html', error = 
    {
        "ip":request.remote_addr,
        "method":request.method,
        "error":exception
    })



def space(userDirect):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(userDirect):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024*1024)



@app.route('/download')
def download():
    username= session.get("username")
    working_dir = pwd.getpwnam(username).pw_dir#type:ignore
    home_dir_zip = shutil.make_archive('homedir', 'zip', working_dir)
    logging.debug('A user just downloaded their home directory  '+ '{ '+ session["username"] + ' }')
    return send_file(home_dir_zip, as_attachment=True,mimetype='application/zip')
    #problem
    #lhome directory matatmchich as_atachement.


@app.route('/logout')
def logout():
    logging.debug('A user just Disconnected '+ '{ '+ session["username"] + ' }')
    session.clear()
    session['logged_out'] = True
    return render_template("index.html")



if __name__ == "__main__" :
    app.run(debug=True,port=8080)
    #http://127.0.0.1:8080 localhost:8080
    
    
    
    