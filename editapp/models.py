from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Domain(models.Model):
    domain = models.CharField(max_length=64, primary_key=True)
    owner =  models.ForeignKey(User, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now_add=True) # when it was changed
    exported = models.DateTimeField()   # when it was saved to a file for the DNS server
    rrs = models.TextField()

    class Meta:
        permissions = (
            ("see_all", "Can see all users' domains"),
        )