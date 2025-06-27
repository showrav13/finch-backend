from django.db import models

# Create your models here.
class CompanySetting(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    address_line_1 = models.TextField(blank=True, null=True)
    address_line_2 = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to="company/logo", blank=True, null=True)
    tax = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0, help_text="Enter tax as a percentage (%)")
    shipping_fee = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0, help_text="Enter shipping fee as extra charge")
    currency = models.CharField(max_length=255, blank=True, null=True)
    currency_symbol = models.CharField(max_length=255, blank=True, null=True)
    currency_code = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Company Setting"
        verbose_name_plural = "Company Settings"