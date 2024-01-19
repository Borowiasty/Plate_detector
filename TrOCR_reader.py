import cv2
import torch 
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

class TrOCR_reader_class:
    def __init__(self, model_size= 'large', whitelist= "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
        self.device = torch.device('cuda' if torch.cuda.is_available else 'cpu')                                                        #zadeklarowanie GPU
        self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-' + model_size + '-printed')                                   #small\base\large    automatycznie powinien zacząć się pobierać
        self.model= VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-' + model_size + '-printed').to(self.device)             #żeby użyć GPU    #small\base\large    automatycznie powinien zacząć się pobierać
        self.allowed = whitelist 
        self.result_tr = []

    def TrOCR(self, image):
        pixel_values = self.processor(image, return_tensors='pt').pixel_values.to(self.device)
        generated_ids = self.model.generate(pixel_values)
        text_tr = self.processor.batch_decode(generated_ids, skip_special_tokens = True)[0]
        self.result_tr.append(text_tr)
        return self.result_tr

    def Whitelist_filter(self, list, allowed):
        result = []
        for res in list:
            filtered  = ''.join(filter(lambda char: char in allowed, res))
            result.append(filtered)
        return result

    def upper(self, list):
        return[odczyt.upper() for odczyt in list]

    def text_from_image(self, image):
        dimensions = image.shape
        cropped = image[:,int(dimensions[1]/12):int(dimensions[1])]
        self.TrOCR(cropped)
        result_tr_up = self.upper(self.result_tr)
        result_tr_filtr = self.Whitelist_filter(result_tr_up, self.allowed)

        self.result_tr = []
        return(result_tr_filtr)