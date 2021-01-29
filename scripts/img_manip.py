from PIL import Image
import imagehash
import cv2 as cv
import imutils
import numpy as np

def cv_to_pil(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    return img

def get_hash(img):
    return int(str(imagehash.dhash(img)),16)

def cv_get_hash(img):
    img = cv_to_pil(img)
    return get_hash(img)

def bit_count(n):
    count = 0
    while (n):
        count += n & 1
        n >>= 1
    return count

def hash_compare(hash1, hash2):
    return bit_count(hash1 ^ hash2)

def img_compare(img1, img2):
    hash1 = get_hash(img1)
    hash2 = get_hash(img2)

    return hash_compare(hash1, hash2)

def resize(scale_percent, img):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dsize = (width, height)

    return cv.resize(img, dsize)

def display(img):
    try:
        img = cv_to_pil(img)
    except:
        pass
    img.show()

def find_card_border(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    mat_sz = 3
    blur = cv.blur(gray,(mat_sz,mat_sz))

    edges = cv.Canny(blur,100,200)

    sz = 2
    kernel = np.ones((sz,sz),np.uint8)
    filled_edges = cv.morphologyEx(edges,cv.MORPH_GRADIENT,kernel)

    contours,hierarchy = cv.findContours(filled_edges,1,2)

    if not contours:
        h,w,channels = img.shape
        return ((w/2,h/2),(w,h),0)

    max_cont = contours[0]
    max_cont_ar = cv.contourArea(contours[0])
    for each_contour in contours:
        area = cv.contourArea(each_contour)
        if area > max_cont_ar:
            max_cont = each_contour
            max_cont_ar = area
            
    cv.cvtColor(gray, cv.COLOR_GRAY2RGB)

    rect = cv.minAreaRect(max_cont)
    
    return rect

def draw_box (img, rect):
    box = cv.boxPoints(rect)
    box = np.int0(box)

    return cv.drawContours(img,[box],-1,(6,244,7),2)

def crop_to_card (img,rect):
    center, size, angle = rect[0], rect[1], rect[2]
    center, size = tuple(map(int, center)), tuple(map(int, size))

    if angle > 45:
        size = (size[1],size[0])
        angle = angle - 90

    rot = imutils.rotate(img,angle,center)

    img_crop = cv.getRectSubPix(rot, size, center)

    return img_crop

def crop_art(img):
    try:
        img = cv_to_pil(img)
    except:
        pass
    width, height = img.size
    w_act = 672
    h_act = 936
    
    left = 56 * width / w_act
    right = 615 * width / w_act

    top = 110 * height / h_act
    bottom = 518 * height / h_act

    return img.crop((left,top,right,bottom))