from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Property(models.Model):
    CATEGORY_CHOICES = (
        ('HOME', 'Home'),
        ('APARTMENT', 'Apartment'),
        ('BEACHFRONT', 'Beachfront'),
        ('MOUNTAIN', 'Mountain'),
        ('CABIN', 'Cabin'),
        ('VILLA', 'Villa'),
        ('OTHER', 'Other'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties_owned')
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='HOME')
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    max_guests = models.PositiveIntegerField(default=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def main_image(self):
        main_img = self.images.filter(is_primary=True).first()
        if main_img:
            return main_img.image.url
        first_img = self.images.first()
        if first_img:
            return first_img.image.url
        return None

    def get_gallery_images(self):
        return self.images.all()[:6]

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/%Y/%m/%d/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Image for {self.property.title}"
