import os
import sys

# Memastikan Vercel bisa membaca file main.py dari folder utama
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
