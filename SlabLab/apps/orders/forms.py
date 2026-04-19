from django import forms


class CheckoutForm(forms.Form):
    """Shipping information for checkout."""
    shipping_name = forms.CharField(
        max_length=255, label='Full Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    shipping_address = forms.CharField(
        label='Address',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Street address', 'rows': 2})
    )
    shipping_city = forms.CharField(
        max_length=100, label='City',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    shipping_state = forms.CharField(
        max_length=100, label='State / Province', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'})
    )
    shipping_zip = forms.CharField(
        max_length=20, label='ZIP / Postal Code',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP Code'})
    )
    shipping_country = forms.CharField(
        max_length=100, label='Country', initial='United States',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'})
    )
    notes = forms.CharField(
        required=False, label='Order Notes',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any special instructions...', 'rows': 2})
    )
