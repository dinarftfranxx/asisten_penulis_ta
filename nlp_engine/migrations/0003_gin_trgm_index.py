"""
Migrasi untuk membuat GIN trigram index pada kolom 'kata' di tabel kamus_kata.
Index ini mempercepat query similarity() dari pg_trgm secara signifikan.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nlp_engine', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS idx_kamus_kata_trgm ON kamus_kata USING gin (kata gin_trgm_ops);",
            reverse_sql="DROP INDEX IF EXISTS idx_kamus_kata_trgm;",
        ),
    ]
