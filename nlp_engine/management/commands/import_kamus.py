"""
Management command untuk import data dari file CSV ke database.

Cara pakai:
    python manage.py import_kamus              # import semua
    python manage.py import_kamus --kata        # hanya kata baku + kelas kata
    python manage.py import_kamus --frasa       # hanya frasa bigram
    python manage.py import_kamus --tidak-baku  # hanya kata tidak baku
    python manage.py import_kamus --clear       # hapus data lama sebelum import
"""
import csv
import os
import time

from django.core.management.base import BaseCommand
from nlp_engine.models import KataKamus, FrasaKorpus, BentukTidakBaku


class Command(BaseCommand):
    help = 'Import data kamus dari file CSV ke database PostgreSQL'

    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    BATCH_SIZE = 5000

    def add_arguments(self, parser):
        parser.add_argument(
            '--kata', action='store_true',
            help='Import kamus kata baku + kelas kata saja'
        )
        parser.add_argument(
            '--frasa', action='store_true',
            help='Import korpus frasa (bigram) saja'
        )
        parser.add_argument(
            '--tidak-baku', action='store_true',
            help='Import kata tidak baku saja'
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Hapus data lama sebelum import'
        )

    def handle(self, *args, **options):
        import_semua = not (options['kata'] or options['frasa'] or options['tidak_baku'])

        if options['kata'] or import_semua:
            self._import_kata_kamus(clear=options['clear'])

        if options['frasa'] or import_semua:
            self._import_frasa_korpus(clear=options['clear'])

        if options['tidak_baku'] or import_semua:
            self._import_bentuk_tidak_baku(clear=options['clear'])

        self.stdout.write(self.style.SUCCESS('\n✅ Semua import selesai!'))

    def _import_kata_kamus(self, clear=False):
        """
        Import dari kamus_kata_baku.csv dan kamus_kelas_kata.csv.
        Digabung jadi satu tabel KataKamus.
        """
        self.stdout.write('\n📖 Import Kata Kamus...')

        if clear:
            deleted, _ = KataKamus.objects.all().delete()
            self.stdout.write(f'   Hapus {deleted} data lama')

        # Tahap 1: Baca semua kata baku
        file_baku = os.path.join(self.DATA_DIR, 'kamus_kata_baku.csv')
        kata_dict = {}  # {kata: kelas_kata}

        with open(file_baku, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                kata = row['kata_baku'].strip()
                if kata:
                    kata_dict[kata] = None  # kelas kata belum diketahui

        self.stdout.write(f'   Baca {len(kata_dict)} kata dari kamus_kata_baku.csv')

        # Tahap 2: Tambahkan kelas kata dari kamus_kelas_kata.csv
        file_kelas = os.path.join(self.DATA_DIR, 'kamus_kelas_kata.csv')
        matched = 0

        with open(file_kelas, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                kata = row['kata'].strip()
                kelas = row['kelas'].strip()
                if kata in kata_dict:
                    kata_dict[kata] = kelas
                    matched += 1
                else:
                    # kata ada di kelas tapi tidak di baku — tetap tambahkan
                    kata_dict[kata] = kelas

        self.stdout.write(f'   Gabung {matched} kelas kata dari kamus_kelas_kata.csv')

        # Tahap 3: Ambil kata yang sudah ada di database untuk skip duplicates
        existing_kata = set(KataKamus.objects.values_list('kata', flat=True))
        new_entries = {k: v for k, v in kata_dict.items() if k not in existing_kata}
        self.stdout.write(f'   {len(existing_kata)} sudah di DB, {len(new_entries)} baru')

        # Tahap 4: Bulk insert
        objects = [
            KataKamus(kata=kata, kelas_kata=kelas)
            for kata, kelas in new_entries.items()
        ]

        start = time.time()
        KataKamus.objects.bulk_create(objects, batch_size=self.BATCH_SIZE)
        elapsed = time.time() - start

        total = KataKamus.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {len(objects)} kata diimport ({elapsed:.1f}s). Total di DB: {total}'
        ))

    def _import_frasa_korpus(self, clear=False):
        """Import dari kamus_frasa.csv ke tabel FrasaKorpus."""
        self.stdout.write('\n📚 Import Frasa Korpus (bigram)...')

        if clear:
            deleted, _ = FrasaKorpus.objects.all().delete()
            self.stdout.write(f'   Hapus {deleted} data lama')

        file_frasa = os.path.join(self.DATA_DIR, 'kamus_frasa.csv')

        # Baca semua frasa dari CSV
        frasa_list = []
        with open(file_frasa, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                frasa = row['frasa'].strip()
                try:
                    frekuensi = int(row['frekuensi'].strip())
                except (ValueError, KeyError):
                    frekuensi = 0
                if frasa:
                    frasa_list.append((frasa, frekuensi))

        self.stdout.write(f'   Baca {len(frasa_list)} frasa dari kamus_frasa.csv')

        # Skip yang sudah ada
        existing_frasa = set(FrasaKorpus.objects.values_list('frasa', flat=True))
        new_entries = [(f, freq) for f, freq in frasa_list if f not in existing_frasa]
        self.stdout.write(f'   {len(existing_frasa)} sudah di DB, {len(new_entries)} baru')

        # Bulk insert
        objects = [
            FrasaKorpus(frasa=frasa, frekuensi=frekuensi)
            for frasa, frekuensi in new_entries
        ]

        start = time.time()
        KataKamus_created = 0
        for i in range(0, len(objects), self.BATCH_SIZE):
            batch = objects[i:i + self.BATCH_SIZE]
            FrasaKorpus.objects.bulk_create(batch, batch_size=self.BATCH_SIZE)
            KataKamus_created += len(batch)
            if KataKamus_created % 50000 == 0 or KataKamus_created == len(objects):
                self.stdout.write(f'   ... {KataKamus_created}/{len(objects)} diimport')

        elapsed = time.time() - start
        total = FrasaKorpus.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {len(objects)} frasa diimport ({elapsed:.1f}s). Total di DB: {total}'
        ))

    def _import_bentuk_tidak_baku(self, clear=False):
        """Import dari kamus_tidak_baku.csv ke tabel BentukTidakBaku."""
        self.stdout.write('\n🔄 Import Bentuk Tidak Baku...')

        if clear:
            deleted, _ = BentukTidakBaku.objects.all().delete()
            self.stdout.write(f'   Hapus {deleted} data lama')

        file_tb = os.path.join(self.DATA_DIR, 'kamus_tidak_baku.csv')

        # Baca semua mapping
        mapping_list = []
        with open(file_tb, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tidak_baku = row['tidak_baku'].strip()
                baku = row['bentuk_baku'].strip()
                if tidak_baku and baku:
                    mapping_list.append((tidak_baku, baku))

        self.stdout.write(f'   Baca {len(mapping_list)} mapping dari kamus_tidak_baku.csv')

        # Skip yang sudah ada
        existing = set(BentukTidakBaku.objects.values_list('kata_tidak_baku', flat=True))
        new_entries = [(tb, b) for tb, b in mapping_list if tb not in existing]
        self.stdout.write(f'   {len(existing)} sudah di DB, {len(new_entries)} baru')

        # Bulk insert
        objects = [
            BentukTidakBaku(kata_tidak_baku=tb, kata_baku=b)
            for tb, b in new_entries
        ]

        start = time.time()
        BentukTidakBaku.objects.bulk_create(objects, batch_size=self.BATCH_SIZE)
        elapsed = time.time() - start

        total = BentukTidakBaku.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {len(objects)} mapping diimport ({elapsed:.1f}s). Total di DB: {total}'
        ))