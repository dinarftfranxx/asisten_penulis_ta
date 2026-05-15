import pandas as pd
import re

def jalankan_mesin_pembersih():
    print("Senior lu lagi kerja... Tungguin aja, laptopnya jangan dimatiin.")
    
    kumpulan_kata = set()
    
    # Daftar sampah yang HARUS dibuang biar Levenshtein nggak error
    sampah = {
        'me', 'mem', 'men', 'meng', 'meny', 'pe', 'pem', 'pen', 'peng', 'peny',
        'di', 'ter', 'ke', 'se', 'ber', 'per', 'pel', 'an', 'kan', 'nya', 'ku', 
        'mu', 'kau', 'nda', 'i', 'lah', 'kah', 'tah', 'pun', 'pra', 'pasca', 
        'maha', 'tata', 'swa', 'tuna', 'antar', 'sub', 'super', 'wan', 'wati', 
        'man', 'isme', 'isasi', 'logi', 'grafi'
    }

    try:
        # Buka file aslinya
        df = pd.read_csv('kbbi_v(rapih).xlsx - kbbi_v.csv')
        
        # Kolom yang mau gue sedot isinya
        kolom_penting = ['nama', 'kata_dasar', 'kata_turunan', 'gabungan_kata', 'peribahasa', 'idiom']

        for index, row in df.iterrows():
            for kolom in kolom_penting:
                if kolom in df.columns:
                    teks_kotor = str(row[kolom]).lower()
                    if teks_kotor != 'nan' and teks_kotor.strip() != '':
                        # Hapus teks dalam kurung
                        teks_kotor = re.sub(r'\(.*?\)', ' ', teks_kotor)
                        # Buang angka dan tanda baca
                        teks_kotor = re.sub(r'[^a-z\s-]', ' ', teks_kotor)
                        
                        # Pecah teksnya kalau ada spasi dobel
                        potongan_kata = [re.sub(r'\s+', ' ', t).strip() for t in teks_kotor.split('  ') if t.strip()]
                        
                        for kata in potongan_kata:
                            kata = kata.strip('-')
                            if len(kata) > 1 and kata not in sampah:
                                kumpulan_kata.add(kata)

        # Simpan ke file baru yang udah siap pakai
        df_hasil = pd.DataFrame(list(kumpulan_kata), columns=['kata_baku'])
        df_hasil.sort_values(by='kata_baku', inplace=True)
        df_hasil.to_csv('kbbi_final_ta.csv', index=False)
        
        print(f"Selesai bos! File 'kbbi_final_ta.csv' udah jadi.")
        
    except Exception as e:
        print(f"Error dari mesin: {e}")

# Tombol on/off nya
jalankan_mesin_pembersih()