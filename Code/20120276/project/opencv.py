import os
import cv2

def RGBtoGray(file, file_url):
    path = os.getcwd() + file_url
    gray_image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    filename, extension = os.path.splitext(file)
    gray_filename = filename + '_grayscale' + extension
    gray_file_url = os.path.dirname(path) + '/' + gray_filename

    cv2.imwrite(gray_file_url, gray_image)

    return gray_filename

def face_detection(file, file_url):
    path = os.getcwd() + file_url
    img = cv2.imread(path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_classifier = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    
    face = face_classifier.detectMultiScale(
            gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )

    for (x, y, w, h) in face:
        face_img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 4)

    filename, extension = os.path.splitext(file)
    face_filename = filename + '_face' + extension
    face_file_url = os.path.dirname(path) + '/' + face_filename

    cv2.imwrite(face_file_url, face_img)

    return face_filename