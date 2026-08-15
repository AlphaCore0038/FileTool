PIL_FORMAT = {"PNG": "PNG", "JPG": "JPEG", "WEBP": "WEBP", "PDF": "PDF"}


def convert_image(src_path, out_path, target_fmt):
    """Convert a JPG/PNG/WEBP image to another image format or a PDF page."""
    from PIL import Image

    with Image.open(src_path) as img:
        if target_fmt == "JPG" and img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        if target_fmt == "PDF":
            img.save(out_path, format="PDF", resolution=100.0)
        else:
            img.save(out_path, format=PIL_FORMAT[target_fmt])


def compress_image(src_path, out_path, quality=70):
    """Re-encode an image as JPEG at the given quality (0-100)."""
    from PIL import Image

    with Image.open(src_path) as img:
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        img.save(out_path, format="JPEG", quality=quality, optimize=True)


HANDLERS = {
    ("JPG", "PNG"): lambda s, o: convert_image(s, o, "PNG"),
    ("JPG", "WEBP"): lambda s, o: convert_image(s, o, "WEBP"),
    ("JPG", "PDF"): lambda s, o: convert_image(s, o, "PDF"),
    ("PNG", "JPG"): lambda s, o: convert_image(s, o, "JPG"),
    ("PNG", "WEBP"): lambda s, o: convert_image(s, o, "WEBP"),
    ("PNG", "PDF"): lambda s, o: convert_image(s, o, "PDF"),
    ("WEBP", "JPG"): lambda s, o: convert_image(s, o, "JPG"),
    ("WEBP", "PNG"): lambda s, o: convert_image(s, o, "PNG"),
    ("WEBP", "PDF"): lambda s, o: convert_image(s, o, "PDF"),
}
