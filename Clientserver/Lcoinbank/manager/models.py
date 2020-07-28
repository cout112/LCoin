from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Accounts(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
	name = models.CharField(max_length=128)
	code = models.CharField(max_length=65)
	amount = models.DecimalField(max_digits=10,decimal_places=2, default=0.00)

	def __str__(self):
		return f"{self.user}: Account name {self.name} with {self.amount}"

# class Transactions(models.Model):
# 	origin = models.ForeignKey(Accounts, on_delete=models.CASCADE, related_name="money_sent")
# 	destination = models.ForeignKey(Accounts, on_delete=models.CASCADE, related_name="money_received")
# 	amount = models.DecimalField(max_digits=10, decimal_places=2)
	

# 	def __str__(self):
# 		return f"transaction from {self.origin} to {self.destination} for the amount of {self.amount}"



