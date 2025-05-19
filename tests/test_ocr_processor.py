import json
from unittest.mock import patch
import pdf2image
import pytest
from pathlib import Path
from PIL import Image
from src.exceptions import UnsupportedLanguageError, PDFProcessingError
from src.ocr_processor import PDFOCRProcessor


def test_init_with_empty_languages():
    with pytest.raises(ValueError, match="Список языков не может быть пустым"):
        PDFOCRProcessor(languages=[])

def test_invalid_pdf_path(ocr_processor):
    with pytest.raises(PDFProcessingError, match="Файл не найден"):
        ocr_processor.process_pdf("invalid_path.pdf")

def test_init_with_invalid_languages():
    with pytest.raises(ValueError, match="Языки должны быть списком строк"):
        PDFOCRProcessor(languages="english")
    with pytest.raises(ValueError, match="Все языки должны быть строками"):
        PDFOCRProcessor(languages=[1, 2, 3])

def test_pdf_to_images_success(ocr_processor, sample_pdf):
    images = list(ocr_processor.pdf_to_images(sample_pdf))
    assert len(images) == 1
    assert isinstance(images[0], Image.Image)

def test_pdf_to_images_invalid_path(ocr_processor):
    with pytest.raises(FileNotFoundError):
        list(ocr_processor.pdf_to_images("nonexistent.pdf"))

def test_extract_text_with_tesseract(ocr_processor, sample_image):
    # Используем реальное изображение с текстом
    img = Image.open(sample_image)
    text = ocr_processor.extract_text_with_tesseract(img)
    assert "Test Text" in text

def test_extract_text_with_tesseract_from_custom_image(ocr_processor):
    test_image_path = Path("tests/test_data/PDF-Document-ChatBot.png")
    assert test_image_path.exists(), f"Тестовое изображение не найдено: {test_image_path}"

    with Image.open(test_image_path) as img:
        # Конвертируем в RGB если нужно
        if img.mode != 'RGB':
            img = img.convert('RGB')
        text = ocr_processor.extract_text_with_tesseract(img)
        assert "chat with your pdf files" in text.lower(), (
            f"Текст не распознан. Полученный текст: {text}"
        )

def test_extract_text_with_tesseract_failure(ocr_processor):
    # Тест с пустым изображением
    img = Image.new('RGB', (100, 100))
    text = ocr_processor.extract_text_with_tesseract(img)
    assert text == ""

@patch('pytesseract.image_to_string')
def test_extract_text_with_tesseract_error(mock_tesseract, ocr_processor):
    mock_tesseract.side_effect = Exception("Tesseract error")
    img = Image.new('RGB', (100, 100))
    text = ocr_processor.extract_text_with_tesseract(img)
    assert text == ""

def test_process_pdf_success(ocr_processor, sample_pdf):
    result = ocr_processor.process_pdf(str(sample_pdf))
    assert result["status"] == "success"
    assert len(result["pages"]) == 1
    assert result["page_count"] == 1

def test_process_pdf_success_with_custom_blank_pdf(ocr_processor):
    valid_blank_pdf = Path("tests/test_data/valid.pdf")
    result = ocr_processor.process_pdf(str(valid_blank_pdf))
    assert result["status"] == "success"
    assert result["pages"][0]["text"] == ""
    assert result["pages"][0]["status"] == "empty_or_failed"
    assert len(result["pages"]) == 1
    assert result["page_count"] == 1

def test_process_pdf_failure(ocr_processor, tmp_path):
    # Создаем битый PDF
    bad_pdf = tmp_path / "bad.pdf"
    bad_pdf.write_text("Not a PDF")
    
    with pytest.raises(PDFProcessingError):
        ocr_processor.process_pdf(bad_pdf)

def test_process_pdf_failure_with_custom_corrupted_pdf(ocr_processor):
    corrupted_pdf = Path("tests/test_data/corrupted.pdf")

    with pytest.raises(PDFProcessingError) as excinfo:
        ocr_processor.process_pdf(corrupted_pdf)
    
    assert "ошибка обработки pdf" in str(excinfo.value).lower()
    assert "ошибка конвертации pdf" in str(excinfo.value).lower()

def test_process_pdf_empty(ocr_processor, tmp_path):
    # Создаем пустой PDF
    empty_pdf = tmp_path / "empty.pdf"
    empty_pdf.write_bytes(b'')
    
    with pytest.raises(PDFProcessingError) as exc_info:
        ocr_processor.process_pdf(empty_pdf)

    assert "пустой" in str(exc_info.value).lower()
    assert "pdf" in str(exc_info.value).lower()

def test_save_to_json(ocr_processor, sample_pdf, tmp_path):
    result = ocr_processor.process_pdf(str(sample_pdf))
    output_path = ocr_processor.save_to_json(result, str(tmp_path))
    
    assert output_path.exists()
    with open(output_path, 'r') as f:
        data = json.load(f)
        assert data["status"] == "success"

def test_save_to_json_invalid_data(ocr_processor):
    with pytest.raises(ValueError):
        ocr_processor.save_to_json({})

@patch('pdf2image.convert_from_path')
def test_pdf_to_images_poppler_error(mock_convert, ocr_processor, sample_pdf):
    mock_convert.side_effect = pdf2image.exceptions.PDFInfoNotInstalledError()
    with pytest.raises(PDFProcessingError, match="Poppler не установлен"):
        list(ocr_processor.pdf_to_images(sample_pdf))

def test_validate_pdf_path_invalid_size(ocr_processor, tmp_path):
    # Создаем слишком большой PDF
    big_pdf = tmp_path / "big.pdf"
    with open(big_pdf, 'wb') as f:
        f.seek(ocr_processor.config.PDF_SIZE_LIMIT + 1)
        f.write(b'0')
    
    with pytest.raises(ValueError, match="превышает"):
        ocr_processor._validate_pdf_path(big_pdf)
