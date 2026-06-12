# nlp_engine/views.py
import re
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import KataKamus, FrasaKorpus, BentukTidakBaku, AturanAwalKalimat
from django.db.utils import ProgrammingError, OperationalError
from .algoritma import cari_saran_typo_db, cek_sentence_starter, cek_ngram_bigram_db

# ===== MEMUAT DATA KECIL KE MEMORI SAAT SERVER MENYALA =====
# KataKamus (75k) & BentukTidakBaku (3.5k) cukup kecil → cache di memori
# FrasaKorpus (670k) → query database langsung (ada index)

def _muat_kamus_ke_memori():
    """Muat kata baku ke set Python untuk pengecekan O(1)."""
    try:
        kamus = set(KataKamus.objects.values_list('kata', flat=True))
        print(f"[OK] Kamus kata baku dimuat dari DB: {len(kamus):,} kata")
        return kamus
    except (ProgrammingError, OperationalError):
        print("[WARNING] Tabel kamus_kata belum ada (mungkin sedang migrate).")
        return set()

def _muat_tidak_baku_ke_memori():
    """Muat pemetaan tidak_baku → baku ke dict Python."""
    try:
        kamus = dict(BentukTidakBaku.objects.values_list('kata_tidak_baku', 'kata_baku'))
        print(f"[OK] Kamus tidak baku dimuat dari DB: {len(kamus):,} entri")
        return kamus
    except (ProgrammingError, OperationalError):
        print("[WARNING] Tabel tidak_baku belum ada.")
        return {}

def _muat_aturan_awal_kalimat():
    """Muat aturan awal kalimat ke dict Python."""
    try:
        aturan = dict(AturanAwalKalimat.objects.values_list('kata_terlarang', 'saran_pengganti'))
        print(f"[OK] Aturan awal kalimat dimuat dari DB: {len(aturan)} entri")
        return aturan
    except (ProgrammingError, OperationalError):
        print("[WARNING] Tabel aturan_awal_kalimat belum ada. Mengembalikan kamus kosong.")
        return {}

KBBI_SET = _muat_kamus_ke_memori()
TIDAK_BAKU_DICT = _muat_tidak_baku_ke_memori()
ATURAN_AWAL_KALIMAT_DICT = _muat_aturan_awal_kalimat()


@api_view(['POST'])
def cek_teks(request):
    teks_input = request.data.get('teks', '')
    hasil_pengecekan = []

    kalimat_list = re.split(r'[.!?\n]+', teks_input)

    for kalimat in kalimat_list:
        kalimat = kalimat.strip()
        if not kalimat:
            continue

        # --- TAHAP 1: CEK POS TAGGING (Awal Kalimat) ---
        peringatan_pos = cek_sentence_starter(kalimat, ATURAN_AWAL_KALIMAT_DICT)
        if peringatan_pos:
            hasil_pengecekan.append({
                "jenis_error": "Tata Bahasa (POS Tagging)",
                "teks_bermasalah": kalimat,
                "keterangan": peringatan_pos,
                "konteks": kalimat
            })

        # --- TAHAP 2: CEK TYPO & BENTUK TIDAK BAKU ---
        kata_kata = kalimat.split()

        for i in range(len(kata_kata)):
            kata_asli = kata_kata[i]
            kata_bersih = kata_asli.strip('.,!?()[]{}"\'').lower()

            if not kata_bersih:
                continue

            # --- TAHAP 3: CEK N-GRAM (Kewajaran Frasa) via Database ---
            if i < len(kata_kata) - 1:
                if kata_asli[-1] not in '.,!?;:()[]{}"\'':
                    kata_berikut_asli = kata_kata[i+1]

                    if kata_berikut_asli[0] not in '.,!?;:()[]{}"\'':
                        kata_berikut_bersih = kata_berikut_asli.strip('.,!?()[]{}"\'').lower()

                        # N-Gram hanya berjalan jika KEDUA kata adalah kata baku
                        if kata_bersih in KBBI_SET and kata_berikut_bersih in KBBI_SET:
                            peringatan_ngram = cek_ngram_bigram_db(kata_bersih, kata_berikut_bersih)
                            if peringatan_ngram:
                                hasil_pengecekan.append({
                                    "jenis_error": "Gaya Bahasa (N-Gram)",
                                    "teks_bermasalah": f"{kata_asli} {kata_berikut_asli}",
                                    "keterangan": peringatan_ngram,
                                    "konteks": kalimat
                                })

            # A. Cek bentuk tidak baku dulu (koreksi langsung)
            if kata_bersih in TIDAK_BAKU_DICT:
                hasil_pengecekan.append({
                    "jenis_error": "Bentuk Tidak Baku",
                    "teks_bermasalah": kata_bersih,
                    "keterangan": f"Bentuk baku: {TIDAK_BAKU_DICT[kata_bersih]}",
                    "konteks": kalimat
                })
                continue

            # B. Eksekusi Levenshtein via pg_trgm (Database)
            if kata_bersih not in KBBI_SET:
                saran = cari_saran_typo_db(kata_bersih)
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