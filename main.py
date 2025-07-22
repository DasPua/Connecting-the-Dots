from Preprocessing import get_images_from_bounding_boxes
import easyocr
from OCR import batch_ocr, ocr, modified_parallel_ocr
import time
import os
from collections import defaultdict
import json

start_time = time.time()
pdfs_path = './input'
model_path = "./Models/ocr_models"
_reader = None

def _init_reader():
    global _reader
    _reader = easyocr.Reader(
        ['en'],
        gpu=False,
        verbose=False,
        download_enabled=False,
        model_storage_directory=os.path.abspath(model_path)
    )

def _ocr_worker(image):
    global _reader
    if _reader is None:
        _init_reader()
    return _reader.readtext_batched(image,batch_size=128, detail = 0)

def _modified_ocr_worker(tasks):
    cls, img , page  = tasks
    global _reader
    if _reader is None:
        _init_reader()
    results =  _reader.readtext_batched(img, batch_size=128, detail=0)
    results = " ".join(results[0])
    results = results.strip().lower()
    return (cls, results, page)

def main() :
    print("time taken for detection: ", detection_time)
    print("time taken for ocr: ", time.time()-start_time-detection_time)

if __name__ == "__main__":
    image_dictionary = get_images_from_bounding_boxes(pdfs_path)
    detection_time = time.time() - start_time
    page_information = defaultdict(lambda : defaultdict(list))
    for item in image_dictionary:
        page = item['page']
        cls  = int(item['class_id'])
        img  = item['final_image']
        page_information[page][cls].append(img)
        
    text_information = defaultdict(lambda : defaultdict(list))
    class_map = {'0' : 'Content', '1' : 'Heading', '2' : 'Subheading', '3' : 'Title'}
    check_count = defaultdict(lambda : defaultdict(int))
    output = []
    
    tasks = []
    for page, classes in page_information.items():
        flag = False
        for cls, imgs in classes.items():
            if cls==0 : continue
            for img in imgs:
                tasks.append((cls, img, page))
            
    results = modified_parallel_ocr(tasks, _init_reader, _modified_ocr_worker, max_workers = 8)
    
    results = sorted(results, key=lambda x: x[2])
    
    flag = False
    
    for cls, text, page in results :
        if cls == 3:
            output.append({'title': text, 'outline': []})
            flag = False
        elif cls == 2 and flag:
            output[-1]['outline'].append({'h2': text, 'page': page})
        else:
            output[-1]['outline'].append({'h1': text, "page": page})
            flag = True
            
    # json_output = json.dumps(output, indent=4)
    # print(json_output)
    output_file_path = os.path.join(os.path.abspath('./output'), "results.json")
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"JSON saved to {os.path.abspath(output_file_path)}")
    main()