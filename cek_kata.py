import csv
import os

DATA_DIR = os.path.join('nlp_engine', 'data')
path = os.path.join(DATA_DIR, 'kamus_kata_baku.csv')

kamus = {}
with open(path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        kamus[row['kata_baku']] = True

print(f"Total kata dimuat: {len(kamus)}")
print(f"'ini' ada: {'ini' in kamus}")
print(f"'melakukan' ada: {'melakukan' in kamus}")
print(f"'adalah' ada: {'adalah' in kamus}")
print(f"'analisa' ada: {'analisa' in kamus}")

# Cek isi 5 baris sekitar kata 'ini'
sorted_words = sorted(kamus.keys())
if 'ini' in sorted_words:
    idx = sorted_words.index('ini')
    print(f"\nKata sekitar 'ini' di kamus: {sorted_words[idx-2:idx+3]}")
