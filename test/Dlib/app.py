import dlib
import numpy as np
import cv2

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("shape_predictor_5_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

def convert_and_trim_bb(image, rect):
    # extract the starting and ending (x, y)-coordinates of the
    # bounding box
    startX = rect.left()
    startY = rect.top()
    endX = rect.right()
    endY = rect.bottom()
    # ensure the bounding box coordinates fall within the spatial
    # dimensions of the image
    startX = max(0, startX)
    startY = max(0, startY)
    endX = min(endX, image.shape[1])
    endY = min(endY, image.shape[0])
    # compute the width and height of the bounding box
    w = endX - startX
    h = endY - startY
    # return our bounding box coordinates
    return (startX, startY, w, h)


#load images
img1 = dlib.load_rgb_image("img1.png")
img2 = dlib.load_rgb_image("img2.png")
 
#detection
img1_detection = detector(img1, 1)
img2_detection = detector(img2, 1)

img1_box = [convert_and_trim_bb(img1, r) for r in img1_detection]
for (x, y, w, h) in img1_box:
    # draw the bounding box on our image
    cv2.rectangle(img1, (x, y), (x + w, y + h), (0, 255, 0), 2) 

cv2.imwrite('img1_out.png', img1)

img2_box = [convert_and_trim_bb(img2, r) for r in img2_detection]
for (x, y, w, h) in img2_box:
    # draw the bounding box on our image
    cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 255, 0), 2) 

cv2.imwrite('img2_out.png', img2)

 
img1_shape = sp(img1, img1_detection[0])
img2_shape = sp(img2, img2_detection[0])
 


#alignment
img1_aligned = dlib.get_face_chip(img1, img1_shape)
img2_aligned = dlib.get_face_chip(img2, img2_shape)

img1_representation = facerec.compute_face_descriptor(img1_aligned)
img2_representation = facerec.compute_face_descriptor(img2_aligned)



img1_representation = np.array(img1_representation)
img2_representation = np.array(img2_representation)

def findEuclideanDistance(source_representation, test_representation):
    euclidean_distance = source_representation - test_representation
    euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))
    euclidean_distance = np.sqrt(euclidean_distance)
    return euclidean_distance

distance = findEuclideanDistance(img1_representation, img2_representation)
threshold = 0.6 #distance threshold declared in dlib docs for 99.38% confidence score on LFW data set
 
if distance < threshold: 
    print("they are same")
else: 
    print("they are different")
