import os
from typing import Dict, List, Optional
import json
import logging
from pathlib import Path
import pytesseract
import pdf2image
from PIL import Image


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class OCRProcessorError(Exception):
    """Базовое исключение для ошибок обработки OCR"""

    pass


class UnsupportedLanguageError(OCRProcessorError):
    """Исключение для неподдерживаемых языков"""

    pass


class PDFProcessingError(OCRProcessorError):
    """Исключение для ошибок обработки PDF"""

    pass


class PDFOCRProcessor:
    DEFAULT_LANGUAGES = ["eng"]

    def __init__(self, languages: Optional[List[str]] = None):
        """
        Инициализация процессора OCR

        :param languages: список языков для распознавания (по умолчанию английский)
        :raises OCRProcessorError: если инициализация не удалась
        """
        self.languages = self.DEFAULT_LANGUAGES if languages is None else languages
        self.tesseract_langs = "+".join(self.languages)

        try:
            self._init_tesseract()
            self._validate_languages()
        except Exception as e:
            logger.error(f"Ошибка инициализации OCR процессора: {e}")
            raise OCRProcessorError(f"Ошибка инициализации OCR процессора: {e}")

    def _validate_languages(self) -> None:
        """Проверяет доступность указанных языков в Tesseract"""
        try:
            available_langs = pytesseract.get_languages(config="")
            missing_langs = [
                lang for lang in self.languages if lang not in available_langs
            ]

            if missing_langs:
                raise UnsupportedLanguageError(
                    f"Следующие языки не поддерживаются: {missing_langs}. "
                    f"Доступные языки: {available_langs}"
                )
        except Exception as e:
            raise OCRProcessorError(f"Ошибка проверки языков: {e}")

    def _init_tesseract(self) -> None:
        """Инициализация Tesseract OCR"""
        if os.name == "nt":
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if not os.path.exists(tesseract_path):
                raise OCRProcessorError(
                    f"Tesseract не найден по пути: {tesseract_path}. "
                    "Пожалуйста, установите Tesseract или укажите правильный путь."
                )
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            raise OCRProcessorError(f"Tesseract не доступен: {e}")

    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Конвертирует PDF в список изображений

        :param pdf_path: путь к PDF-файлу
        :return: список изображений
        :raises PDFProcessingError: если конвертация не удалась
        """
        try:
            pdf_path = Path(pdf_path)
            print("PDF path as PurePath object:", pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"Файл не найден: {pdf_path}")
            if pdf_path.suffix.lower() != ".pdf":
                raise ValueError(f"Файл должен быть PDF: {pdf_path}")

            logger.info(f"Конвертация PDF в изображения: {pdf_path}")
            return pdf2image.convert_from_path(pdf_path)

        except pdf2image.exceptions.PDFInfoNotInstalledError:
            raise PDFProcessingError(
                "Poppler не установлен или не добавлен в PATH. "
                "Установите Poppler для работы с PDF."
            )
        except Exception as e:
            raise PDFProcessingError(f"Ошибка конвертации PDF: {e}")

    def extract_text_with_tesseract(self, image: Image.Image) -> str:
        """
        Извлекает текст с изображения с помощью Tesseract OCR

        :param image: изображение PIL
        :return: распознанный текст
        """
        try:
            # Конвертируем в grayscale для лучшего распознавания
            if image.mode != "L":
                image = image.convert("L")

            return pytesseract.image_to_string(image, lang=self.tesseract_langs).strip()
        except Exception as e:
            logger.error(f"Ошибка OCR для изображения: {e}")
            return ""

    def process_pdf(self, pdf_path: str) -> Dict[str, str]:
        """
        Обрабатывает PDF файл и извлекает текст со всех страниц

        :param pdf_path: путь к PDF файлу
        :return: словарь с результатами распознавания
        :raises PDFProcessingError: если обработка не удалась
        """
        try:
            images = self.pdf_to_images(pdf_path)
            if not images:
                raise PDFProcessingError("PDF не содержит изображений или пуст")

            result = {
                "pdf_path": str(pdf_path),
                "pages": [],
                "languages": self.languages,
                "page_count": len(images),
                "status": "success",
            }

            for i, image in enumerate(images, start=1):
                page_text = self.extract_text_with_tesseract(image)
                result["pages"].append(
                    {
                        "page_number": i,
                        "text": page_text,
                        "status": "success" if page_text else "empty_or_failed",
                    }
                )
                logger.info(f"Обработана страница {i}/{len(images)}")

            return result

        except Exception as e:
            logger.error(f"Ошибка обработки PDF: {e}")
            raise PDFProcessingError(f"Ошибка обработки PDF: {e}")

    def save_to_json(self, data: Dict) -> None:
        """
        Сохраняет данные в JSON файл

        :param data: данные для сохранения
        :raises OCRProcessorError: если сохранение не удалось
        """
        try:
            if "pdf_path" not in data or "languages" not in data:
                raise ValueError("Данные должны содержать 'pdf_path' и 'languages'")

            pdf_path = Path(data["pdf_path"])
            languages = data["languages"]

            output_filename = f"result_{pdf_path.stem}_{'_'.join(languages)}.json"
            output_path = Path("output") / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Результаты сохранены в {output_path}")
        except Exception as e:
            raise OCRProcessorError(f"Ошибка сохранения результатов: {e}")


def main():
    try:
        processor = PDFOCRProcessor()
        result = processor.process_pdf("input/da8b0f0b-cfea-40c4-b020-e0924a142f4b.pdf")
        processor.save_to_json(result)

        logger.info("Обработка завершена успешно")

    except UnsupportedLanguageError as e:
        logger.error(f"Ошибка языка: {e}")
    except PDFProcessingError as e:
        logger.error(f"Ошибка обработки PDF: {e}")
    except OCRProcessorError as e:
        logger.error(f"Ошибка OCR процессора: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)


if __name__ == "__main__":
    main()
