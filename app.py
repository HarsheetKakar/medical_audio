from flask import Flask,render_template,request,url_for,redirect
import pyrebase
import json
from script import Speech
from time import gmtime, strftime
import speech_recognition as sr
from thread import ContinuousThread
from queue import Queue
import werkzeug
import threading
from datetime import datetime
#flask setup
app = Flask(__name__)

threads = []
audio_queue = Queue()

#firebase setup
with open("config.json",'r') as configuration_file:
    config = json.loads(configuration_file.read())

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()

def get_name(user):
    return user['email'].split('@')[0]

@app.route('/login',methods=['POST','GET'])
def login():
    if(request.method == "POST"):
        email = request.form['email']
        password = request.form['password']
        try:
            if(email and password):
                user = auth.sign_in_with_email_and_password(email,password)
            return redirect(url_for('home'))
        except Exception as e:
            print(f"error {e}")
            return "Wrong email or password"
    else:
        return render_template('login.html')

@app.route('/signup',methods=['POST','GET'])
def signup():
    if(request.method == "POST"):
        email = request.form['email']
        password = request.form['password']
        try:
            if(email and password):
                user = auth.create_user_with_email_and_password(email,password)
            return redirect(url_for('login'))
        except Exception as e:
            print(f"error : {e}")
            return "Unable to signup"
    else:
        return render_template('signup.html')

@app.route('/home')
@app.route('/',methods=['GET','POST'])
def home():
    global audio_queue
    def gen(patients):
        if(not patients):
            return

        for i,v in patients.items():
            yield v

    if(auth.current_user):
        if(request.method=='POST'):
            try:
                if(request.form['bot_start']=='start'):
                    bot()

            except werkzeug.exceptions.BadRequestKeyError:
                if(threads):
                    audio_queue=Queue()
                    audio_queue.put(None)
                    for i in threads:
                        i.stop()

        name = get_name(auth.current_user)
        patients = db.child("Appointments").child(name).get().val()
        patients = gen(patients)

        return render_template("home.html",patients=patients if patients else [],doctor={"name":"Dr. "+name})
    else:
        return redirect(url_for('login'))

def add_audio_to_queue(audio_queue):
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio_queue.put(r.listen(source))
    except KeyboardInterrupt:
        pass

def bot():
    r = sr.Recognizer()
    if(auth.current_user):
        speech = Speech(auth.current_user)
        t1 = ContinuousThread(target=add_audio_to_queue,args=[audio_queue],daemon=True)
        t2 = ContinuousThread(target=speech.recognize_worker,args=[audio_queue,db,r],daemon=True)
        t1.start()
        t2.start()
        threads.append(t1)
        threads.append(t2)
        return threads

@app.route('/logout')
def logout():
    auth.current_user = None
    return redirect(url_for('login'))

def add_appointment():
    doc_name = auth.current_user['email'].split('@')[0]
    name = request.form['patient_name']
    time = request.form['patient_time']
    patient = {
    "name": name,
    "time": time
    }
    if(patient["name"] and patient["time"]):
        db.child("Appointments").child(doc_name).push(patient,auth.current_user['idToken'])

if __name__ == '__main__':
    app.run(debug=True)
