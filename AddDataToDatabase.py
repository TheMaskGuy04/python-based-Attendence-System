
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendencesystem-4f08e-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "21102A0064":
    {
        "Name": "Miral Gudhka",
        "Major": "CMPN",
        "Admission_Year": 2021,
        "Current_year": 2,
        "Standing": "G",
        "total_attendence": 10,
        "Last_Attendence_time": "2023-2-15 00:54:34"
    },
    "21102A0066":
    {
        "Name": "Shubman Gill",
        "Major": "INFT",
        "Admission_Year": 2020,
        "Current_year": 3,
        "Standing": "G",
        "Total_attendence": 9,
        "Last_Attendence_time": "2023-2-11 00:54:10"
    },
    "21102A0067":
    {
        "Name": "Susham Desai",
        "Major": "BIOM",
        "Admission_Year": 2022,
        "Current_year": 1,
        "Standing": "B",
        "total_attendence": 6,
        "Last_Attendence_time": "2023-2-15 00:54:34"
    },
    "21102A0016":
    {
        "Name": "Premanshu Chaudhari",
        "Major": "Mechanical",
        "Admission_Year": 2021,
        "Current_year": 2,
        "Standing": "B",
        "total_attendence": 5,
        "Last_Attendence_time": "2023-2-15 00:50:36"
    }
}

for key,value in data.items():
    ref.child(key).set(value)

