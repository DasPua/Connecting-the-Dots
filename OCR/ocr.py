import PIL as image
from concurrent.futures import ProcessPoolExecutor
import easyocr
import os

model_path = "./Models/ocr_models"

def ocr(page_image):
    reader = easyocr.Reader(
        ['en'],
        gpu=False,
        verbose=False,
        download_enabled=False,
        model_storage_directory=os.path.abspath(model_path)
    )
    return reader.readtext_batched(page_image,batch_size=64, detail=0)

# def batch_ocr(cropped_images):
#     P = Process(target = ocr, args=(cropped_images))
#     P.start()
#     P.join()
        

def batch_ocr(images,_init_reader,_ocr_worker, max_workers=8):
    with ProcessPoolExecutor(max_workers=max_workers, initializer=_init_reader) as executor:
        results = list(executor.map(_ocr_worker, images))
    return results

def modified_parallel_ocr(tasks, _init_reader, _modified_ocr_worker, max_workers=8):
    
    if tasks is None : return []
    with ProcessPoolExecutor(max_workers = max_workers, initializer=_init_reader) as executor:
        results = executor.map(_modified_ocr_worker, tasks)
    return results
        