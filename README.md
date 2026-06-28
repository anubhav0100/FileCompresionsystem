# TeraZip (AGC)

**TeraZip** (AntiGravity Compression) is an ultra-fast, multi-threaded file compression utility designed specifically to tackle massive datasets (1 TB+). By leveraging Python's `multiprocessing` and the `zstandard` algorithm at its maximum compression level, TeraZip achieves unparalleled compression ratios on highly compressible data (like logs, text, and uncompressed databases), shrinking gigabytes into megabytes in seconds.

## ✨ Features
- **Massive Scale:** Designed to handle 1 TB+ files without exhausting your system's RAM by streaming data in 64MB chunks.
- **Maximum Compression:** Uses Zstandard level 22 to achieve up to a 20:1 compression ratio on text/CSV data.
- **Multi-threaded Processing:** Automatically utilizes all your CPU cores to compress and decompress chunks in parallel.
- **Modern GUI:** Sleek, dark-mode graphical interface powered by CustomTkinter.
- **Cross-Platform:** Available as a standalone executable for Windows, macOS, and Linux.

## 📥 Installation

You can run TeraZip either from source or by downloading the standalone executable.

### Running from source
1. Clone the repository or download the source code.
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the GUI:
   ```bash
   python gui.py
   ```
4. Or run the CLI tool:
   ```bash
   python main.py --help
   ```

## 🚀 Usage (CLI)

**Compress a file:**
```bash
python main.py compress "C:\path\to\massive_dataset.csv" "C:\path\to\compressed_output.agc"
```

**Decompress a file:**
```bash
python main.py decompress "C:\path\to\compressed_output.agc" "C:\path\to\restored_dataset.csv"
```

## 💡 What compresses well?
*   **High Ratio (Up to 95% reduction):** Text files, CSVs, JSON logs, XML, source code, uncompressed database dumps.
*   **Low Ratio (1% to 5% reduction):** AI model weights (`.safetensors`), already compressed videos (`.mp4`), images (`.jpg`), and archives (`.zip`).

## 🛠️ Building Executables
To build your own standalone `.exe` or `.app` using PyInstaller:

**Windows:**
```bash
pyinstaller --noconfirm --onefile --windowed --name "TeraZip" gui.py
```
*(The executable will be located in the `dist/` folder)*
