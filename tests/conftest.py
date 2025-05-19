import pytest
from src.ocr_processor import PDFOCRProcessor


@pytest.fixture
def ocr_processor():
    """Создаем экземпляр процессора OCR """
    return PDFOCRProcessor(languages=["eng"])

@pytest.fixture
def sample_pdf(tmp_path):
    """Создаем минимальный PDF с одной страницей"""
    pdf_path = tmp_path / "sample.pdf"

    from PyPDF2 import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return pdf_path

@pytest.fixture
def sample_image(tmp_path):
    """Создаем тестовое изображение с текстом"""
    img_path = tmp_path / "sample.png"

    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (200, 50), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Test Text", fill=(0, 0, 0))
    img.save(img_path)
    return img_path