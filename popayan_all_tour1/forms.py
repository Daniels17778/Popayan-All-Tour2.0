from django import forms
from .models import Usuario, Roles, Hotel
from datetime import date
from django.core.exceptions import ValidationError


#formulario registro

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = [
            "email", "telefono", "password", "profesion",
            "nombre_completo", "identificacion", "fecha_nacimiento",
            "rol", "direccion", "tipo_establecimiento"
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🔹 Excluir "Administrador" del select
        self.fields["rol"].queryset = Roles.objects.exclude(rol__iexact="administrador")

    # 🔹 Validación personalizada para correo
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Correo ya registrado")
        return email

    # 🔹 Validación personalizada para teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        if Usuario.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Numero de teléfono en uso")
        if len(telefono) < 7:
            raise forms.ValidationError("Al menos 7 digitos")
        return telefono

    # 🔹 Validación personalizada para identificación
    def clean_identificacion(self):
        identificacion = self.cleaned_data.get("identificacion")
        if Usuario.objects.filter(identificacion=identificacion).exists():
            raise forms.ValidationError("Identificación ya registrada")
        return identificacion

    # 🔹 Validación de contraseña mínima
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 5:
            raise forms.ValidationError("Al menos 5 caracteres")
        return password

    # 🔹 Validación de edad mínima
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get("fecha_nacimiento")
        from datetime import date
        if fecha_nacimiento:
            edad = (date.today() - fecha_nacimiento).days // 365
            if edad < 16:
                raise forms.ValidationError("Debe ser mayor de 16 años")
        return fecha_nacimiento

    # 🔹 Guardar encriptando contraseña
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # 🔒 Encripta
        if commit:
            user.save()
        return user

#fin form

#perfil usuario
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["email", "password", "nombre_completo", "direccion", "telefono", "imagen_perfil"]
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }
#fin usuario

#formulario Hoteles
class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['nombre', 'descripcion', 'imagen', 'url_mas_info']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del hotel'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descripción detallada del hotel'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'url_mas_info': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com'
            })
        }
        
    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            if imagen.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("La imagen no puede ser mayor a 5MB.")
            
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            import os
            ext = os.path.splitext(imagen.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError("Solo se permiten archivos de imagen (jpg, jpeg, png, gif).")
        return imagen
#fin hoteles