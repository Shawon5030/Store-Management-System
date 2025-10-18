
from django.db import models

class Product(models.Model):
    serial_number = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=150)
    mrr_number = models.CharField(max_length=50)
    date = models.DateField()
    total_received = models.PositiveIntegerField()
    distributed = models.PositiveIntegerField(default=0)
    remaining = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
 
        self.remaining = self.total_received - self.distributed
        self.total_price = self.unit_price * self.remaining
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} (MRR: {self.mrr_number})"
