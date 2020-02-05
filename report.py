from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import webbrowser

# If modifying these scopes, delete the file token.pickle.


class Report:
    def __init__(self,SCOPES,TEMPLATE_ID='1MH9515IunzmwZbPOqkctSrlxJFgCW_eOQmRl-j0vqUI'):
        self.SCOPES = SCOPES
        self.TEMPLATE_ID = TEMPLATE_ID
        self._validate()

    def _validate(self):
        creds = None

        #checks if token.pickel exists already
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                        "docs_config.json",self.SCOPES)
                creds = flow.run_local_server(port=8080)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.docs = build('docs', 'v1', credentials=creds)
        self.drive = build('drive', 'v3', credentials=creds)

    def _format_for_merge(self,key,value):
        key = f"{{{{{key}}}}}" #dont ask why 10 braces
        formatted = {
        'replaceAllText': {
            'containsText': {
                'text': key,
                'matchCase':  'true'
            },
            'replaceText': value,
            }
        }
        return formatted

    def form_report(self,data):
        #document = service_docs.documents().get(documentId=DOCUMENT_ID).execute()

        date = datetime.datetime.now().strftime("%y/%m/%d")

        requests = []

        #put all entities in merge format
        for key,value in data.items():
            if(type(value)!=type([])):
                requests.append(self._format_for_merge(key,value))
            else:
                value = "\n".join(value)
                requests.append(self._format_for_merge(key,value))

        requests.append(self._format_for_merge("date",str(date)))

        #copy template to new file
        report_template = self.drive.files().copy(fileId=self.TEMPLATE_ID,body={"name":f"Report {data['pat_name']}"}).execute()
        report = self.docs.documents().batchUpdate(documentId=report_template['id'], body={'requests': requests}).execute()
        report_url = f"https://docs.google.com/document/d/{report['documentId']}/edit"
        webbrowser.open(report_url)

        return report_url

if __name__ == '__main__':
    data = {
    "hospital_name":"XYZ",
    "doctor_name":"abc",
    "doctor_speciality":"MBBS",
    "hospital_address":"B10",
    "pat_address":"A10",
    "hospital_phone":"102918127",
    "pat_id":"1",
    "pat_age":"20",
    "pat_name":"harsheet",
    "symptoms":["fever","headache"],
    "tests":["ABX","SHA"],
    "medicines":["xxi","paracetamol"],
    "hospital_email":"hospital@gmail.com",
    "diagnosis": "Maleria"
    }
    report = Report()
    report.form_report(data)
