from firebase import *

class Doctor:
    def __init__(self,user):
        self.user = user
        for i,v in db.child('Doctors').child(self.user['localId']).get().val().items():
            self.doctor = v
            break

    def get_name(self):
        return self.doctor['name']

    def get_spl(self):
        return self.doctor['spl']

    def get_hospital_name(self):
        return self.doctor['hospital_name']

class Patient:
    def __init__(self,user):
        self.user = user
        for i,v in db.child('Patients').child(self.user['localId']).get().val().items():
            self.patient = v
            break

    def get_name(self):
        return self.patient['name']

    def get_address(self):
        return self.patient['address']

    def get_phone(self):
        return self.patient['phone']

    def get_age(self):
        return self.patient['age']

    def get_gender(self):
        return self.patient['gender']

    def get_prescription(self):
        return self.patient['prescription']

    def get_report(self):
        return self.patient['prescription']['report_url']

    def get_diseases(self):
        return self.patient['prescription']['disease']

    def get_tests(self):
        return self.patient['prescription']['tests']

    def get_meds(self):
        return self.patient['prescription']['meds']

    def get_symptoms(self):
        return self.patient['prescription']['symptoms']

    def get_advice(self):
        return self.patient['prescription']['advice']

    def get_appointment(self):
        return self.patient['prescription']['appointments']

## TODO: implement set appointment function
    def set_appointment(self,date):
        return


if __name__ == '__main__':
    user = auth.sign_in_with_email_and_password('harsheetkakar@gmail.com','123456')
    doc = Doctor(user)
    print(doc.get_name())
