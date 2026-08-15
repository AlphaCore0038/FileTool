import os
import tempfile
from pathlib import Path

from .helpers import docx_to_html, html_to_pdf, page_html, resolve_output_path
from .pdf import _page_count, pdf_to_images


def _docx_html(src):
    return docx_to_html(src)


def docx_to_txt(src, out):
    from docx import Document

    doc = Document(src)
    lines = [p.text for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(lines)
    Path(out).write_text(text + "\n", encoding="utf-8")


def docx_to_md(src, out):
    import mammoth

    with open(src, "rb") as f:
        result = mammoth.convert_to_markdown(f)
    Path(out).write_text(result.value, encoding="utf-8")


def docx_to_html_handler(src, out):
    Path(out).write_text(page_html(_docx_html(src)), encoding="utf-8")


def docx_to_pdf(src, out):
    html_to_pdf(page_html(_docx_html(src)), out)


def _docx_to_images(src, target_fmt, on_conflict=None):
    fd, tmp = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        html_to_pdf(page_html(_docx_html(src)), tmp)
        n = _page_count(tmp)
        paths = [
            resolve_output_path(src, target_fmt, on_conflict=on_conflict, suffix=f"_page{i + 1}")
            for i in range(n)
        ]
        pdf_to_images(tmp, paths, target_fmt)
        return paths
    finally:
        Path(tmp).unlink(missing_ok=True)


def _image_handler(target_fmt):
    def handler(src, out, on_conflict=None):
        return _docx_to_images(src, target_fmt, on_conflict=on_conflict)

    return handler


HANDLERS = {
    ("DOCX", "PDF"): docx_to_pdf,
    ("DOCX", "TXT"): docx_to_txt,
    ("DOCX", "MD"): docx_to_md,
    ("DOCX", "HTML"): docx_to_html_handler,
    ("DOCX", "JPG"): _image_handler("JPG"),
    ("DOCX", "PNG"): _image_handler("PNG"),
}