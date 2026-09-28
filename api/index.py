import os
import sys

# Dapatkan lokasi folder saat ini dan folder root di atasnya
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Masukkan kedua path ke sys.path di urutan paling depan
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

# Baru import app dari main.py
from main import app
