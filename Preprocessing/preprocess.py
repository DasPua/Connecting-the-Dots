from pdf2image import convert_from_path
from ultralytics import YOLO
import os
import fitz
import numpy as np
import time
import cv2

pdfs_path = "./input"

def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    zoom = 1.5
    mat = fitz.Matrix(zoom, zoom)
    page_arrays = []

    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4: 
            arr = arr[:, :, :3]
        # arr=cv2.resize(arr, (0,0), fx=0.5, fy=0.5)
        # arr = arr.astype('float32') / 255.0
        page_arrays.append(arr)
    return page_arrays

def convert_to_images(pdfs_path):
    images = []
    cnt = 0
    for pdf in os.listdir(os.path.abspath(pdfs_path)):
        cnt += 1
        images.append(process_pdf(os.path.join(os.path.abspath(pdfs_path), pdf)))
        if cnt == 10: 
            break
    return images    

def get_images_from_bounding_boxes(pdfs_path):
    images = convert_to_images(pdfs_path)
    results = []
    model_path = "../Models/tiny_best.pt"
    model = YOLO(model_path, task="detect")
    for image in images:
        predicts = model.predict(image, verbose=False, device='cpu', batch=64)
        for i, predict in enumerate(predicts):
            for box in predict.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_id = box.cls[0]
                cropped_img = predict.orig_img[y1:y2, x1:x2].copy()
                
                information = {
                    "class_id": class_id,
                    "final_image": cropped_img,
                    "page": i
                }
                results.append(information)
    return results
