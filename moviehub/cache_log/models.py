from django.db import models

class VisitLog(models.Model):
    user = models.CharField(max_length=64, null=True)
    date = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    get_params = models.TextField()
    post_params = models.TextField()
    user_agent = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.user or 'Anonymous'} - {self.date}"

class MovieLog(models.Model):
    movie_title = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie_title} - {self.created_at}"
