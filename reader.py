import textract
from textract.exceptions import ExtensionNotSupported
from image_classify import classify_image
from pathutils import is_img

class FileProcessor:

    def __init__(self, face_manager):
            self.face_manager = face_manager

    def read_text(self, f):
        try:
            text = textract.process(f, encoding='utf-8').decode('utf-8')
        except ExtensionNotSupported:
            text = ''
        if is_img(f):
            self.face_manager.submit([f])
            relevant_classes = classify_image(f)
            if relevant_classes:
                return text, ' '.join(relevant_classes)
        return text, None