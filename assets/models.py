from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AssetCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Asset(models.Model):
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    asset_code = models.CharField(max_length=50, unique=True)
    quantity = models.IntegerField(default=1)

    location = models.CharField(max_length=200, blank=True)
    condition = models.CharField(max_length=100, default="Good")
    purchased_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.asset_code})"


class AssetIssue(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    issued_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    issued_on = models.DateField(auto_now_add=True)
    returned_on = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[("issued", "Issued"), ("returned", "Returned")],
        default="issued"
    )

    def __str__(self):
        return f"{self.asset} -> {self.issued_to}"
