from pathlib import Path

class OCRConfig:
    """Конфигурационные параметры для OCR обработки"""
    DEFAULT_LANGUAGES = ["eng"]
    DEFAULT_OUTPUT_DIR = "output"
    TESSERACT_WINDOWS_PATH = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    PDF_SIZE_LIMIT = 100 * 1024 * 1024  # 100 МБ
