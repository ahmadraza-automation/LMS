from django.contrib import admin
from .models import RadioEchoesEpisode

@admin.register(RadioEchoesEpisode)
class RadioEchoesEpisodeAdmin(admin.ModelAdmin):
    list_display = ['series_name', 'episode_name', 'genre', 'scraped_at']
    search_fields = ['series_name', 'episode_name']
    list_filter = ['genre', 'scraped_at']