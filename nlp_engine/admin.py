from django.contrib import admin
from .models import KataKamus, FrasaKorpus, BentukTidakBaku


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