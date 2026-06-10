from django.contrib import admin
from .models import KataKamus, FrasaKorpus, BentukTidakBaku, AturanAwalKalimat


@admin.register(KataKamus)
class KataKamusAdmin(admin.ModelAdmin):
    list_display = ('kata', 'kelas_kata', 'created_at')
    search_fields = ('kata',)
    list_filter = ('kelas_kata',)
    ordering = ('kata',)


@admin.register(FrasaKorpus)
class FrasaKorpusAdmin(admin.ModelAdmin):
    list_display = ('frasa', 'frekuensi', 'created_at')
    search_fields = ('frasa',)
    ordering = ('-frekuensi',)


@admin.register(BentukTidakBaku)
class BentukTidakBakuAdmin(admin.ModelAdmin):
    list_display = ('kata_tidak_baku', 'kata_baku', 'created_at')
    search_fields = ('kata_tidak_baku', 'kata_baku')
    ordering = ('kata_tidak_baku',)


@admin.register(AturanAwalKalimat)
class AturanAwalKalimatAdmin(admin.ModelAdmin):
    list_display = ('kata_terlarang', 'saran_pengganti', 'created_at')
    search_fields = ('kata_terlarang', 'saran_pengganti')
    ordering = ('kata_terlarang',)