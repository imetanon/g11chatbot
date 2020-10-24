from django.db import models
from core.models import TimestampedModel
from users.models import User
import json

class TripPlan(TimestampedModel):
    STATUS_CHOICES = (
        (0, 'inactive'),
        (1, 'active'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_plans')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    data = models.JSONField(null=False)
    
    @property
    def get_json_data(self):
        return json.dumps(self.data)
   
    def __str__(self):
        return self.user.line_user_id
