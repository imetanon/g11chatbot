from django.db import models
from core.models import TimestampedModel
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from users.models import User

class Province(TimestampedModel):
    code = models.CharField(unique=True, max_length=10, blank=False, null=False)
    name = models.CharField(unique=True, max_length=200, blank=False, null=False)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.id} - {self.name}"

class Category(TimestampedModel):
    name = models.CharField(max_length=255, unique=True, blank=False)
    description = models.CharField(max_length=500, blank=True)
    image_url = models.CharField(max_length=2083, blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class SubCategory(TimestampedModel):
    SUB_CATEGORY_TYPE_CHOICES = (
        (0, 'Sub Category - 1'),
        (1, 'Sub Category - 2'),
        (2, 'Sub Category - 3'),
        (3, 'Sub Category - 4'),
        (4, 'Sub Category - 5'),
        (5, 'Sub Category - 6'),
        (6, 'Sub Category - 7'),
    )
    
    name = models.CharField(max_length=255, unique=True, blank=False)
    sub_category_type = models.IntegerField(choices=SUB_CATEGORY_TYPE_CHOICES, default=0)
    description = models.CharField(max_length=500, blank=True)
    image_url = models.CharField(max_length=2083, blank=True)
    
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
    image_url = models.CharField(max_length=2083, blank=True)
    latitude = models.DecimalField(
        max_digits=8, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True)
    category = models.ManyToManyField(Category)
    sub_category = models.ManyToManyField(SubCategory)
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name='places')
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    # https://stackoverflow.com/questions/1036603/storing-business-hours-in-a-database

    class Meta:
        ordering = ['id']
        
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
        return f"{self.place.name} - {self.weekday}"

class PlaceAction(TimestampedModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='place_actions')
    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name='place_actions')
    action = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.line_user_id} - {self.action}"
    
class SubCategoryKeyword(TimestampedModel):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='sub_category_keywords')
    keyword = models.TextField(blank=False, null=False)
    
    def __str__(self):
        return f"{self.sub_category.name}"
