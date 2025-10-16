from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
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

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = FastAPI(title="PDF Outline Extractor API", version="1.0")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional templates for quick manual testing
app.mount("/static", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------- Initialize OCR ---------- #
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device: {DEVICE}")

print("[INFO] Initializing EasyOCR Reader...")
_reader = easyocr.Reader(
    ['en'],
    gpu=(DEVICE == "cuda"),
    verbose=True,
    download_enabled=False,
    model_storage_directory=os.path.abspath(MODEL_PATH)
)
print("[INFO] EasyOCR Reader initialized successfully.")


# ---------- Core PDF Processing Function ---------- #
def process_pdf(pdf_dir, filename):
    print("[STEP] Entering process_pdf")
    pdf_path = os.path.join(pdf_dir, filename)
    print(f"[STEP] computed pdf_path = {pdf_path}")

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


# ---------- Routes ---------- #
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Optional HTML test page"""
    print("[INFO] Home route accessed.")
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/extract_outline")
async def extract_outline(file: UploadFile = File(...)):
    """Main endpoint for outline extraction"""
    print("[INFO] Extract outline endpoint hit.")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    print(f"[INFO] File saved to: {file_path}")

    result = process_pdf(UPLOAD_FOLDER, filename)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    response_data = {
        "title": result["result"].get("title", None),
        "message": "Outline extracted successfully",
        "json_path": result["json_path"],
        "processing_time": result["processing_time"],
        "detection_time": result["detection_time"],
        "ocr_time": result["ocr_time"],
        "outline": result["result"].get("outline", [])
    }

    return JSONResponse(content=response_data)


# ---------- Entry Point ---------- #
if __name__ == "__main__":
    import uvicorn
    print("[INFO] Starting FastAPI server at http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
