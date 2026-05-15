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

def cari_saran_typo(kata_typo, kbbi_dict, maksimal_saran=3):
    saran = []
    for kata_baku in kbbi_dict.keys():
        if abs(len(kata_typo) - len(kata_baku)) > 3:
            continue
        jarak = hitung_levenshtein(kata_typo.lower(), kata_baku)
        if jarak <= 2:
            saran.append((kata_baku, jarak))
    saran.sort(key=lambda x: x[1])
    return [item[0] for item in saran[:maksimal_saran]]

def cek_sentence_starter(kalimat):
    kata_terlarang = ["dan", "yang", "atau", "karena", "sehingga", "di mana"]
    kalimat_bersih = kalimat.strip().lower()
    if not kalimat_bersih:
        return None
    kata_pertama = kalimat_bersih.split()[0]
    kata_pertama = kata_pertama.strip('.,!?')
    
    if kata_pertama in kata_terlarang:
        return f"Kata '{kata_pertama.capitalize()}' sebaiknya tidak mengawali kalimat."
    return None

def cek_ngram_bigram(kata1, kata2, dummy_corpus):
    frasa = f"{kata1.lower()} {kata2.lower()}"
    if frasa not in dummy_corpus:
        return f"Frasa '{frasa}' terdeteksi kurang wajar/tidak padu."
    return None