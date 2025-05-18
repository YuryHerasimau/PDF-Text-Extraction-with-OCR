class OCRProcessorError(Exception):
    """Базовое исключение для ошибок обработки OCR"""

    pass


class UnsupportedLanguageError(OCRProcessorError):
    """Исключение для неподдерживаемых языков"""

    pass


class PDFProcessingError(OCRProcessorError):
    """Исключение для ошибок обработки PDF"""

    pass
