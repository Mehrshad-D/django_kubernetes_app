from django.db import models

class Message(models.Model):
    """
    A simple model to demonstrate database connectivity.
    Stores a text message and the timestamp it was created.
    """
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.text[:50]}..."

    class Meta:
        ordering = ['-created_at']
