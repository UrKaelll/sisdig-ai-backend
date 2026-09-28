import sys
import os

# Memasukkan direktori utama (root) ke sistem path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
