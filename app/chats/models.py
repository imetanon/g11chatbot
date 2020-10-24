from django.db import models
from core.models import TimestampedModel
from users.models import User

class Log(TimestampedModel):
    line_user_id = models.CharField(max_length=33, blank=False, null=False)
    keyword = models.TextField(blank=False)

    def __str__(self):
        return f"{self.keyword} - {self.line_user_id}"
    
class ChatState(TimestampedModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='chat_state')
    intent = models.CharField(max_length=200, blank=False)
    target = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return f"{self.user.line_user_id} - {self.intent} - {self.target}"