# serializers.py
from rest_framework import serializers
from .models import Roles, TipoEstablecimiento, Usuario, Hotel


# 🔹 Serializer para Roles
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = "__all__"


# 🔹 Serializer para Tipo de Establecimiento
class TipoEstablecimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEstablecimiento
        fields = "__all__"


# 🔹 Serializer para Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)  # Mostrar datos del rol
    rol_id = serializers.PrimaryKeyRelatedField(
        queryset=Roles.objects.all(), source="rol", write_only=True
    )

    tipo_establecimiento = TipoEstablecimientoSerializer(read_only=True)  # Mostrar datos
    tipo_establecimiento_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoEstablecimiento.objects.all(),
        source="tipo_establecimiento",
        write_only=True,
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            "id",
            "email",
            "nombre_completo",
            "telefono",
            "profesion",
            "identificacion",
            "fecha_nacimiento",
            "direccion",
            "imagen_perfil",
            "rol", "rol_id",
            "tipo_establecimiento", "tipo_establecimiento_id",
            "is_active",
        ]


# 🔹 Serializer para Hotel
class HotelSerializer(serializers.ModelSerializer):
    empresario = UsuarioSerializer(read_only=True)
    empresario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source="empresario",
        write_only=True,
        required=False
    )

    class Meta:
        model = Hotel
        fields = [
            "id",
            "nombre",
            "descripcion",
            "imagen",
            "url_mas_info",
            "fecha_creacion",
            "activo",
            "empresario", "empresario_id"
        ]
