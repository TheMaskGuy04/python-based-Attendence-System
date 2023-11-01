import cv2 as cv
import face_recognition
import pickle 
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendencesystem-4f08e-default-rtdb.firebaseio.com/",
    'storageBucket':"attendencesystem-4f08e.appspot.com"
})

# Importing the Student images 
folderimgPath = 'Images'
imgPathList = os.listdir(folderimgPath)
imgList = []
studentIds = []
# print(imgPathList)

for path in imgPathList:
    imgList.append(cv.imread(os.path.join(folderimgPath,path)))
    # print(os.path.splitext(path)[0])
    studentIds.append(os.path.splitext(path)[0])

    fileName = f'{folderimgPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


print(studentIds)

def findEncoding(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv.cvtColor(img,cv.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
        
    return encodeList

print("Encoding Started...")
encodeListKnown = findEncoding(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
# print(encodeListKnown)
print("...Encoding Complete")


file = open("Encodefile.p",'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")

