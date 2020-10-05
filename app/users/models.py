from django.db import models
from core.models import TimestampedModel

import datetime
from django.core.validators import MaxValueValidator, MinValueValidator

def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)    

class User(TimestampedModel):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Undefined'),
    )

    line_user_id = models.CharField(unique=True, max_length=33, blank=False, null=False)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default='U')
    birth_year = models.IntegerField(validators=[MinValueValidator(1984), max_value_current_year])

    def __str__(self):
        return self.line_user_id