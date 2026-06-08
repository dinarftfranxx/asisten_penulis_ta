"""
Migrasi untuk mengaktifkan ekstensi pg_trgm di PostgreSQL
dan membuat GIN trigram index di kolom 'kata' tabel KataKamus.

pg_trgm digunakan untuk similarity search (pengganti brute-force Levenshtein).
"""
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        # Aktifkan ekstensi pg_trgm di PostgreSQL
        TrigramExtension(),
    ]