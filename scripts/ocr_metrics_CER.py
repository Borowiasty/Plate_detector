import numpy as np
import pandas as pd
import easyocr
import pytesseract
from PIL import Image
import Levenshtein

#INICJALIZACJA ZMIENNYCH
reader = easyocr.Reader(['en'], gpu = True)  
custom_config = r"--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- " 
allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- "  
file = pd.read_csv('wyrazne.csv')
result_tess = []
result_easy = []
result_easy_filtr = []
numeros = []
total_distance_tess = 0                                                  
total_length_tess = 0
total_distance_easy = 0                                                  
total_length_easy = 0

#ODCZYT PRZEZ TESSERACT OCR ORAZ EASY OCR
for index, row in file.iterrows():
    image_path = row['PATH']
    with Image.open(image_path) as img:
        text_tess = pytesseract.image_to_string(img, config = custom_config)
        result_tess.append(text_tess)

        #konwersja obrazu na numpy array dla easy ocr 
        img_array = np.array(img)
        text_easy = reader.readtext(img_array)
        for (bbox, text, prob) in text_easy:
            result_easy.append(text)

#ZAMIANA LITER NA WIELKIE
def upper(list):
    return[odczyt.upper() for odczyt in list]

#FILTRACJA WYNIKÓW EASY OCR
result_easy = upper(result_easy)
for res in result_easy:
    if len(res) >= 5:
        allow = True                                             
        for char in res:
            if char not in allowed:
                allow = False

        if allow:
            result_easy_filtr.append(res)
    else:
        continue 

#ODCZYT REFERENCYJNYCH NUMERÓW
for index, row in file.iterrows():
    numer = row['NUMER']
    numeros.append(numer)

#LICZENIE CER DLA TESSERACT OCR
for ref_line, ocr_line in zip(numeros, result_tess):
    ref_line = ref_line.strip()                                 #usunięcie znaków białych
    ocr_line = ocr_line.strip()                                 #usunięcie znaków białych
    distance = Levenshtein.distance(ref_line, ocr_line)
    total_distance_tess += distance
    total_length_tess += len(ref_line)
cer_tess = (total_distance_tess / total_length_tess) * 100
print(f"CER for Tesseract OCR = {cer_tess:.2f}%")

#LICZENIE CER DLA TESSERACT OCR
for ref_line, ocr_line in zip(numeros, result_easy):
    ref_line = ref_line.strip()                                 
    ocr_line = ocr_line.strip()                                 
    distance = Levenshtein.distance(ref_line, ocr_line)
    total_distance_easy += distance
    total_length_easy += len(ref_line)
cer_easy = (total_distance_easy / total_length_easy) * 100
print(f"CER for Easy OCR = {cer_easy:.2f}%")



'''
result_easy = ['Ei', 'PL', 'CB442EP', 'PGN 325FN', 'Fold', 'Po @1', 'PO SNV18', 'Po T611', 'PGN 395Fn', 'Po13', 'Po 16W1',
                'Po T98LV', 'PO SN18', 'PO SN18', 'PojoU', 'Po 1G1Z1', 'Po 1281 V', 'Po 198LV', 'D', 'PO', 'T98LVL', 'PO', 
                '32', 'Baa', 'PO', '3125', 'Boam', 'Da', 'PO', '21SP', 'PO', 'DUP', 'PO 5hG20', 'PSR', '4708A', 'M"e NA', '4zo81',
                'PSR', 'Po 51G20', 'Ui', 'D', 'POR', 'A', 'PKR', 'Nr25', 'Pz', '1K733', 'PZ', 'K73', 'PKRN425', 'PKRN5', 'Po 6T0?5',
                'PEN 5405', 'Paa', 'DBL', '9', 'E', '35', 'TC', '935', 'I', 'PZZES', '7an', 'CMG', '034', 'Po TANS5']


result_tess = ['RPOSWC20\n', 'CB442EP\n', 'RPCN395EN\n', 'BOGN395EN\n', 'JI\n', 'POSNVIBE\n', 'EPO16171\n', 'BPGN395FNI\n', 'BPGN395EN\n', 
            'MEPO16171\n', 'APO198LV\n', 'POSNV189\n', 'FPOONV18\n', 'MPO17\n', 'M71\n', 'APOORLV\n', 'PO198LV\n', 'BP0196L\n', 'PO198LVI\n', 
            '03325\n', '03332\n', 'BPO332\n', '0332\n', '', 'P02\n', '', 'FOSH20\n', 'BPSR47084\n', 'BA708\n', 'BPSR47052\n', 'BPOSWG20\n', 'BP12\n',
            'FPO720VR\n', 'IPO-720VR\n', 'B1733\n', 'PPCRNW2\n', 'BP71K733\n', 'BP71K733\n', 'PPRRNW25\n', 'PPRRNNZ\n', 'EPO61093\n', 'EPCNS40KR\n',
            'BOGNS40KR\n', 'FPOGROO\n', 'R72P015\n', 'F1192\n', 'RY199\n', 'APZ215YS\n', 'BPZ215YS1\n', 'BCMG03U4\n', 'EPO1ANSS\n']
'''                

