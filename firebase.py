import pyrebase
import json

with open("config.json",'r') as configuration_file:
    config = json.loads(configuration_file.read())

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
