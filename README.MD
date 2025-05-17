# PDF Text Extraction with OCR
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

### Общие требования (для всех ОС)

- Python 3.7+
- Tesseract OCR (установить отдельно)
- Poppler (для конвертации PDF в изображения)

1. Установите зависимости Python:
```bash
pip install -r requirements.txt
```

### Для Windows

#### 1. Установка Tesseract OCR

1. Скачайте установщик Tesseract для Windows:  
   https://github.com/UB-Mannheim/tesseract/wiki

2. Запустите установщик. Рекомендуемые параметры:
   - Путь установки: `C:\Program Files\Tesseract-OCR`
   - Обязательно отметьте установку дополнительных языков (включая русский)

3. После установки добавьте путь к Tesseract в системную переменную PATH:
   - Путь для добавления: `C:\Program Files\Tesseract-OCR`

4. Установите языковые данные для русского (если не установили через установщик):
   - Скачайте `rus.traineddata` с https://github.com/tesseract-ocr/tessdata
   - Поместите файл в `C:\Program Files\Tesseract-OCR\tessdata`

#### 2. Установка Poppler (для pdf2image)

1. Скачайте Poppler для Windows:  
   https://github.com/oschwartz10612/poppler-windows/releases/

2. Распакуйте архив в `C:\poppler`

3. Добавьте путь к bin в системную переменную PATH:
   - Например: `C:\poppler\poppler-23.11.0\Library\bin`

#### 3. Настройка Python

Добавьте в начало вашего скрипта (или в конфигурацию):

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Для Linux (Ubuntu/Debian)

1. Установите системные зависимости:

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-rus poppler-utils
```

2. Для дополнительных языков:

```bash
sudo apt install tesseract-ocr-all
```

## Использование

```bash
python main.py
```

## Структура выходного JSON

```json
{
  "pdf_path": "path/to/document.pdf",
  "languages": ["eng", "rus"],
  "page_count": 4,
  "status": "success",
  "pages": [
    {
      "page_number": 1,
      "text": "...распознанный текст...",
      "status": "success"
    },
    ...
  ]
}
```

##  Ошибки и обработка исключений

Классы исключений:

- `OCRProcessorError`: Базовый класс ошибок
- `UnsupportedLanguageError`: Неподдерживаемый язык
- `PDFProcessingError`: Ошибка обработки PDF

## Логирование

Программа ведет лог с уровнем INFO. Пример вывода:
```log
2025-05-17 15:25:38,966 - INFO - Конвертация PDF в изображения: input/document.pdf
2025-05-17 15:25:45,741 - INFO - Обработана страница 1/4
2025-05-17 15:25:49,567 - INFO - Обработана страница 2/4
2025-05-17 15:25:54,058 - INFO - Обработана страница 3/4
2025-05-17 15:25:56,819 - INFO - Обработана страница 4/4
2025-05-17 15:25:56,827 - INFO - Результаты сохранены в output/result_document_eng_rus.json
2025-05-17 15:25:56,827 - INFO - Обработка завершена успешно
```
