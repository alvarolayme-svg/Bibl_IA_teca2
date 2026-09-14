from django import forms

from catalogo.models import Libro
from usuarios.models import Usuario


class PrestamoForm(forms.Form):
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(tipo_usuario__in=['estudiante', 'docente']).order_by('first_name'),
        label='Usuario',
    )
    libro = forms.ModelChoiceField(
        queryset=Libro.objects.filter(stock__gt=0).order_by('titulo'),
        label='Libro disponible',
    )
