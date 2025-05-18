import json
import logging
from pathlib import Path
from typing import Dict, Generator, List, Optional, Union

import pytesseract
import pdf2image
from PIL import Image

from src.exceptions import (
    OCRProcessorError,
    UnsupportedLanguageError,
    PDFProcessingError,
)
from config.settings import OCRConfig


class PDFOCRProcessor:
    """Основной класс для обработки PDF с помощью OCR."""

    def __init__(self, languages: Optional[List[str]] = None):
        """
        Инициализация процессора OCR

        :param languages: список языков для распознавания (по умолчанию английский)
        :raises OCRProcessorError: если инициализация не удалась
        """
        self._setup_logging()
        self.config = OCRConfig()
        self.languages = self._validate_input_languages(languages)
        self.tesseract_langs = "+".join(self.languages)

        try:
            self._init_tesseract()
        except Exception as e:
            self.logger.error(f"Ошибка инициализации OCR процессора: {e}")
            raise OCRProcessorError(f"Ошибка инициализации OCR процессора: {e}")
        
    def _setup_logging(self) -> None:
        """Настройка логгирования."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def _validate_input_languages(self, languages: Optional[List[str]]) -> List[str]:
        """Проверяет и возвращает список языков для OCR."""
        if languages is None:
            return self.config.DEFAULT_LANGUAGES
        
        if not isinstance(languages, list):
            raise ValueError("Языки должны быть списком строк")
        
        if not languages:
            raise ValueError("Список языков не может быть пустым")
        
        if not all(isinstance(lang, str) for lang in languages):
            raise ValueError("Все языки должны быть строками")
    
        return languages

    def _validate_languages(self) -> None:
        """Проверяет доступность указанных языков в Tesseract"""
        try:
            available_langs = pytesseract.get_languages(config="")
            missing_langs = [
                lang for lang in self.languages if lang not in available_langs
            ]

            if missing_langs:
                raise UnsupportedLanguageError(
                    f"Следующие языки не поддерживаются: {missing_langs}."
                    f"Доступные языки: {available_langs}"
                )
        except Exception as e:
            raise OCRProcessorError(f"Ошибка проверки языков: {e}")

    def _init_tesseract(self) -> None:
        """Инициализация Tesseract OCR"""
        if Path.cwd().drive: # Проверка для Windows
            if not self.config.TESSERACT_WINDOWS_PATH.exists():
                raise OCRProcessorError(
                    f"Tesseract не найден по пути: {self.config.TESSERACT_WINDOWS_PATH}."
                    "Пожалуйста, установите Tesseract или укажите правильный путь."
                )
            pytesseract.pytesseract.tesseract_cmd = self.config.TESSERACT_WINDOWS_PATH

        try:
            pytesseract.get_tesseract_version()
            self._validate_languages()
        except Exception as e:
            raise OCRProcessorError(f"Tesseract не доступен: {e}")
        
    def _validate_pdf_path(self, pdf_path: Path) -> None:
        """Проверяет валидность PDF файла."""
        if not pdf_path.exists():
            raise FileNotFoundError(f"Файл не найден: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Файл должен быть PDF: {pdf_path}")
        if pdf_path.stat().st_size == 0:
            raise ValueError(f"Пустой PDF-файл: {pdf_path}")
        if pdf_path.stat().st_size > self.config.PDF_SIZE_LIMIT:
            raise ValueError(f"Размер PDF превышает {self.config.PDF_SIZE_LIMIT} МБ: {pdf_path}")

    def pdf_to_images(
        self,
        pdf_path: Union[str, Path],
        grayscale: bool = True,
    ) -> Generator[Image.Image, None, None]:
        """
        Конвертирует PDF в генератор изображений

        :param pdf_path: путь к PDF-файлу
        :param grayscale: конвертировать в градацию серого (по умолчанию: True)
        :return: генератор, возвращающий PIL изображения
        :raises PDFProcessingError: если конвертация не удалась
        """
        pdf_path = Path(pdf_path)
        self._validate_pdf_path(pdf_path)
                
        self.logger.info(f"Конвертация PDF в изображения: {pdf_path}")
        try:
            yield from pdf2image.convert_from_path(
                pdf_path,
                grayscale=grayscale,
            )
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
            return pytesseract.image_to_string(
                image,
                lang=self.tesseract_langs,
            ).strip()
        except Exception as e:
            self.logger.error(f"Ошибка OCR для изображения: {e}")
            return ""

    def process_pdf(self, pdf_path: str) -> Dict[str, str]:
        """
        Обрабатывает PDF файл и извлекает текст со всех страниц

        :param pdf_path: путь к PDF файлу
        :return: словарь с результатами распознавания
        :raises PDFProcessingError: если обработка не удалась
        """
        result = {
            "pdf_path": str(pdf_path),
            "pages": [],
            "languages": self.languages,
            "status": "success",
        }

        try:
            # Получаем генератор изображений
            images_gen = self.pdf_to_images(pdf_path)

            for i, image in enumerate(images_gen, start=1):
                page_text = self.extract_text_with_tesseract(image)
                result["pages"].append({
                    "page_number": i,
                    "text": page_text,
                    "status": "success" if page_text else "empty_or_failed",
                })
                self.logger.info(f"Обработана страница {i}")
            
            result["page_count"] = len(result["pages"])
            return result

        except Exception as e:
            self.logger.error(f"Ошибка обработки PDF: {e}")
            raise PDFProcessingError(f"Ошибка обработки PDF: {e}")

    def save_to_json(self, data: Dict, output_dir: Optional[str] = None) -> Path:
        """
        Сохраняет данные в JSON файл

        :param data: данные для сохранения
        :param output_dir: директория для сохранения
        :return: путь к сохранённому файлу
        :raises OCRProcessorError: если сохранение не удалось
        """
        required_keys = {"pdf_path", "languages"}
        if not required_keys.issubset(data.keys()):
            raise ValueError(f"Данные должны содержать {required_keys}")

        output_dir = Path(output_dir or self.config.DEFAULT_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_stem = Path(data["pdf_path"]).stem
        lang_suffix = "_".join(data["languages"])
        output_path = output_dir / f"result_{pdf_stem}_{lang_suffix}.json"

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.logger.info(f"Результаты сохранены в {output_path}")
            return output_path
        except Exception as e:
            raise OCRProcessorError(f"Ошибка сохранения результатов: {e}")
