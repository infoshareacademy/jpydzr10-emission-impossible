from django.contrib.auth.models import AbstractUser
from django.db import models
from companies.models import Company


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True)
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('użytkownik', 'Użytkownik'),
        ('audytor', 'Audytor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='użytkownik', verbose_name="Rola")
    companies = models.ManyToManyField(Company, through='UserCompanyPermission')
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "Użytkownik"
        verbose_name_plural = "Użytkownicy"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class UserCompanyPermission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    can_save = models.BooleanField(default=False)
    can_read = models.BooleanField(default=True)