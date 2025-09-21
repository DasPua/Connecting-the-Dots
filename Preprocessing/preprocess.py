from ultralytics import YOLO
import fitz
import numpy as np
import torch

# Automatically choose device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device for YOLO: {DEVICE}")

def process_pdf_to_images(pdf_path):
    """Convert a single PDF to list of images (one per page)"""
    print(f"[STEP] Processing PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    zoom = 1.5
    mat = fitz.Matrix(zoom, zoom)
    page_arrays = []

    for page_num, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            arr = arr[:, :, :3]
        page_arrays.append(arr)
        print(f"[STEP] Processed page {page_num}, shape: {arr.shape}")

    return page_arrays

def get_images_from_bounding_boxes(pdf_path, model_path="./Models/best.pt"):
    """Get cropped images for a single PDF using YOLO"""
    images = process_pdf_to_images(pdf_path)
    results = []

    print(f"[STEP] Loading YOLO model from {model_path} on device {DEVICE}...")
    model = YOLO(model_path, task="detect")

    predicts = model.predict(images, verbose=True, device=DEVICE, batch=64)
    for page_index, predict in enumerate(predicts):
        for box in predict.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            cropped_img = predict.orig_img[y1:y2, x1:x2].copy()
            info = {"class_id": class_id, "final_image": cropped_img, "page": page_index}
            results.append(info)
            print(f"[STEP] Detected class {class_id} on page {page_index}, box: ({x1},{y1},{x2},{y2})")

    print(f"[INFO] Total cropped images extracted: {len(results)}")
    return results
