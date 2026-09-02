"""Mixin para que los forms del portal rendericen con las clases de
Bootstrap 5 que trae el template Lexa, sin sumar una dependencia nueva
(django-crispy-forms/django-widget-tweaks). Cada form del portal lo agrega
como primer padre; el admin de Django y el panel de superadmin no lo usan."""

from django import forms


class BootstrapFieldsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_class = 'form-select'
            else:
                css_class = 'form-control'
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing} {css_class}'.strip()
