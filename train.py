import fitz 
import os
import easyocr

data_path = './input_files'
reader = easyocr.Reader(['en'],gpu=True)
docs = []
output_path = './output_files'
cnt = 0
for pdfs in os.listdir(os.path.abspath(data_path)):
    
    pdf_path = os.path.join(data_path, pdfs)
    pdf = fitz.open(pdf_path)
    mat = fitz.Matrix(4,4)
    
    num_pages = len(pdf)
    
    for i in range(num_pages):
        val = f'{output_path}/{cnt+1}.png'
        page_content = pdf.load_page(i)
        pix = page_content.get_pixmap(matrix = mat)
        pix.save(val)
        
        result = reader.readtext(val,detail = 0)
        print(cnt+1)
        cnt+=1
    
    pdf.close()
    