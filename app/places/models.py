from django.db import models
from core.models import TimestampedModel
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

class Category(TimestampedModel):
    name = models.CharField(max_length=255, unique=True, blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
    
class SubCategory(TimestampedModel):
    name = models.CharField(max_length=255, unique=True, blank=True)

    class Meta:
        verbose_name = 'sub-category'
        verbose_name_plural = 'sub-categories'

    def __str__(self):
        return self.name

class Place(TimestampedModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    name_english = models.CharField(max_length=255, blank=True)
    display_name = models.CharField(max_length=255, blank=True)
    address1 = models.CharField(max_length=255, blank=False, null=False)
    address2 = models.CharField(max_length=255, blank=True)
    address3 = models.CharField(max_length=255, blank=True)
    tambon = models.CharField(max_length=200, blank=True)
    review_score = models.DecimalField(max_digits=2, decimal_places=1, validators=[
                                       MinValueValidator(0), MaxValueValidator(5)], default=0, blank=True, null=True)
    review_count = models.IntegerField(default=0, blank=True, null=True)
    # https://stackoverflow.com/questions/219569/best-database-field-type-for-a-url
    online_link = models.CharField(max_length=2083, blank=True)
    map_link = models.CharField(max_length=2083, blank=True)
    latitude = models.DecimalField(
        max_digits=8, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True)
    category = models.ManyToManyField(Category)
    sub_category = models.ManyToManyField(SubCategory)
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    # https://stackoverflow.com/questions/1036603/storing-business-hours-in-a-database

    @property
    def location(self):
        return f"{self.address1} {str(self.address2 or '')} {str(self.address3 or '')}"

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name
        super().save(*args, **kwargs)


class BusinessHour(TimestampedModel):
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name='business_hours')
    day = models.IntegerField(choices=DAY_CHOICES)
    open_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)
    
    @property
    def weekday(self):
        return self.get_day_display()

    def __str__(self):
        # return f"{self.place.name} - {self.DAY_CHOICES[self.day - 1][1]}"
        return f"{self.place.name} - {self.week_day}"
    
