# FileTool

A simple Python GUI application for working with files.

**FileTool** brings a few common file operations into one place — **convert, merge, and compress** — so you don't have to use a different tool for every small task.

I started this project because I felt a simple desktop tool for these operations could be useful, and it also gave me a chance to build something practical while learning and experimenting with Python.

> 🚧 FileTool is currently under active development.

## Features

### 🔄 Convert

Convert files between supported formats.

Some of the formats being worked with include:

* PDF
* DOCX
* PPTX
* TXT
* Markdown
* Images

The available conversions will continue to grow as the project develops.

### 🔗 Merge

Merge multiple files into a single file where supported.

For example:

* Merge multiple PDFs
* Combine supported documents
* Merge text-based files

### 🗜️ Compress

Compress supported files to reduce their size.

Compression methods depend on the type of file being processed.

---

## 🖥️ Interface

FileTool currently uses a simple **Tkinter GUI**.

Files can be selected using the normal file browser, keeping the workflow straightforward:

```text
Choose an operation
        ↓
Browse for file(s)
        ↓
Select output location
        ↓
Process
        ↓
Done
```

---

## 🛠️ Built With

* **Python**
* **Tkinter**
* Python libraries for file processing
* Git
* GitHub

The project is built entirely with Python.

---

## 📂 Project Structure

```text
FileTool/
│
├── converters/
│   └── ...
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

The structure may change as new features are added.

---

## 🚀 Getting Started

### Requirements

* Windows
* Python 3.x

### Clone the repository

```bash
git clone https://github.com/AlphaCore0038/FileTool.git
cd FileTool
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run FileTool

```bash
python main.py
```

---

## 📌 Current Status

| Feature          | Status                     |
| ---------------- | -------------------------- |
| GUI              | ✅ Available                |
| File Conversion  | 🚧 In Development          |
| File Merging     | 🚧 In Development          |
| File Compression | 🚧 In Development          |
| Batch Processing | 📋 Planned                 |
| Drag & Drop      | 📋 Not currently supported |

Supported formats and operations may change as development continues.

---

## 🔮 Future Ideas

Some things I may add as the project grows:

* More file formats
* More conversion combinations
* Better error handling
* Progress indicators
* Batch processing
* Improved GUI
* File preview
* Drag-and-drop support
* Standalone `.exe` build
* More compression options

Not everything on this list is guaranteed to be implemented.

---

## 🤝 Contributing

FileTool is currently a personal/student-level open-source project.

If you find a bug, have an idea, or want to improve something, feel free to open an issue or submit a pull request.

---

## 📄 License

This project is open source.

*A license will be added as the project develops.*

---

## 👨‍💻 About

**FileTool** is a personal project built by **Chaitanya**.

The goal isn't to create another complicated file-management platform. It's simply to make a useful little tool that handles some common file operations in one place.

Built with Python while learning, experimenting, and improving along the way.

---

⭐ If you find FileTool useful, consider giving the repository a star.