# nlp_engine/algoritma.py
from .models import KataKamus, FrasaKorpus


# LEVENSHTEIN DISTANCE (tetap dipakai sebagai fallback/perhitungan manual)

def hitung_levenshtein(kata_salah, kata_target):
    m = len(kata_salah)
    n = len(kata_target)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if kata_salah[i - 1] == kata_target[j - 1]:
                biaya_substitusi = 0
            else:
                biaya_substitusi = 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + biaya_substitusi
            )
    return dp[m][n]


# SARAN TYPO VIA DATABASE (pg_trgm similarity)

def cari_saran_typo_db(kata_typo, maksimal_saran=3):
    
    kata_typo = kata_typo.lower()

    # Gunakan trigram similarity dari PostgreSQL pg_trgm
    # similarity() mengembalikan nilai 0-1, tapi aing ambil yang >= 0.3
    kandidat = KataKamus.objects.raw(
        """
        SELECT id, kata, similarity(kata, %s) AS skor
        FROM kamus_kata
        WHERE similarity(kata, %s) >= 0.3
        ORDER BY skor DESC
        LIMIT %s
        """,
        [kata_typo, kata_typo, maksimal_saran]
    )

    hasil = []
    for row in kandidat:
        # Filter tambahan: hanya ambil yang jarak Levenshtein <= 2
        jarak = hitung_levenshtein(kata_typo, row.kata)
        if jarak <= 2:
            hasil.append(row.kata)

    return hasil


# CEK SENTENCE STARTER (POS Tagging sederhana)

def cek_sentence_starter(kalimat, aturan_dict):
    kalimat_bersih = kalimat.strip().lower()
    if not kalimat_bersih:
        return None
    kata_pertama = kalimat_bersih.split()[0]
    kata_pertama = kata_pertama.strip('.,!?')

    if kata_pertama in aturan_dict:
        saran = aturan_dict[kata_pertama]
        return f"Kata '{kata_pertama.capitalize()}' dilarang mengawali kalimat. Saran: {saran}"
    return None



def cek_ngram_bigram_db(kata1, kata2):
   
    frasa = f"{kata1.lower()} {kata2.lower()}"
    ada = FrasaKorpus.objects.filter(frasa=frasa).exists()
    if not ada:
        return f"Frasa '{frasa}' terdeteksi kurang wajar/tidak padu."
    return None