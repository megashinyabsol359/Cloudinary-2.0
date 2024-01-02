import os
import cv2
from ultralytics import YOLO
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
    crop_file_url = os.path.dirname(path) + '/' + crop_filename

    cv2.imwrite(crop_file_url, cropped_image)

    return crop_filename

def rotate(file, file_url, angle):
    path = os.getcwd() + file_url
    img = cv2.imread(path)
    
    height, width = img.shape[:2] # image shape has 3 dimensions
    image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape
    
    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)
    
    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0,0]) 
    abs_sin = abs(rotation_mat[0,1])
    
    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)
    
    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]
    
    # rotate image with the new bounds and translated rotation matrix
    rotated_img = cv2.warpAffine(img, rotation_mat, (bound_w, bound_h))

    filename, extension = os.path.splitext(file)
    rotate_filename = filename + '_rotate' + extension
    rotate_file_url = os.path.dirname(path) + '/' + rotate_filename

    cv2.imwrite(rotate_file_url, rotated_img)

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

# def hsv(file, file_url, h, s, v):
#     path = os.getcwd() + file_url
#     img = cv2.imread(path, cv2.IMREAD_COLOR)

#     # Changes the H value
#     img[1:,:,0] = (img[1:,:,0] + h) % 180
#     # Changes the S value
#     img[2:,:,1] += s
#     # Changes the V value
#     img[:,:,2] += v

#     hsv = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

#     filename, extension = os.path.splitext(file)
#     hsv_filename = filename + '_hsv' + extension
#     hsv_file_url = os.path.dirname(path) + '/' + hsv_filename

#     cv2.imwrite(hsv_file_url, hsv)

#     return hsv_filename
# 
# 
def hsv(file, file_url, h, s, v):
    path = os.getcwd() + file_url
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv[:,:,0] = (hsv[:,:,0] + h) % 180
    hsv[:,:,1] = np.where((255 - hsv[:,:,1]) < s,255,hsv[:,:,1]+s) # Changes the S value
    hsv[:,:,2] = np.where((255 - hsv[:,:,2]) < v,255,hsv[:,:,2]+v) # Changes the V value
    hsv = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    filename, extension = os.path.splitext(file)
    hsv_filename = filename + '_hsv' + extension
    hsv_file_url = os.path.dirname(path) + '/' + hsv_filename

    cv2.imwrite(hsv_file_url, hsv)

    return hsv_filename

def object_detection(file, file_url):
    path = os.getcwd() + file_url
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    model = YOLO('yolov8n.pt')
    
    results = model.predict(img, show=True)
    im_array = results[0].plot()  # plot a BGR numpy array of predictions
    im_array = cv2.cvtColor(im_array, cv2.COLOR_RGB2BGR)
    
    filename, extension = os.path.splitext(file)
    object_filename = filename + '_object_detection' + extension
    object_file_url = os.path.dirname(path) + '/' + object_filename

    cv2.imwrite(object_file_url, im_array)

    return object_filename
