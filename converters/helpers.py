from pathlib import Path

from . import EXT_TO_FORMAT, FORMAT_TO_EXT


class CancelledError(Exception):
    """Raised when the user cancels a conversion (e.g. conflict dialog)."""


def detect_format(path):
    """Return the canonical source format for a file path, or None if unsupported."""
    p = Path(path)
    fmt = EXT_TO_FORMAT.get(p.suffix.lower())
    if fmt == "PDF":
        try:
            with open(p, "rb") as f:
                head = f.read(5)
            if not head.startswith(b"%PDF"):
                return None
        except OSError:
            return None
    return fmt


def get_output_dir(source_path):
    """Return (and create) the output/ subfolder next to the source file."""
    out_dir = Path(source_path).parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def page_image_paths(source_path, target_fmt, n_pages):
    """Return the list of output paths for a multi-page image conversion."""
    return [
        resolve_output_path(source_path, target_fmt, suffix=f"_page{i + 1}")
        for i in range(n_pages)
    ]


def resolve_output_path(source_path, target_fmt, on_conflict=None, suffix=""):
    """Build an output path inside the output/ folder.

    on_conflict(path) must return one of:
        "overwrite" -> use the existing path as-is
        "rename"    -> pick the next free "name (1)" path
        "cancel"    -> raise CancelledError
    If on_conflict is None, conflicts are silently renamed.
    """
    out_dir = get_output_dir(source_path)
    base = Path(source_path).stem + suffix
    ext = FORMAT_TO_EXT[target_fmt]
    candidate = out_dir / f"{base}{ext}"
    counter = 1
    while candidate.exists():
        if on_conflict is None:
            choice = "rename"
        else:
            choice = on_conflict(candidate)
        if choice == "overwrite":
            return candidate
        if choice == "cancel":
            raise CancelledError()
        candidate = out_dir / f"{base} ({counter}){ext}"
        counter += 1
    return candidate


def page_html(body):
    """Wrap an HTML fragment into a full printable HTML document."""
    return (
        "<!DOCTYPE html>\n<html><head><meta charset='utf-8'><title>Document</title>"
        "<style>body{font-family:Georgia,serif;font-size:12pt;margin:2cm}"
        "pre{font-family:Consolas,monospace;white-space:pre-wrap}</style></head>"
        f"<body>{body}</body></html>\n"
    )


def html_to_pdf(html, out_path):
    """Convert an HTML string to a PDF file using xhtml2pdf."""
    from xhtml2pdf import pisa

    with open(out_path, "wb") as f:
        result = pisa.CreatePDF(html, dest=f)
    if result.err:
        raise RuntimeError("Failed to generate PDF from HTML")


def docx_to_html(src_path):
    """Extract the HTML body of a DOCX file using mammoth."""
    import mammoth

    with open(src_path, "rb") as f:
        result = mammoth.convert_to_html(f)
    return result.value


def html_to_docx(html, out_path):
    """Build a DOCX file from an HTML string using htmldocx."""
    from docx import Document
    from htmldocx import HtmlToDocx

    document = Document()
    HtmlToDocx().add_html_to_document(html, document)
    document.save(out_path)
