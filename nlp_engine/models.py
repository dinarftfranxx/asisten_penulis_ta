from django.db import models


class KataKamus(models.Model):
    """
    Tabel kamus kata baku Bahasa Indonesia.
    Gabungan dari kamus_kata_baku.csv + kamus_kelas_kata.csv.
    Digunakan oleh:
      - Levenshtein (via pg_trgm similarity search) untuk deteksi typo
      - POS Tagging untuk cek kelas kata
    """
    kata = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Kata baku dari KBBI"
    )
    kelas_kata = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Kelas kata (Nomina, Verba, Adjektiva, dll)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kamus_kata'
        verbose_name = 'Kata Kamus'
        verbose_name_plural = 'Kata Kamus'
        ordering = ['kata']

    def __str__(self):
        if self.kelas_kata:
            return f"{self.kata} ({self.kelas_kata})"
        return self.kata


class FrasaKorpus(models.Model):
    """
    Tabel korpus frasa (bigram) dari dataset Leipzig Corpora.
    Digunakan oleh algoritma N-Gram untuk mengecek kewajaran frasa.
    """
    frasa = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text="Pasangan 2 kata (bigram)"
    )
    frekuensi = models.IntegerField(
        default=0,
        help_text="Jumlah kemunculan frasa di korpus"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'korpus_frasa'
        verbose_name = 'Frasa Korpus'
        verbose_name_plural = 'Frasa Korpus'
        ordering = ['-frekuensi']

    def __str__(self):
        return f"{self.frasa} ({self.frekuensi}x)"


class BentukTidakBaku(models.Model):
    """
    Tabel pemetaan kata tidak baku ke bentuk bakunya.
    Digunakan untuk koreksi langsung tanpa perlu similarity search.
    """
    kata_tidak_baku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Bentuk penulisan yang tidak baku"
    )
    kata_baku = models.CharField(
        max_length=100,
        help_text="Bentuk baku yang benar"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bentuk_tidak_baku'
        verbose_name = 'Bentuk Tidak Baku'
        verbose_name_plural = 'Bentuk Tidak Baku'
        ordering = ['kata_tidak_baku']

    def __str__(self):
        return f"{self.kata_tidak_baku} → {self.kata_baku}"


class AturanAwalKalimat(models.Model):
    """
    Tabel aturan untuk kata-kata (biasanya konjungsi) yang dilarang mengawali kalimat.
    Dilengkapi dengan saran kata pengganti.
    """
    kata_terlarang = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Kata yang dilarang di awal kalimat (misal: sehingga, dan)"
    )
    saran_pengganti = models.CharField(
        max_length=150,
        help_text="Saran kata pengganti (misal: Akibatnya, Dengan demikian)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'aturan_awal_kalimat'
        verbose_name = 'Aturan Awal Kalimat'
        verbose_name_plural = 'Aturan Awal Kalimat'
        ordering = ['kata_terlarang']

    def __str__(self):
        return f"{self.kata_terlarang} → {self.saran_pengganti}"