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


def is_kata_baku_lengkap(kata, kbbi_set):
    """
    Validasi kata baku dengan mempertimbangkan morfologi Bahasa Indonesia
    (imbuhan produktif: di-, ter-, ber-, se-, ke-...-an, pe-...-an, -nya, -lah, dll)
    """
    if not kata:
        return False
    if kata in kbbi_set:
        return True
    
    # 1. Klitika / Akhiran (-nya, -ku, -mu, -lah, -kah, -pun)
    for suf in ['nya', 'ku', 'mu', 'lah', 'kah', 'pun']:
        if kata.endswith(suf) and len(kata) > len(suf) + 2:
            base = kata[:-len(suf)]
            if base in kbbi_set:
                return True
            if base.startswith('di') and base[2:] in kbbi_set:
                return True
            if base.startswith('ter') and base[3:] in kbbi_set:
                return True
            if base.startswith('ber') and base[3:] in kbbi_set:
                return True

    # 2. Awalan Pasif di-
    if kata.startswith('di') and len(kata) > 3:
        stem = kata[2:]
        if stem in kbbi_set:
            return True
        if stem.endswith('kan') and stem[:-3] in kbbi_set:
            return True
        if stem.endswith('i') and stem[:-1] in kbbi_set:
            return True
        if stem.endswith('an') and stem[:-2] in kbbi_set:
            return True

    # 3. Awalan ter-
    if kata.startswith('ter') and len(kata) > 4:
        stem = kata[3:]
        if stem in kbbi_set:
            return True
        if stem.endswith('kan') and stem[:-3] in kbbi_set:
            return True
        if stem.endswith('i') and stem[:-1] in kbbi_set:
            return True
        if stem.endswith('an') and stem[:-2] in kbbi_set:
            return True

    # 4. Awalan ber-
    if kata.startswith('ber') and len(kata) > 4:
        stem = kata[3:]
        if stem in kbbi_set:
            return True
        if stem.endswith('an') and stem[:-2] in kbbi_set:
            return True

    # 5. Awalan se-
    if kata.startswith('se') and len(kata) > 3:
        if kata[2:] in kbbi_set:
            return True

    # 6. Konfiks ke-...-an dan pe-...-an
    if (kata.startswith('ke') or kata.startswith('pe')) and kata.endswith('an') and len(kata) > 5:
        if kata[2:-2] in kbbi_set:
            return True

    return False


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

        # --- TAHAP 2: CEK BENTUK TIDAK BAKU & TYPO ---
        kata_kata = kalimat.split()

        for i in range(len(kata_kata)):
            kata_asli = kata_kata[i]
            kata_bersih = kata_asli.strip('.,!?()[]{}"\'').lower()

            if not kata_bersih or not kata_bersih.isalpha():
                continue

            # A. Cek Bentuk Tidak Baku Terlebih Dahulu
            if kata_bersih in TIDAK_BAKU_DICT:
                hasil_pengecekan.append({
                    "jenis_error": "Bentuk Tidak Baku",
                    "teks_bermasalah": kata_bersih,
                    "keterangan": f"Bentuk baku: {TIDAK_BAKU_DICT[kata_bersih]}",
                    "konteks": kalimat
                })
                continue

            # B. Cek Typo (Levenshtein + pg_trgm) jika bukan kata baku & bukan bentuk berimbuhan sah
            if not is_kata_baku_lengkap(kata_bersih, KBBI_SET):
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