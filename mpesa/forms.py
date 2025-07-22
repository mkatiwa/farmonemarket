
from django import forms

class PaymentForm(forms.Form):
    phone_number = forms.CharField(label='Phone Number', max_length=15)
    amount = forms.DecimalField(label='Amount', max_digits=10, decimal_places=2)