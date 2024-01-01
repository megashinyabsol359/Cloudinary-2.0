import os
import cv2
import torch
import numpy as np

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

def crop(file, file_url, x1, x2, y1, y2):
    path = os.getcwd() + file_url
    img = cv2.imread(path)
    
    cropped_image = img[x1:x2, y1:y2]

    filename, extension = os.path.splitext(file)
    crop_filename = filename + '_crop' + extension
    face_file_url = os.path.dirname(path) + '/' + crop_filename

    cv2.imwrite(crop_file_url, cropped_image)

    return crop_filename

def rotate(file, file_url, x, cX, cY):
    path = os.getcwd() + file_url
    img = cv2.imread(path)
    
    # grab the dimensions of the image and calculate the center of the
    # image
    (h, w) = img.shape[:2]
    
    (cX, cY) = (w // 2, h // 2)
    
    # rotate our image by 45 degrees around the center of the image
    M = cv2.getRotationMatrix2D((cX, cY), 45, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h))

    filename, extension = os.path.splitext(file)
    rotate_filename = filename + '_rotate' + extension
    rotate_file_url = os.path.dirname(path) + '/' + rotate_filename

    cv2.imwrite(rotate_file_url, rotated)

    return rotate_filename

def resize(file, file_url, x):
    path = os.getcwd() + file_url
    img = cv2.imread(path)
    
    width = int(img.shape[1] * x / 100)
    height = int(img.shape[0] * x / 100)
    dim = (width, height)
    
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    filename, extension = os.path.splitext(file)
    resize_filename = filename + '_resize' + extension
    resize_file_url = os.path.dirname(path) + '/' + resize_filename

    cv2.imwrite(resize_file_url, resized)

    return resize_filename

def hsv(file, file_url, h, s, v):
    path = os.getcwd() + file_url
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    
    # Changes the H value
    img[1:,:,0] = (img[1:,:,0] + h) % 180
    
    # Changes the S value
    img[2:,:,1] += s
    
    # Changes the V value
    img[:,:,2] += v
    
    hsv = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

    filename, extension = os.path.splitext(file)
    hsv_filename = filename + '_resize' + extension
    hsv_file_url = os.path.dirname(path) + '/' + hsv_filename

    cv2.imwrite(hsv_file_url, hsv)

    return hsv_filename

def object_detection(file, file_url):
    path = os.getcwd() + file_url
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # force_reload = recache latest code
    model.eval()
    results = model([img])
    results.render()  # updates results.imgs with boxes and labels

    filename, extension = os.path.splitext(file)
    gray_filename = filename + '_object_detection'
    gray_file_url = os.path.dirname(path) + '/' + gray_filename

    results.save(save_dir=gray_file_url)
    #cv2.imwrite(gray_file_url, results.imgs[0])

    return gray_filename + '/image0.jpg'
