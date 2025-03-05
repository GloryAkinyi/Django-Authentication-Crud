from django.db import models

# Create your models here.

class Appointment(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=12)
    date = models.DateField()
    department = models.CharField(max_length=200)
    doctor = models.CharField(max_length=200)
    message = models.TextField()
    image = models.ImageField(upload_to='appointments/')  # New field

    def __str__(self):
        return self.name
