from django import forms
from .models import Card, Category


class CardForm(forms.ModelForm):
    """Form for creating / editing a card listing."""
    class Meta:
        model = Card
        fields = [
            'title', 'description', 'category',
            'set_name', 'edition', 'rarity', 'condition',
            'language', 'print_run', 'year', 'brand',
            'grading_company', 'grade', 'serial_number', 'population',
            'price', 'pricing_type', 'stock',
            'image', 'image_back',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class CategoryForm(forms.ModelForm):
    """Form for creating / editing categories (admin)."""
    class Meta:
        model = Category
        fields = ['name', 'parent', 'description', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class AdvancedSearchForm(forms.Form):
    """Advanced filtering for card search."""
    q = forms.CharField(required=False, label='Search', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search cards...'}
    ))
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False, empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    rarity = forms.ChoiceField(
        choices=[('', 'Any Rarity')] + Card.RARITY_CHOICES,
        required=False, widget=forms.Select(attrs={'class': 'form-select'}),
    )
    condition = forms.ChoiceField(
        choices=[('', 'Any Condition')] + Card.CONDITION_CHOICES,
        required=False, widget=forms.Select(attrs={'class': 'form-select'}),
    )
    grading_company = forms.ChoiceField(
        choices=[('', 'Any Grading')] + Card.GRADING_COMPANY_CHOICES,
        required=False, widget=forms.Select(attrs={'class': 'form-select'}),
    )
    brand = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Brand (e.g. Pokémon)'}
    ))
    min_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min $'}),
    )
    max_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max $'}),
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year'}),
    )
    sort = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('price', 'Price: Low → High'),
            ('-price', 'Price: High → Low'),
            ('title', 'Name: A → Z'),
            ('-views_count', 'Most Viewed'),
        ],
        required=False, initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
