from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )

    property = models.ForeignKey('listings.Property', on_delete=models.CASCADE, related_name='bookings')
    traveller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_made')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.property.title} - {self.traveller.username}"

    def total_price(self):  # CHANGED: method instead of @property
        if self.check_in and self.check_out and self.property:
            nights = (self.check_out - self.check_in).days
            return nights * self.property.price_per_night
        return 0
