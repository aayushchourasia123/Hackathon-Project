from django.db import models

# Create your models here.

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('CASH_IN', 'CASH_IN'),
        ('CASH_OUT', 'CASH_OUT'),
        ('DEBIT', 'DEBIT'),
        ('PAYMENT', 'PAYMENT'),
        ('TRANSFER', 'TRANSFER'),
    ]
    
    transaction_id = models.AutoField(primary_key=True)
    step = models.IntegerField(default=1)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    nameOrig = models.CharField(max_length=100)  # Origin account name
    oldbalanceOrg = models.DecimalField(max_digits=15, decimal_places=2)
    newbalanceOrig = models.DecimalField(max_digits=15, decimal_places=2)
    nameDest = models.CharField(max_length=100)  # Destination account name
    oldbalanceDest = models.DecimalField(max_digits=15, decimal_places=2)
    newbalanceDest = models.DecimalField(max_digits=15, decimal_places=2)
    isFraud = models.BooleanField(default=False)
    isFlaggedFraud = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'Predictor'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.type} - {self.nameOrig} to {self.nameDest} - ${self.amount}"
    
    @property
    def balanceDiffOrg(self):
        return self.newbalanceOrig - self.oldbalanceOrg
    
    @property
    def balanceDiffDest(self):
        return self.newbalanceDest - self.oldbalanceDest
