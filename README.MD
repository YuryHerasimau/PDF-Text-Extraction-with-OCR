# Извлечение текста из PDF с помощью OCR
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Описание

Этот проект предоставляет инструмент для извлечения текста из PDF-документов с использованием OCR (оптического распознавания символов). Поддерживаются как сканированные PDF (изображения), так и PDF с текстовым слоем.

## Особенности

- Поддержка многоязычного распознавания (Tesseract OCR)
- Конвертация PDF в изображения с помощью pdf2image
- Сохранение результатов в JSON с сохранением структуры документа
- Гибкая настройка языков распознавания
- Логирование процесса обработки

## Установка

### Обязательные компоненты
- Python 3.7+
- Tesseract OCR
- Poppler (для конвертации PDF)

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

### Windows
1. **Tesseract**:
   - Скачайте с [официального сайта](https://github.com/UB-Mannheim/tesseract/wiki)
   - Установите в `C:\Program Files\Tesseract-OCR`
   - Добавьте в PATH: `C:\Program Files\Tesseract-OCR`

2. **Poppler**:
   - Скачайте [здесь](https://github.com/oschwartz10612/poppler-windows/releases/)
   - Добавьте в PATH папку `bin`

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-rus poppler-utils
```

## Как использовать

Запустите и укажите путь к PDF:
```bash
python main.py
```

## Формат результатов

Пример вывода:
```json
{
  "pdf_path": "doc.pdf",
  "pages": [
    {
      "page_number": 1,
      "text": "Распознанный текст...",
      "status": "success"
    }
  ],
  "languages": ["rus", "eng"],
  "status": "success",
  "page_count": 1
}
```

## Ошибки и обработка исключений

Классы исключений:

- `OCRProcessorError`: Базовый класс ошибок
- `UnsupportedLanguageError`: Неподдерживаемый язык
- `PDFProcessingError`: Ошибка обработки PDF

Система сообщит о проблемах:
- Неправильный формат PDF
- Отсутствие нужных языков
- Проблемы с зависимостями
- Ошибки доступа к файлам

## Логирование

Пример работы:
```bash
2025-05-17 15:25:38,966 - INFO - Конвертация PDF в изображения: input/document.pdf
2025-05-17 15:25:45,741 - INFO - Обработана страница 1/4
2025-05-17 15:25:49,567 - INFO - Обработана страница 2/4
2025-05-17 15:25:54,058 - INFO - Обработана страница 3/4
2025-05-17 15:25:56,819 - INFO - Обработана страница 4/4
2025-05-17 15:25:56,827 - INFO - Результаты сохранены в output/result_document_eng_rus.json
```

## Тестирование

Запустите тесты:
```bash
pytest tests/ -v
```

Пример работы:
```bash
collected 18 items

tests/test_ocr_processor.py::test_init_with_empty_languages PASSED                                                     [  5%]
tests/test_ocr_processor.py::test_invalid_pdf_path PASSED                                                              [ 11%]
tests/test_ocr_processor.py::test_init_with_invalid_languages PASSED                                                   [ 16%] 
tests/test_ocr_processor.py::test_pdf_to_images_success PASSED                                                         [ 22%]
tests/test_ocr_processor.py::test_pdf_to_images_invalid_path PASSED                                                    [ 27%]
tests/test_ocr_processor.py::test_extract_text_with_tesseract PASSED                                                   [ 33%]
tests/test_ocr_processor.py::test_extract_text_with_tesseract_from_custom_image PASSED                                 [ 38%]
tests/test_ocr_processor.py::test_extract_text_with_tesseract_failure PASSED                                           [ 44%]
tests/test_ocr_processor.py::test_extract_text_with_tesseract_error PASSED                                             [ 50%]
tests/test_ocr_processor.py::test_process_pdf_success PASSED                                                           [ 55%]
tests/test_ocr_processor.py::test_process_pdf_success_with_custom_blank_pdf PASSED                                     [ 61%]
tests/test_ocr_processor.py::test_process_pdf_failure PASSED                                                           [ 66%]
tests/test_ocr_processor.py::test_process_pdf_failure_with_custom_corrupted_pdf PASSED                                 [ 72%]
tests/test_ocr_processor.py::test_process_pdf_empty PASSED                                                             [ 77%]
tests/test_ocr_processor.py::test_save_to_json PASSED                                                                  [ 83%]
tests/test_ocr_processor.py::test_save_to_json_invalid_data PASSED                                                     [ 88%]
tests/test_ocr_processor.py::test_pdf_to_images_poppler_error PASSED                                                   [ 94%]
tests/test_ocr_processor.py::test_validate_pdf_path_invalid_size PASSED                                                [100%]
```