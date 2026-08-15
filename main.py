import os
import tempfile
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

from converters import HANDLERS, VALID_TARGETS
from converters.helpers import CancelledError, detect_format, get_output_dir, resolve_output_path
from converters.images import compress_image
from converters.pdf import compress_pdf, merge_pdfs, split_pdf_every, split_pdf_ranges

BG = "#1e1e1e"
PANEL = "#252526"
SIDEBAR = "#2d2d30"
BUTTON = "#3a3d41"
ACCENT = "#0e639c"
ACCENT_HOVER = "#1177bb"
TEXT = "#e8e8e8"
MUTED = "#9d9d9d"
BORDER = "#3f3f46"

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")

MULTI_PAGE = {
    ("PDF", "JPG"), ("PDF", "PNG"), ("PDF", "WEBP"),
    ("DOCX", "JPG"), ("DOCX", "PNG"),
    ("PPTX", "JPG"), ("PPTX", "PNG"),
}

IMAGE_FORMATS = ("JPG", "PNG", "WEBP")
FILE_TYPES = [
    ("All supported", "*.pdf *.docx *.pptx *.txt *.md *.markdown *.html *.htm *.jpg *.jpeg *.png *.webp *.xlsx *.csv"),
    ("All files", "*.*"),
]

TOAST = {
    "success": "#1b5e4a",
    "error": "#8b2f2f",
    "warn": "#7a5c2e",
}


class Toaster:
    def __init__(self, root):
        self.root = root
        self.window = None

    def show(self, message, kind="success", duration=2500):
        self._destroy()
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        bg = TOAST[kind]
        win.configure(bg=bg)
        tk.Label(win, text=message, bg=bg, fg="#ffffff", font=FONT, padx=16, pady=10).pack()
        win.update_idletasks()
        x = self.root.winfo_rootx() + self.root.winfo_width() - win.winfo_width() - 16
        y = self.root.winfo_rooty() + self.root.winfo_height() - win.winfo_height() - 16
        x = min(max(x, 8), win.winfo_screenwidth() - win.winfo_width() - 8)
        y = min(max(y, 8), win.winfo_screenheight() - win.winfo_height() - 8)
        win.geometry(f"+{x}+{y}")
        win.attributes("-alpha", 0.0)
        self.window = win
        self._fade_to(1.0, lambda: self.root.after(duration, self._close))

    def _fade_to(self, target, done):
        if self.window is None:
            return
        try:
            current = self.window.attributes("-alpha")
        except tk.TclError:
            return
        if abs(current - target) < 0.01:
            done()
            return
        step = 0.1 if target > current else -0.1
        self.window.attributes("-alpha", current + step)
        self.root.after(20, lambda: self._fade_to(target, done))

    def _close(self):
        if self.window is None:
            return
        self._fade_to(0.0, self._destroy)

    def _destroy(self):
        if self.window is not None:
            try:
                self.window.destroy()
            except tk.TclError:
                pass
            self.window = None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Document Toolbox")
        self.geometry("880x580")
        self.minsize(780, 520)
        self.configure(bg=BG)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure(
            "TCombobox",
            fieldbackground=BUTTON, background=BUTTON, foreground=TEXT,
            arrowcolor=TEXT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
        )
        self.style.map("TCombobox", fieldbackground=[("readonly", BUTTON)])

        self.selected = None
        self.merge_files = []
        self.last_output = None
        self.toaster = Toaster(self)

        self._build_sidebar()
        self._build_panels()

        self._show("convert")

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=SIDEBAR, width=150)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="TOOLBOX", bg=SIDEBAR, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(pady=(18, 10))

        self.side_buttons = {}
        for tool, label in (("convert", "Convert"), ("merge", "Merge"), ("split", "Split"), ("compress", "Compress")):
            btn = tk.Button(
                sidebar, text=label, command=lambda t=tool: self._show(t),
                bg=BUTTON, fg=TEXT, activebackground=ACCENT_HOVER, activeforeground=TEXT,
                relief="flat", font=FONT, pady=10, cursor="hand2", bd=0,
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.side_buttons[tool] = btn

    def _build_panels(self):
        self.container = tk.Frame(self, bg=PANEL)
        self.container.pack(side="left", fill="both", expand=True)

        self.panels = {
            "convert": self._build_convert(),
            "merge": self._build_merge(),
            "split": self._build_split(),
            "compress": self._build_compress(),
        }

    def _panel(self, title):
        panel = tk.Frame(self.container, bg=PANEL)
        tk.Label(panel, text=title, bg=PANEL, fg=TEXT, font=FONT_TITLE).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Frame(panel, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 16))
        return panel

    def _btn(self, parent, text, command, accent=False, **kw):
        return tk.Button(
            parent, text=text, command=command,
            bg=ACCENT if accent else BUTTON, fg=TEXT,
            activebackground=ACCENT_HOVER if accent else BUTTON,
            activeforeground=TEXT, relief="flat", font=FONT_BOLD if accent else FONT,
            cursor="hand2", bd=0, **kw,
        )

    def _open_output(self):
        target = self.last_output
        if target is None and self.selected:
            target = get_output_dir(self.selected)
        if target:
            os.startfile(str(target))

    def _set_output(self, path):
        self.last_output = Path(path)
        self.open_btn.config(state="normal")

    def _build_convert(self):
        panel = self._panel("Convert Documents")

        self.zone = tk.Button(
            panel,
            text="Choose a file\n\nPDF · DOCX · PPTX · TXT · MD · HTML\nJPG · PNG · WEBP · XLSX · CSV",
            command=self._pick_file, bg=PANEL, fg=MUTED,
            activebackground=PANEL, activeforeground=TEXT,
            relief="solid", bd=1, highlightbackground=BORDER, highlightcolor=BORDER,
            highlightthickness=1, font=("Segoe UI", 12), padx=20, pady=28, cursor="hand2",
        )
        self.zone.pack(fill="x", padx=24, pady=(0, 14))

        self.file_label = tk.Label(panel, text="No file selected", bg=PANEL, fg=MUTED, font=FONT, anchor="w")
        self.file_label.pack(fill="x", padx=24)

        row = tk.Frame(panel, bg=PANEL)
        row.pack(fill="x", padx=24, pady=(14, 0))

        self.from_var = tk.StringVar(value="-")
        tk.Label(row, text="From:", bg=PANEL, fg=MUTED, font=FONT).grid(row=0, column=0, sticky="w")
        tk.Label(row, textvariable=self.from_var, bg=PANEL, fg=TEXT, font=FONT_BOLD).grid(row=0, column=1, sticky="w", padx=(8, 24))

        tk.Label(row, text="To:", bg=PANEL, fg=MUTED, font=FONT).grid(row=0, column=2, sticky="w")
        self.to_var = tk.StringVar()
        self.to_combo = ttk.Combobox(row, textvariable=self.to_var, state="readonly", width=12, font=FONT)
        self.to_combo.grid(row=0, column=3, sticky="w", padx=(8, 0))

        self.convert_btn = self._btn(panel, "CONVERT", self._convert, accent=True, padx=28, pady=10)
        self.convert_btn.pack(pady=20)

        footer = tk.Frame(panel, bg=PANEL)
        footer.pack(side="bottom", fill="x", padx=24, pady=10)
        tk.Label(
            footer, text="Output is saved in an 'output' folder next to the source file.",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 9),
        ).pack(side="left")
        self.open_btn = self._btn(footer, "Open output folder", self._open_output, state="disabled", padx=12, pady=4)
        self.open_btn.pack(side="right")

        return panel

    def _build_merge(self):
        panel = self._panel("Merge into one PDF")

        tk.Label(
            panel,
            text="Pick PDFs, or images (JPG / PNG / WEBP) — or a mix of both.\nThey are combined into a single PDF, in the order shown.",
            bg=PANEL, fg=MUTED, font=FONT, justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 12))

        self.merge_list = tk.Listbox(
            panel, bg=BG, fg=TEXT, selectbackground=ACCENT, selectforeground=TEXT,
            relief="flat", highlightbackground=BORDER, highlightthickness=1, font=FONT,
        )
        self.merge_list.pack(fill="both", expand=True, padx=24)

        btns = tk.Frame(panel, bg=PANEL)
        btns.pack(fill="x", padx=24, pady=12)
        self._btn(btns, "Add files", self._merge_add).pack(side="left")
        self._btn(btns, "Remove selected", self._merge_remove).pack(side="left", padx=8)
        self._btn(btns, "Clear", self._merge_clear).pack(side="left")
        self._btn(btns, "MERGE", self._merge_go, accent=True).pack(side="right")

        return panel

    def _build_split(self):
        panel = self._panel("Split PDF")

        self.split_file = None

        tk.Label(panel, text="No PDF selected", bg=PANEL, fg=MUTED, font=FONT, anchor="w").pack(fill="x", padx=24)
        self._btn(panel, "Choose PDF", self._pick_split).pack(anchor="w", padx=24, pady=(8, 14))

        self.split_mode = tk.StringVar(value="every")
        tk.Radiobutton(
            panel, text="Split every N pages", variable=self.split_mode, value="every",
            bg=PANEL, fg=TEXT, selectcolor=BG, activebackground=PANEL, activeforeground=TEXT,
            font=FONT, cursor="hand2",
        ).pack(anchor="w", padx=24)
        self.pages_spin = tk.Spinbox(
            panel, from_=1, to=9999, width=6, bg=BUTTON, fg=TEXT, insertbackground=TEXT,
            buttonbackground=BUTTON, buttoncursor="hand2", relief="flat", font=FONT,
        )
        self.pages_spin.delete(0, "end")
        self.pages_spin.insert(0, "2")
        self.pages_spin.pack(anchor="w", padx=40, pady=(4, 10))

        tk.Radiobutton(
            panel, text="Custom ranges", variable=self.split_mode, value="ranges",
            bg=PANEL, fg=TEXT, selectcolor=BG, activebackground=PANEL, activeforeground=TEXT,
            font=FONT, cursor="hand2",
        ).pack(anchor="w", padx=24)
        self.ranges_entry = tk.Entry(
            panel, bg=BUTTON, fg=TEXT, insertbackground=TEXT, relief="flat", font=FONT,
        )
        self.ranges_entry.insert(0, "1-2, 3-4, 5")
        self.ranges_entry.pack(fill="x", padx=40, pady=(4, 14))

        self._btn(panel, "SPLIT", self._split_go, accent=True).pack(anchor="w", padx=24)

        return panel

    def _build_compress(self):
        panel = self._panel("Compress")

        self.compress_file = None

        tk.Label(panel, text="No file selected", bg=PANEL, fg=MUTED, font=FONT, anchor="w").pack(fill="x", padx=24)
        self._btn(panel, "Choose PDF or image", self._pick_compress).pack(anchor="w", padx=24, pady=(8, 14))

        qrow = tk.Frame(panel, bg=PANEL)
        qrow.pack(fill="x", padx=24)
        tk.Label(qrow, text="Quality", bg=PANEL, fg=MUTED, font=FONT).pack(side="left")
        self.quality_var = tk.IntVar(value=60)
        self.quality_val = tk.Label(qrow, text="60", bg=PANEL, fg=TEXT, font=FONT_BOLD)
        self.quality_val.pack(side="right")
        self.quality_scale = tk.Scale(
            qrow, from_=1, to=100, orient="horizontal", variable=self.quality_var,
            command=lambda v: self.quality_val.config(text=v),
            bg=PANEL, fg=TEXT, troughcolor=BUTTON, highlightthickness=0,
            activebackground=ACCENT_HOVER, font=("Segoe UI", 8),
        )
        self.quality_scale.pack(fill="x", padx=8)

        tk.Label(
            panel, text="Lower quality = smaller file.\nPDFs are rebuilt page by page; images are re-saved as JPG.",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 9), justify="left",
        ).pack(anchor="w", padx=24, pady=(12, 14))

        self._btn(panel, "COMPRESS", self._compress_go, accent=True).pack(anchor="w", padx=24)

        return panel

    def _show(self, tool):
        for name, btn in self.side_buttons.items():
            btn.configure(bg=ACCENT if name == tool else BUTTON)
        for name, panel in self.panels.items():
            if name == tool:
                panel.pack(fill="both", expand=True)
            else:
                panel.pack_forget()

    def _busy(self, on):
        self.config(cursor="watch" if on else "")
        self.update()

    def _ask_conflict(self, path):
        answer = messagebox.askyesnocancel(
            "File already exists",
            f"'{path.name}' already exists.\n\nYes = overwrite\nNo = save with a new name\nCancel = stop",
        )
        if answer is None:
            return "cancel"
        return "overwrite" if answer else "rename"

    def _pick_file(self):
        path = filedialog.askopenfilename(title="Choose a file", filetypes=FILE_TYPES)
        if not path:
            return
        fmt = detect_format(path)
        if fmt is None:
            self.toaster.show("unsupported file type", "warn")
            return
        self.selected = path
        self.file_label.config(text=f"File: {path}", fg=TEXT)
        self.from_var.set(fmt)
        self.to_combo["values"] = VALID_TARGETS[fmt]
        self.to_var.set(VALID_TARGETS[fmt][0])

    def _convert(self):
        src = self.selected
        fmt = self.from_var.get()
        tgt = self.to_var.get()
        if not src or fmt == "-" or not tgt:
            self.toaster.show("choose a file first", "warn")
            return
        handler = HANDLERS[(fmt, tgt)]
        self._busy(True)
        try:
            if (fmt, tgt) in MULTI_PAGE:
                paths = handler(str(src), str(src), on_conflict=self._ask_conflict)
            else:
                out = resolve_output_path(src, tgt, on_conflict=self._ask_conflict)
                paths = handler(str(src), str(out))
                if paths is None:
                    paths = [out]
            out_dir = get_output_dir(src)
            self._set_output(out_dir)
            self.toaster.show(f"done: {len(paths)} file(s) saved", "success")
        except CancelledError:
            pass
        except Exception as e:
            self.toaster.show(f"conversion failed: {str(e)[:70]}", "error")
        finally:
            self._busy(False)

    def _merge_add(self):
        paths = filedialog.askopenfilenames(title="Choose files to merge", filetypes=FILE_TYPES)
        for p in paths:
            if p not in self.merge_files:
                self.merge_files.append(p)
                self.merge_list.insert("end", Path(p).name)

    def _merge_remove(self):
        for i in reversed(self.merge_list.curselection()):
            del self.merge_files[i]
            self.merge_list.delete(i)

    def _merge_clear(self):
        self.merge_files = []
        self.merge_list.delete(0, "end")

    def _merge_go(self):
        if len(self.merge_files) < 2:
            self.toaster.show("add at least two files", "warn")
            return
        pdfs = []
        imgs = []
        for p in self.merge_files:
            fmt = detect_format(p)
            if fmt == "PDF":
                pdfs.append(p)
            elif fmt in IMAGE_FORMATS:
                imgs.append((p, fmt))
            else:
                self.toaster.show(f"'{Path(p).name}' is not a PDF or an image", "warn")
                return
        self._busy(True)
        try:
            tmpdir = Path(tempfile.mkdtemp(prefix="filetool_merge_"))
            merged_parts = list(pdfs)
            for i, (img, fmt) in enumerate(imgs):
                tmp_pdf = tmpdir / f"img_{i}.pdf"
                HANDLERS[(fmt, "PDF")](img, str(tmp_pdf))
                merged_parts.append(str(tmp_pdf))
            out = self._merge_output_name(self.merge_files[0])
            merge_pdfs(merged_parts, out)
            self._set_output(out.parent)
            self.toaster.show(f"merged {len(merged_parts)} file(s) into {out.name}", "success")
        except CancelledError:
            pass
        except Exception as e:
            self.toaster.show(f"merge failed: {str(e)[:70]}", "error")
        finally:
            self._busy(False)

    def _merge_output_name(self, first_file):
        out_dir = get_output_dir(first_file)
        candidate = out_dir / "merged.pdf"
        n = 1
        while candidate.exists():
            choice = self._ask_conflict(candidate)
            if choice == "overwrite":
                return candidate
            if choice == "cancel":
                raise CancelledError()
            candidate = out_dir / f"merged ({n}).pdf"
            n += 1
        return candidate

    def _pick_split(self):
        path = filedialog.askopenfilename(title="Choose a PDF", filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        fmt = detect_format(path)
        if fmt != "PDF":
            self.toaster.show("only PDF files can be split", "warn")
            return
        self.split_file = path

    def _split_go(self):
        if not self.split_file:
            self.toaster.show("choose a PDF first", "warn")
            return
        self._busy(True)
        try:
            if self.split_mode.get() == "every":
                try:
                    n = int(self.pages_spin.get())
                except ValueError:
                    raise ValueError("Pages per file must be a number.")
                if n < 1:
                    raise ValueError("Pages per file must be at least 1.")
                paths = split_pdf_every(self.split_file, n)
            else:
                try:
                    ranges = self._parse_ranges(self.ranges_entry.get())
                except ValueError as e:
                    raise ValueError(f"Bad range format: {e}")
                paths = split_pdf_ranges(self.split_file, ranges)
            self._set_output(get_output_dir(self.split_file))
            self.toaster.show(f"split into {len(paths)} files", "success")
        except ValueError as e:
            self.toaster.show(f"bad range format: {e}", "error")
        except Exception as e:
            self.toaster.show(f"split failed: {str(e)[:70]}", "error")
        finally:
            self._busy(False)

    def _parse_ranges(self, text):
        ranges = []
        for part in text.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, _, b = part.partition("-")
                ranges.append((int(a.strip()), int(b.strip())))
            else:
                v = int(part)
                ranges.append((v, v))
        if not ranges:
            raise ValueError("no ranges given")
        return ranges

    def _pick_compress(self):
        path = filedialog.askopenfilename(title="Choose a PDF or image", filetypes=FILE_TYPES)
        if not path:
            return
        fmt = detect_format(path)
        if fmt != "PDF" and fmt not in IMAGE_FORMATS:
            self.toaster.show("only PDFs and images can be compressed", "warn")
            return
        self.compress_file = path

    def _compress_go(self):
        if not self.compress_file:
            self.toaster.show("choose a file first", "warn")
            return
        fmt = detect_format(self.compress_file)
        quality = self.quality_var.get()
        self._busy(True)
        try:
            if fmt == "PDF":
                out = resolve_output_path(self.compress_file, "PDF", on_conflict=self._ask_conflict)
                compress_pdf(self.compress_file, out, quality=quality)
            else:
                out = resolve_output_path(self.compress_file, "JPG", on_conflict=self._ask_conflict)
                compress_image(self.compress_file, out, quality=quality)
            self._set_output(out.parent)
            self.toaster.show(f"compressed at quality {quality}", "success")
        except CancelledError:
            pass
        except Exception as e:
            self.toaster.show(f"compress failed: {str(e)[:70]}", "error")
        finally:
            self._busy(False)


def main():
    App().mainloop()


if __name__ == "__main__":
    main()