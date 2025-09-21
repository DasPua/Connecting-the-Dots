from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import time
import json
from collections import defaultdict
import easyocr
import torch

from Preprocessing import get_images_from_bounding_boxes

UPLOAD_FOLDER = "./input"
OUTPUT_FOLDER = "./output"
MODEL_PATH = "./Models/ocr_models"

app = Flask(__name__, template_folder="templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Automatically choose device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device: {DEVICE}")

# Initialize EasyOCR Reader
print("[INFO] Initializing EasyOCR Reader...")
_reader = easyocr.Reader(
    ['en'],
    gpu=(DEVICE == "cuda"),
    verbose=True,
    download_enabled=False,
    model_storage_directory=os.path.abspath(MODEL_PATH)
)
print("[INFO] EasyOCR Reader initialized successfully.")

def process_pdf(pdf_dir, filename):
    print("[STEP] Entering process_pdf")
    pdf_path = os.path.join(pdf_dir, filename)
    print(f"[STEP] pdf_dir = {pdf_dir}")
    print(f"[STEP] filename = {filename}")
    print(f"[STEP] computed pdf_path = {pdf_path}")
    print(f"[STEP] does pdf_path exist? {os.path.exists(pdf_path)}")
    print(f"[STEP] is pdf_path a file? {os.path.isfile(pdf_path)}")
    print(f"[STEP] is pdf_dir a directory? {os.path.isdir(pdf_dir)}")

    pdf_path = os.path.join(pdf_dir, filename)
    image_dictionary = get_images_from_bounding_boxes(pdf_path)

    print(f"[STEP] Number of extracted bounding box images: {len(image_dictionary)}")

    if not image_dictionary:
        return {"error": "No bounding box images found."}

    detection_time = time.time()
    page_information = defaultdict(lambda: defaultdict(list))
    for item in image_dictionary:
        page = item['page']
        cls = int(item['class_id'])
        img = item['final_image']
        page_information[page][cls].append(img)

    results = []
    for page, classes in page_information.items():
        for cls, imgs in classes.items():
            if cls == 0:
                continue
            for img in imgs:
                text_list = _reader.readtext(img, detail=0)
                text = " ".join(text_list).strip()
                results.append((cls, text, page))

    results = sorted(results, key=lambda x: x[2])
    output = {}
    title_found = False
    for cls, text, page in results:
        if cls == 3 and not title_found:
            output = {'title': text, 'outline': []}
            title_found = True
        elif title_found:
            if cls == 1:
                output['outline'].append({'level': 'H1', 'text': text, 'page': page})
            elif cls == 2:
                output['outline'].append({'level': 'H2', 'text': text, 'page': page})

    final_json = {"title": output.get("title"), "outline": output.get("outline", [])}
    output_file_path = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(filename)[0]}.json")
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=4, ensure_ascii=False)

    print("[INFO] JSON Output:")
    print(json.dumps(final_json, indent=4, ensure_ascii=False))

    processing_time = time.time() - detection_time
    return {
        "json_path": output_file_path,
        "processing_time": processing_time,
        "detection_time": detection_time,
        "ocr_time": processing_time,
        "result": final_json
    }

# ---------- Routes ----------
@app.route("/")
def home():
    print("[INFO] Home route accessed.")
    return render_template("index.html")

@app.route("/extract_outline", methods=["POST"])
def extract_outline():
    print("[INFO] Extract outline endpoint hit.")
    if "file" not in request.files:
        print("[ERROR] No file part in the request.")
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        print("[ERROR] No selected file.")
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    print(f"[INFO] File saved to: {file_path}")

    result = process_pdf(app.config["UPLOAD_FOLDER"], filename)

    if "error" in result:
        print(f"[ERROR] {result['error']}")
        return jsonify({"error": result["error"]}), 500

    response_data = {
        "title": result["result"].get("title", None),
        "message": "Outline extracted successfully",
        "json_path": result["json_path"],
        "processing_time": result["processing_time"],
        "detection_time": result["detection_time"],
        "ocr_time": result["ocr_time"],
        "outline": result["result"].get("outline", [])
    }
    print("[INFO] Returning response...")
    return jsonify(response_data)

# ---------- Main ----------
if __name__ == "__main__":
    print("[INFO] Starting Flask server at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
# import torch
# print(torch.cuda.is_available())