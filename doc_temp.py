import faiss
import os
from sentence_transformers import SentenceTransformer
import timeit
from pdf2image import convert_from_path
import pytesseract
import numpy as np


start_date = timeit.timeit()
index = faiss.IndexFlatL2(384)
pt= r'C:\Users\os\Desktop\doc search\poppler-24.08.0\Library\bin'

model = SentenceTransformer('paraphrase-MiniLM-L6-v2') #all-MiniLM-L6-v2
d = {}

for i in os.listdir(r'C:\Users\os\Desktop\doc search\\'):
    if i.endswith('.pdf'):
        pages = convert_from_path(i, dpi=300, poppler_path = pt) # dpi can be adjusted for better accuracy
        
        extracted_text = ''
        for page in pages:
            text = pytesseract.image_to_string(page)
            extracted_text += text + '\n'

        embedding = model.encode(extracted_text)
        faiss_index = index.ntotal
        index.add(np.array([embedding]))
        d[faiss_index] = i
    print('one done')

print(d)
find = "opencv certificate"
search = model.encode(find)
D, I = index.search(np.array([search]), k=2)
print(D, I)
    

