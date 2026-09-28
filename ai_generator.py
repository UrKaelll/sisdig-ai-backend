import json
import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# 1. Muat file .env dari root project
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# 2. Tempelkan API Key Groq kamu di sini (diawali gsk_...)
HARDCODED_API_KEY = "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"

SYSTEM_PROMPT = """
Anda adalah AI Dosen Pengampu mata kuliah Sistem Digital & Arsitektur Komputer.

Tugas Utama:
1. Menganalisis materi PowerPoint (PPT) yang diberikan.
2. Mengembangkan poin PPT menjadi modul pembelajaran akademis yang MENDALAM, KOMPLEKS, dan TERSTRUKTUR.
3. Menghasilkan output JSON murni yang valid untuk dirender frontend.

ATURAN PENULISAN CONTENT (SANGAT PENTING):
- DILARANG MENULIS DALAM BENTUK PARAGRAF PANJANG/TEBAL.
- Semua penjelasan pada 'content' WAJIB ditulis dalam bentuk POIN-POIN BERTAHAP, LANGKAH-LANGKAH KALKULASI, atau PROSEDUR RUNTUT.
- Gunakan penomoran bertingkat (misal: "1. Tahap Inisialisasi: ...", "2. Eksekusi Bit: ...") dan format Markdown (**bold**, <code>) agar penjelasan menyerupai papan tulis dosen.

ATURAN KUIS & LATIHAN SOAL (ACTIVITIES):
- Buatlah minimal 3-5 soal kuis/latihan yang bervariasi.
- Soal HARUS spesifik, bervariasi (konversi, fungsi gerbang logika, perhitungan bit), dan tidak boleh monoton/diulang.
- Setiap soal WAJIB memiliki pilihan jawaban, index jawaban benar, dan PENJELASAN LENGKAP (step-by-step) mengapa jawaban tersebut benar.

Gunakan HANYA tipe section: theory, example, interactive_conversion, practice, summary
Gunakan HANYA tipe interaktif: conversion_simulator, binary_grouping, positional_weight, quiz
Gunakan HANYA tipe konversi: binary_to_decimal, decimal_to_binary, binary_to_octal, octal_to_binary, binary_to_hexadecimal, hexadecimal_to_binary, decimal_to_octal, octal_to_decimal, decimal_to_hexadecimal, hexadecimal_to_decimal

Struktur JSON Wajib:
{
    "course": "Sistem Digital",
    "week": 1,
    "title": "...",
    "description": "...",
    "learning_objectives": ["..."],
    "sections": [
        {
            "type": "theory",
            "title": "Sub-Bab...",
            "content": [
                "**Langkah 1 (Prinsip Dasar):** ...",
                "**Langkah 2 (Formula/Rumus):** ...",
                "**Langkah 3 (Analisis Sifat):** ..."
            ],
            "interactive_type": null,
            "conversion_types": []
        }
    ],
    "activities": [
        {
            "id": 1,
            "question": "Berapakah hasil konversi 1011(2) ke desimal?",
            "options": ["9", "11", "13", "15"],
            "correct": 1,
            "explanation": "Tahapan Perhitungan:\\n- Bit 3: 1 × 2³ = 8\\n- Bit 2: 0 × 2² = 0\\n- Bit 1: 1 × 2¹ = 2\\n- Bit 0: 1 × 2⁰ = 1\\nTotal: 8 + 0 + 2 + 1 = 11(10)"
        }
    ]
}
"""

def get_available_groq_models(client):
    """Mendapatkan daftar model aktif langsung dari server Groq tanpa hardcode"""
    try:
        models_data = client.models.list()
        available_ids = [m.id for m in models_data.data]
        print(f"---> [DEBUG] Model yang tersedia di akun Groq kamu: {available_ids} <---")
        
        # Prioritaskan model Llama / Qwen yang berkapasitas besar jika tersedia
        preferred_keywords = ['llama-3.3', 'llama-3.2', 'llama-3.1', 'llama', 'qwen']
        
        sorted_models = []
        for kw in preferred_keywords:
            for m_id in available_ids:
                if kw in m_id and m_id not in sorted_models:
                    sorted_models.append(m_id)
                    
        # Tambahkan sisa model aktif lainnya
        for m_id in available_ids:
            if m_id not in sorted_models:
                sorted_models.append(m_id)
                
        return sorted_models
    except Exception as e:
        print(f"[WARN] Gagal mengambil daftar model dinamis dari Groq: {e}")
        return ["llama-3.3-70b-versatile", "llama-3.2-11b-vision-preview", "llama-3.1-8b-instant"]

def generate_ai_media(slides_data):
    api_key = os.getenv("GROQ_API_KEY") or HARDCODED_API_KEY

    if not api_key or "PASTE_GROQ" in api_key:
        raise ValueError("GROQ_API_KEY belum terpasang dengan benar.")

    client = Groq(api_key=api_key)

    material = {
        "slides": slides_data
    }

    # Kompres JSON untuk menghemat ruang token
    compact_material_json = json.dumps(material, ensure_ascii=False, separators=(',', ':'))

    full_prompt = f"""
    {SYSTEM_PROMPT}

    Berikut adalah data materi PowerPoint yang harus diproses:
    {compact_material_json}
    """

    models_to_try = get_available_groq_models(client)

    last_error = None

    for model_name in models_to_try:
        try:
            print(f"\n---> [DEBUG] Mengirim request ke model: {model_name} <---")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "Anda adalah AI pembuat JSON terstruktur untuk media pembelajaran. Kembalikan HANYA format JSON murni."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=4096
            )

            result_text = response.choices[0].message.content
            print(f"---> [DEBUG] Sukses diproses oleh model: {model_name} <---")
            return json.loads(result_text)

        except Exception as e:
            last_error = e
            print(f"[WARN] Model {model_name} gagal: {e}")
            continue

    raise last_error