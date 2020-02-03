import speech_recognition as sr
from time import gmtime, strftime
import pyrebase
import json

class Speech:
    def __init__(self,user):
        self.user = user

    def getDict(self,s):
        a = {
            "text": s,
            "time": strftime("%Y-%m-%d %H:%M:%S", gmtime())
        }
        return a

    def getJSON(self,text):
        return json.dumps(self.getDict(text))

    def recognize_worker(self,audio_queue,db,r):
        audio = audio_queue.get()
        try:
            if audio is None: return

            text = r.recognize_google(audio)

            x = str(self.user['email']).split('@')[0]

            db.child("Convo").child(x).push(self.getDict(text),self.user['idToken'])

            print(f"sent to firebase: {text}")

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except AssertionError:
            return
        finally:
            pass

if __name__ == '__main__':

    with open("config.json",'r') as configuration_file:
        config = json.loads(configuration_file.read())

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    auth = firebase.auth()

    while(True):
        email = "test@gmail.com"
        password = "123456"
        try:
            user = auth.sign_in_with_email_and_password(email,password)
            break
        except Exception as e:
            print("password wrong")
            continue

    speech = Speech(user)
    recognize_thread = Thread(target=speech.recognize_worker,daemon=True)
    recognize_thread.start()

    with sr.Microphone() as source:
        try:
            while True:
                audio_queue.put(r.listen(source))
        except KeyboardInterrupt:
            print("this worked")
            pass

    audio_queue.join()
    audio_queue.put(None)
    recognize_thread.join()
