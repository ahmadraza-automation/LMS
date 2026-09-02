from django.db import models

class RadioEchoesEpisode(models.Model):
    series_name = models.CharField(max_length=255)
    episode_name = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    broadcast_date = models.CharField(max_length=50, null=True, blank=True)
    episode_length = models.CharField(max_length=50, null=True, blank=True)
    download_link = models.URLField(null=True, blank=True)
    play_link = models.URLField(null=True, blank=True)
    file_size = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=True)
    
    scraped_url = models.URLField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scraped_at']
        verbose_name_plural = "Radio Echoes Episodes"
    
    def __str__(self):
        return f"{self.series_name} - {self.episode_name}"
    class SiteSetting(models.Model):
           site_name = models.CharField(max_length=100, default="AHMAD SQUAD")
    logo = models.ImageField(upload_to="site/", blank=True, null=True)

    def __str__(self):
        return self.site_name