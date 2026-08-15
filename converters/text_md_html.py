from html import escape
from pathlib import Path

from .helpers import html_to_docx, html_to_pdf, page_html


def _read_text(path):
    data = Path(path).read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def _html_to_txt(html):
    import html2text

    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    h.body_width = 0
    return h.handle(html)


def _html_to_md(html):
    import html2text

    h = html2text.HTML2Text()
    h.body_width = 0
    return h.handle(html)


def _txt_to_html_body(text):
    body = "".join(f"<p>{escape(line)}</p>" for line in text.splitlines()) or "<p></p>"
    return page_html(body)


def txt_to_html(src, out):
    with open(out, "w", encoding="utf-8") as f:
        f.write(_txt_to_html_body(_read_text(src)))


def txt_to_md(src, out):
    Path(out).write_bytes(_read_text(src).encode("utf-8"))


def txt_to_docx(src, out):
    from docx import Document

    doc = Document()
    for line in _read_text(src).splitlines():
        doc.add_paragraph(line)
    doc.save(out)


def txt_to_pdf(src, out):
    html_to_pdf(_txt_to_html_body(_read_text(src)), out)


def _md_to_html(text):
    import markdown

    return markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br"])


def md_to_html(src, out):
    with open(out, "w", encoding="utf-8") as f:
        f.write(page_html(_md_to_html(_read_text(src))))


def md_to_txt(src, out):
    html = _md_to_html(_read_text(src))
    Path(out).write_text(_html_to_txt(html), encoding="utf-8")


def md_to_docx(src, out):
    html_to_docx(page_html(_md_to_html(_read_text(src))), out)


def md_to_pdf(src, out):
    html_to_pdf(page_html(_md_to_html(_read_text(src))), out)


def html_to_pdf_handler(src, out):
    html_to_pdf(Path(src).read_text(encoding="utf-8", errors="replace"), out)


def html_to_docx_handler(src, out):
    html_to_docx(Path(src).read_text(encoding="utf-8", errors="replace"), out)


def html_to_txt(src, out):
    html = Path(src).read_text(encoding="utf-8", errors="replace")
    Path(out).write_text(_html_to_txt(html), encoding="utf-8")


def html_to_md(src, out):
    html = Path(src).read_text(encoding="utf-8", errors="replace")
    Path(out).write_text(_html_to_md(html), encoding="utf-8")


HANDLERS = {
    ("TXT", "PDF"): txt_to_pdf,
    ("TXT", "DOCX"): txt_to_docx,
    ("TXT", "MD"): txt_to_md,
    ("TXT", "HTML"): txt_to_html,
    ("MD", "PDF"): md_to_pdf,
    ("MD", "DOCX"): md_to_docx,
    ("MD", "TXT"): md_to_txt,
    ("MD", "HTML"): md_to_html,
    ("HTML", "PDF"): html_to_pdf_handler,
    ("HTML", "DOCX"): html_to_docx_handler,
    ("HTML", "TXT"): html_to_txt,
    ("HTML", "MD"): html_to_md,
}
