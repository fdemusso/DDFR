import hashlib
import logging
import pillow_heif as heif
import os
from PIL import Image
from app.config import path_settings
logger = logging.getLogger(__name__)

class ImgValidation:

    def __init__(self, path):
        self.path = None
        self.name = None
        self.ext = None
        self.hash = None
        self.normalize_img(path)


    @property
    def is_valid(self):
        return self.path is not None and self.name is not None and self.ext is not None and self.hash is not None 

    
    @staticmethod
    def ConvertAnyToPng(path, name, ext):
        ext = ext.lower()
        filepng = f"{path_settings.imgsfolder}/{name}.png"

        if ext == ".png" and filepng == path:
            return path

        # Registrazione HEIC (solo se serve)
        if ext == ".heic":
            heif.register_heif_opener()

        # Formati supportati
        supported_ext = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".heic"]

        if ext not in supported_ext:
            logger.error("Formato non supportato per la conversione.")
            return None

        try:
            img = Image.open(path)
            img.save(filepng, "PNG")
        except Exception as e:
            logger.error(f"Errore durante la conversione: {e}")
            return None

        # Provo a rimuovere l'originale
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.error(f"Errore durante la rimozione del file originale: {e}")

        return filepng

    @staticmethod
    def validate_png(path):
        if path is None or not os.path.exists(path):
            return False  
        name, ext = os.path.splitext(path)
        if(ext == "png" ):
            return True
        return False

    @staticmethod
    def hash_img(path):
        if not ImgValidation.validate_png(path):
            return None
        
        img_hash = hashlib.md5(Image.open(path).tobytes())
        return img_hash.hexdigest()
    

    def normalize_img(self, path):

        if not os.path.exists(path):
            return False
        
        name, ext = os.path.splitext(path)
        filepng = ImgValidation.ConvertAnyToPng(path, name, ext)
        if ImgValidation.validate_png(filepng):
            hash = ImgValidation.hash_img(filepng)
            name, ext = os.path.splitext(filepng)
            if hash is not None:
                self.path = filepng
                self.name = name
                self.ext = ext
                self.hash = hash
                return True
        return False
    
    def compare_img(self, path):
        img = ImgValidation(path)
        if img.is_valid and (self.hash == img.hash):
            return True

        return False






