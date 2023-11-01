import cv2 as cv
import os
import numpy as np
import pickle
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendencesystem-4f08e-default-rtdb.firebaseio.com/",
    'storageBucket':"attendencesystem-4f08e.appspot.com"
})

bucket = storage.bucket()

capture = cv.VideoCapture(0)

capture.set(3,640)
capture.set(4,480)

imgBackground = cv.imread('Resources/background.png')

# Importing the mode images into a List
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []

for path in modePathList:
    imgModeList.append(cv.imread(os.path.join(folderModePath,path)))

# print(len(imgModeList))


#Loading the encoding file
print("Loading Encoded File")
file = open('Encodefile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encoded file loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = capture.read()

    imgsmall = cv.resize(img,(0,0),None,0.25,0.25)
    imgsmall = cv.cvtColor(imgsmall,cv.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgsmall)
    encodeCurFrame = face_recognition.face_encodings(imgsmall,faceCurFrame)

    imgBackground[162:162+480,55:55+640] = img
    imgBackground[44:44+633,808:808+414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, FaceLoc in zip(encodeCurFrame,faceCurFrame):
            matches  = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            # print("Matches",matches)
            # print("FaceDis",faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index",matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print("Id of Known Face:",studentIds[matchIndex])
                y1,x2,y2,x1 = FaceLoc
                y1,x2,y2,x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1,162+y1,x2-x1,y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox,rt=0)
                id = studentIds[matchIndex]

                if counter==0:
                    cvzone.putTextRect(imgBackground, "Loading", (275,400))
                    cv.imshow("Attendence",imgBackground)
                    cv.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter!=0:
            if counter == 1:
                # Get the Data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Get the Image from the Storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv.imdecode(array, cv.COLOR_BGRA2BGR)

                # Update data of attendence 
                datetimeobject = datetime.strptime(studentInfo['Last_Attendence_time'],"%Y-%m-%d %H:%M:%S")
                secondsElapsed=(datetime.now()-datetimeobject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:

                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendence'] +=1
                    ref.child('total_attendence').set(studentInfo['total_attendence'])
                    ref.child('Last_Attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44+633,808:808+414] = imgModeList[modeType]

            if modeType !=3:

                if 10 < counter < 20:
                    modeType = 2

                # print("Mode type at 117 line:",modeType," And counter =",counter)
                imgBackground[44:44+633,808:808+414] = imgModeList[modeType]

                if counter <= 10:
                    cv.putText(imgBackground,str(studentInfo['total_attendence']),(861,125),cv.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv.putText(imgBackground,str(studentInfo['Major']),(1006,550),cv.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv.putText(imgBackground,str(id),(1006,493),cv.FONT_HERSHEY_COMPLEX,0.5,(50,50,50),1)
                    cv.putText(imgBackground,str(studentInfo['Standing']),(910,625),cv.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv.putText(imgBackground,str(studentInfo['Current_year']),(1025,625),cv.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv.putText(imgBackground,str(studentInfo['Admission_Year']),(1125,625),cv.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)

                    (w,h), _ = cv.getTextSize(studentInfo['Name'],cv.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414 - w)//2
                    cv.putText(imgBackground,str(studentInfo['Name']),(808+offset,445),cv.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)

                    imgBackground[175:175 + 216,909:909 + 216] = imgStudent

                counter +=1

                if counter>=20:
                    ccounter = 0
                    modeType =0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44+633,808:808+414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    # cv.imshow("Webcam",img)
    cv.imshow("Attendence",imgBackground)
    cv.waitKey(1)

