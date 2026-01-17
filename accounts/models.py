from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('OWNER', 'Property Owner'),
        ('TRAVELLER', 'Traveller'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='TRAVELLER')

    def is_owner(self):
        return self.role == 'OWNER'

    def is_traveller(self):
        return self.role == 'TRAVELLER'

    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    class Meta:
        ordering = ['-date_joined']
