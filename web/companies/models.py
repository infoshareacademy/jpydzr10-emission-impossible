from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=200)
    zip = models.CharField(max_length=20)
    tel = models.CharField(max_length=30)
    mail = models.EmailField()
    krs = models.CharField(max_length=20)
    regon = models.CharField(max_length=20)
    nip = models.CharField(max_length=20)
    capital_group_name = models.CharField(max_length=200)

    def __str__(self):
        return self.co_name