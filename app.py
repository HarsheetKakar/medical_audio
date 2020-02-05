from flask import render_template,request,url_for,redirect
import json
from speech import Speech
from time import gmtime, strftime
import speech_recognition as sr
from thread import ContinuousThread
from queue import Queue
import werkzeug
import threading
from datetime import datetime
from report import Report
from pprint import pprint
from models import Doctor, Patient
from flask import Flask
from firebase import *

app = Flask(__name__)

threads = []
audio_queue = Queue()

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
        name = request.form['name']
        spl = request.form['spl']
        hospital_name = request.form['hospital_name']
        try:
            if(email and password):
                user = auth.create_user_with_email_and_password(email,password)
                db.child('Doctors').child(user['localId']).push(request.form)
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

        name = Doctor(auth.current_user).get_name()
        print(name)
        #patients = db.child("Appointments").child(name).get().val()
        patients = None

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

@app.route("/report",methods=['GET','POST'])
def report():
    if(auth.current_user):
        if(request.method=='POST'):
            rep = Report(SCOPES=['https://www.googleapis.com/auth/drive.metadata.readonly',
                            'https://www.googleapis.com/auth/documents',
                            'https://www.googleapis.com/auth/drive'])
            doc = Doctor(auth.current_user)
            hospital = Hospital(auth.current_user)
            #make patient database
            data = {
                "hospital_name":hospital.get_name(),
                "doctor_name":doc.get_name(),
                "doctor_speciality":doc.get_spl(),
                "hospital_address":hospital.get_address(),
                "pat_address":"{{abc}}",
                "hospital_phone":hospital.get_phone(),
                "pat_id":"{{1}}",
                "pat_age":"{{20}}",
                "pat_name":"{{harsheet}}",
                "symptoms":request.form['symptoms'],
                "tests":request.form['tests'],
                "medicines":request.form['medicines'],
                "hospital_email":hospital.get_email(),
                "diagnosis": request.form['diagnosis']
            }
            #feed it to database
            report_url = rep.form_report(data)
            return redirect(url_for('home'))
        return render_template('report.html',
                                symptoms = ["{{fever}}"],
                                tests =["{{test}}"],
                                diagnosis=["{{disease}}"],
                                medicines = ['{{par}}'])
    else:
        return redirect(url_for('login'))

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

    
