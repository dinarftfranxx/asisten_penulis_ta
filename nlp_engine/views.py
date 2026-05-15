# nlp_engine/views.py
import re  # Modul bawaan Python untuk memisahkan kalimat
import os
import csv
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Import ke-3 algoritma kita
from .algoritma import cari_saran_typo, cek_sentence_starter, cek_ngram_bigram

# ===== MEMUAT DATA DARI CSV (SAAT SERVER PERTAMA KALI MENYALA) =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def muat_kamus_kata():
    """Memuat daftar kata baku dari CSV ke dalam dictionary."""
    kamus = {}
    path = os.path.join(DATA_DIR, 'kamus_kata_baku.csv')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                kamus[row['kata_baku']] = True
        print(f"[OK] Kamus kata baku dimuat: {len(kamus):,} kata")
    except FileNotFoundError:
        print(f"[WARNING] File tidak ditemukan: {path}")
    return kamus

def muat_kamus_frasa():
    """Memuat daftar frasa dari CSV ke dalam dictionary."""
    kamus = {}
    path = os.path.join(DATA_DIR, 'kamus_frasa.csv')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                kamus[row['frasa']] = True
        print(f"[OK] Kamus frasa dimuat: {len(kamus):,} frasa")
    except FileNotFoundError:
        print(f"[WARNING] File tidak ditemukan: {path}")
    return kamus

def muat_kamus_tidak_baku():
    """Memuat pemetaan kata tidak baku -> kata baku dari CSV."""
    kamus = {}
    path = os.path.join(DATA_DIR, 'kamus_tidak_baku.csv')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                kamus[row['tidak_baku']] = row['bentuk_baku']
        print(f"[OK] Kamus tidak baku dimuat: {len(kamus):,} entri")
    except FileNotFoundError:
        print(f"[WARNING] File tidak ditemukan: {path}")
    return kamus

# Data dimuat SEKALI saat server menyala, disimpan di memori
KBBI_DICT = muat_kamus_kata()
CORPUS_BIGRAM = muat_kamus_frasa()
TIDAK_BAKU_DICT = muat_kamus_tidak_baku()


@api_view(['POST'])
def cek_teks(request):
    teks_input = request.data.get('teks', '')
    hasil_pengecekan = []
    
    # Kita pecah teks berdasarkan titik, tanda seru, atau tanda tanya
    # Gunakan split yang mempertahankan pemisah jika memungkinkan, 
    # tapi cara termudah adalah per kalimat:
    kalimat_list = re.split(r'[.!?\n]+', teks_input)
    
    for kalimat in kalimat_list:
        kalimat = kalimat.strip()
        if not kalimat:
            continue
            
        # --- TAHAP 1: CEK POS TAGGING (Awal Kalimat) ---
        peringatan_pos = cek_sentence_starter(kalimat)
        if peringatan_pos:
            hasil_pengecekan.append({
                "jenis_error": "Tata Bahasa (POS Tagging)",
                "teks_bermasalah": kalimat,
                "keterangan": peringatan_pos,
                "konteks": kalimat
            })

        # --- TAHAP 2: CEK TYPO (Levenshtein) & BENTUK TIDAK BAKU ---
        kata_kata = kalimat.split()
        
        for i in range(len(kata_kata)):
            kata_asli = kata_kata[i]
            kata_bersih = kata_asli.strip('.,!?()[]{}"\'').lower()
            
            if not kata_bersih:
                continue
            
            # A. Cek bentuk tidak baku dulu (koreksi langsung)
            if kata_bersih in TIDAK_BAKU_DICT:
                hasil_pengecekan.append({
                    "jenis_error": "Bentuk Tidak Baku",
                    "teks_bermasalah": kata_bersih,
                    "keterangan": f"Bentuk baku: {TIDAK_BAKU_DICT[kata_bersih]}",
                    "konteks": kalimat
                })
                continue  # Sudah ketemu koreksi langsung, skip Levenshtein
                
            # B. Eksekusi Levenshtein (Mendeteksi Typo)
            if kata_bersih not in KBBI_DICT:
                saran = cari_saran_typo(kata_bersih, KBBI_DICT)
                if saran:
                    hasil_pengecekan.append({
                        "jenis_error": "Typo (Levenshtein)",
                        "teks_bermasalah": kata_bersih,
                        "keterangan": f"Mungkin maksudmu: {', '.join(saran)}",
                        "konteks": kalimat
                    })
                    
    return Response({
        "status": "sukses",
        "teks_asli": teks_input,
        "hasil": hasil_pengecekan
    })