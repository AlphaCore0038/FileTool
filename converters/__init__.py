EXT_TO_FORMAT = {
    ".pdf": "PDF",
    ".docx": "DOCX",
    ".pptx": "PPTX",
    ".txt": "TXT",
    ".md": "MD",
    ".markdown": "MD",
    ".html": "HTML",
    ".htm": "HTML",
    ".jpg": "JPG",
    ".jpeg": "JPG",
    ".png": "PNG",
    ".webp": "WEBP",
    ".xlsx": "XLSX",
    ".csv": "CSV",
}

FORMAT_TO_EXT = {
    "PDF": ".pdf",
    "DOCX": ".docx",
    "PPTX": ".pptx",
    "TXT": ".txt",
    "MD": ".md",
    "HTML": ".html",
    "JPG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "XLSX": ".xlsx",
    "CSV": ".csv",
}

VALID_TARGETS = {
    "PDF": ["DOCX", "PPTX", "TXT", "MD", "HTML", "JPG", "PNG", "WEBP"],
    "DOCX": ["PDF", "TXT", "MD", "HTML", "JPG", "PNG"],
    "PPTX": ["PDF", "TXT", "MD", "JPG", "PNG"],
    "TXT": ["PDF", "DOCX", "MD", "HTML"],
    "MD": ["PDF", "DOCX", "TXT", "HTML"],
    "HTML": ["PDF", "DOCX", "TXT", "MD"],
    "JPG": ["PNG", "WEBP", "PDF"],
    "PNG": ["JPG", "WEBP", "PDF"],
    "WEBP": ["JPG", "PNG", "PDF"],
    "XLSX": ["CSV", "TXT", "HTML"],
    "CSV": ["XLSX", "TXT", "HTML"],
}

HANDLERS = {}

from . import images, spreadsheet, text_md_html  # noqa: E402

HANDLERS.update(images.HANDLERS)
HANDLERS.update(spreadsheet.HANDLERS)
HANDLERS.update(text_md_html.HANDLERS)
