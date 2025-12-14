import hashlib
import logging
import pillow_heif as heif
import os
from PIL import Image
from config import path_settings
logger = logging.getLogger(__name__)

class ImgValidation:
    """Image validation and conversion utility.

    Validates image files, converts them to PNG format, and generates
    MD5 hash for identification. Supports multiple image formats including HEIC.

    Attributes:
        path (str | None): Path to the normalized PNG image file.
        name (str | None): Image filename without extension.
        ext (str | None): File extension (always .png after normalization).
        hash (str | None): MD5 hash of the image content.

    """

    def __init__(self, path: str, delete : bool = False):
        """Initialize ImgValidation and normalize the image.

        Args:
            path (str): Path to the image file to validate.
            delete (bool): Whether to delete the original file after conversion.
                Default: False.

        """
        self.path = None
        self.name = None
        self.ext = None
        self.hash = None
        self.normalize_img(path, delete)


    @property
    def is_valid(self) -> bool:
        """Check if the image validation was successful.

        Returns:
            bool: True if all attributes (path, name, ext, hash) are set, False otherwise.

        """
        return self.path is not None and self.name is not None and self.ext is not None and self.hash is not None 

    @staticmethod
    def convert_any_to_png(path: str, name: str, ext: str, delete: bool = False) -> str | None:
        """Convert image file to PNG format.

        Converts supported image formats to PNG and saves in configured images folder.
        Supports: PNG, JPG, JPEG, BMP, TIFF, GIF, HEIC.

        Args:
            path (str): Original image file path.
            name (str): Base filename without extension.
            ext (str): Original file extension.
            delete (bool): Whether to delete original file after conversion. Default: False.

        Returns:
            str | None: Path to converted PNG file, or None if conversion fails.

        """
        ext = ext.lower()
        filepng = f"{path_settings.imgsfolder}/{name}.png"

        if ext == ".png" and filepng == path:
            return path

        if ext == ".heic":
            heif.register_heif_opener()

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

        try:
            if os.path.exists(path) and delete == True:
                os.remove(path)
        except Exception as e:
            logger.error(f"Errore durante la rimozione {path} originale: {e}")

        return filepng

    @staticmethod
    def validate_png(path: str) -> bool:
        """Validate that a file exists and has PNG extension.

        Args:
            path (str): File path to validate.

        Returns:
            bool: True if file exists and has .png extension, False otherwise.

        """
        if path is None or not os.path.exists(path):
            return False  
        name, ext = os.path.splitext(path)
        if ext.lower() == ".png":
            return True
        return False

    @staticmethod
    def hash_img(path: str) -> str | None:
        """Generate MD5 hash of PNG image content.

        Args:
            path (str): Path to PNG image file.

        Returns:
            str | None: MD5 hash hexdigest if valid PNG, None otherwise.

        """
        if not ImgValidation.validate_png(path):
            return None
        
        img_hash = hashlib.md5(Image.open(path).tobytes())
        return img_hash.hexdigest()

    def normalize_img(self, path: str, delete: bool) -> bool:
        """Normalize image: convert to PNG, validate, and generate hash.

        Processes image file through conversion, validation, and hashing pipeline.
        Sets instance attributes (path, name, ext, hash) on success.

        Args:
            path (str): Path to image file to normalize.
            delete (bool): Whether to delete original file after conversion.

        Returns:
            bool: True if normalization successful, False otherwise.

        """
        if not os.path.exists(path):
            return False
        
        if delete is None:
            delete = False
        
        filename_with_ext = os.path.basename(path)
        name, ext = os.path.splitext(filename_with_ext)
        filepng = ImgValidation.convert_any_to_png(path, name, ext, delete)
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
    
    def compare_img(self, path: str) -> bool:
        """Compare this image with another image file by hash.

        Args:
            path (str): Path to image file to compare with.

        Returns:
            bool: True if images have the same MD5 hash, False otherwise.

        """
        if not self.is_valid :
            logger.warning(f"{self.path} non è un percorso valido")
            return False
        
        img = ImgValidation(path)
        if img.is_valid and (self.hash == img.hash):
            return True
        return False






