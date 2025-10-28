from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.conf import settings


# tabla de roles
class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    rol = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Rol'
    )

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.rol


# tabla tipo Establecimiento
class TipoEstablecimiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Tipo de Establecimiento"
    )

    class Meta:
        db_table = "tipo_establecimiento"
        verbose_name = "Tipo de Establecimiento"
        verbose_name_plural = "Tipos de Establecimiento"

    def __str__(self):
        return self.nombre


# tabla usuario
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un correo electrónico")
        email = self.normalize_email(email)

        # Conversión automática de ids a instancias
        rol = extra_fields.get("rol")
        if rol and isinstance(rol, int):
            extra_fields["rol"] = Roles.objects.get(pk=rol)

        tipo = extra_fields.get("tipo_establecimiento")
        if tipo and isinstance(tipo, int):
            extra_fields["tipo_establecimiento"] = TipoEstablecimiento.objects.get(pk=tipo)

        extra_fields.setdefault("is_active", True)  # Activo por defecto
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if "fecha_nacimiento" not in extra_fields:
            extra_fields["fecha_nacimiento"] = "2000-08-07"

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")
        
        if "identificacion" not in extra_fields or not extra_fields["identificacion"]:
            extra_fields["identificacion"] = f"admin-{email}"

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    nombre_completo = models.CharField(max_length=255, verbose_name="Nombre completo")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    profesion = models.CharField(max_length=100, blank=True, null=True, verbose_name="Profesión")
    identificacion = models.CharField(max_length=50, unique=True, verbose_name="Identificación")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de nacimiento")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")

    # 🔹 Imagen de perfil
    imagen_perfil = models.ImageField(
        upload_to="usuarios/perfiles/",  # Carpeta dentro de MEDIA_ROOT
        blank=True,
        null=True,
        verbose_name="Imagen de perfil"
    )

    rol = models.ForeignKey(Roles, on_delete=models.CASCADE, verbose_name="Rol")
    tipo_establecimiento = models.ForeignKey(
        TipoEstablecimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Establecimiento"
    )

    # Campos administrativos
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre_completo", "rol"]

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.nombre_completo} ({self.email})"

    def clean(self):
        """Validación de negocio: Empresario debe tener tipo_establecimiento"""
        if self.rol and self.rol.rol.lower() == "empresario" and not self.tipo_establecimiento:
            raise ValidationError("Un empresario debe tener un tipo de establecimiento asignado.")

#Fin usuario

#modelo Hoteles
class Hotel(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Hotel")
    descripcion = models.TextField(verbose_name="Descripción")
    imagen = models.ImageField(upload_to="hoteles/", verbose_name="Imagen")
    url_mas_info = models.URLField(verbose_name="URL para más información")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")

    # CORREGIDO: limit_choices_to debe usar la relación correcta
    empresario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="hoteles",
        limit_choices_to={"rol__rol": "empresario"}  # 🔥 CORREGIDO: uso doble underscore para ForeignKey
    )
    
    class Meta:
        db_table = "hoteles"
        verbose_name = "Hotel"
        verbose_name_plural = "Hoteles"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.empresario.nombre_completo if self.empresario else 'Sin empresario'}"

#fin hoteles
