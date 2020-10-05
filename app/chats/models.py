from django.db import models
from core.models import TimestampedModel

class Log(TimestampedModel):
    line_user_id = models.CharField(max_length=33, blank=False, null=False)
    keyword = models.TextField(blank=False)

    def __str__(self):
        return f"{self.keyword} - {self.line_user_id}"
