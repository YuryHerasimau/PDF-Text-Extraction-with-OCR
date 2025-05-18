import logging
from src.ocr_processor import PDFOCRProcessor


def main():
    """Точка входа для CLI использования."""
    try:
        processor = PDFOCRProcessor(["eng", "rus"])
        input_pdf = input("Введите путь к PDF-файлу: ").strip()
        result = processor.process_pdf(input_pdf)
        processor.save_to_json(result)
    except Exception as e:
        logging.error(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
