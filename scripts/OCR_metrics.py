import pandas as pd
import easyocr
import pytesseract
from PIL import Image
import Levenshtein
import cv2
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

device = torch.device('cuda' if torch.cuda.is_available else 'cpu')
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-large-printed')                              #small\base\large
model= VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-large-printed').to(device)             #small\base\large
reader = easyocr.Reader(['en'], gpu = True)  
custom_config = r"--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"    #best psm: 8 same as 13
allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  
file = pd.read_csv('Rejestracje.csv')
result_tess = []
result_easy = []
result_tr = []
full_text_easy = []
numeros = []
bbox_area = 0
text_easy = []



'''
addition fine tuning for TrOCR models, for future use
model.config.early_stopping = True
model.config.max_length = 8
model.config.no_repeat_ngram_size = 10
model.config.length_penalty = 20.0
model.config.num_beams = 3
'''


def Tesseract_OCR (image):
    text_tess = pytesseract.image_to_string(image, config = custom_config)
    result_tess.append(text_tess)
    return result_tess

def Easy_OCR(image):
    text_easy = reader.readtext(image)
    filtered_text = [word for word in text_easy if Bbox_area(word[0]) > 150]    #area threshold = 150
    full_text = ' '.join([word[1] for word in filtered_text])                   #joining filtered text
    result_easy.append(full_text)
    return result_easy

def Bbox_area(bbox):
    return (bbox[2][0] - bbox[0][0]) * (bbox[2][1] - bbox[0][1])

def TrOCR(image):
    pixel_values = processor(image, return_tensors='pt').pixel_values.to(device)
    generated_ids = model.generate(pixel_values)
    text_tr = processor.batch_decode(generated_ids, skip_special_tokens = True)[0]
    result_tr.append(text_tr)
    return result_tr

def Whitelist_filter(list, allowed):
    result = []
    for res in list:
        filtered  = ''.join(filter(lambda char: char in allowed, res))
        result.append(filtered)
    return result

def upper(list):
    return[odczyt.upper() for odczyt in list]

def CER(numbers, result):
    total_distance = 0                                                  
    total_length = 0
    for ref_line, ocr_line in zip(numbers, result):
        ref_line = ref_line.strip()                                 #usunięcie znaków białych
        ocr_line = ocr_line.strip()                                 #usunięcie znaków białych
        distance = Levenshtein.distance(ref_line, ocr_line)
        total_distance += distance
        total_length += len(ref_line)
    cer = (total_distance / total_length) * 100
    return cer

#ODCZYT REFERENCYJNYCH NUMERÓW
for index, row in file.iterrows():
    numer = row['NUMER']
    numeros.append(numer)

for index, row in file.iterrows():
    image_path = row['PATH']
    img = cv2.imread(image_path)
    dimensions = img.shape
    cropped = img[:,int(dimensions[1]/12):int(dimensions[1])]

    Tesseract_OCR(cropped)
    Easy_OCR(cropped)
    TrOCR(cropped)


result_easy_up = upper(result_easy)
result_tr_up = upper(result_tr)

result_easy_filtr = Whitelist_filter(result_easy_up, allowed)
result_tr_filtr = Whitelist_filter(result_tr_up, allowed)

cer_tess = CER(numeros, result_tess)
cer_easy = CER(numeros, result_easy_filtr)
cer_tr = CER(numeros, result_tr_filtr)
print(f"CER for Tesseract OCR = {cer_tess:.2f}%")
print(f"CER for Easy OCR = {cer_easy:.2f}%")
print(f"CER for TrOCR = {cer_tr:.2f}%")
