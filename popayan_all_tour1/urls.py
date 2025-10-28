# popayan_all_tour1/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import RolViewSet, TipoEstablecimientoViewSet, UsuarioViewSet, HotelViewSet

# 🔹 Registramos los ViewSets en el router
router = DefaultRouter()
router.register(r'roles', RolViewSet)
router.register(r'tipos-establecimientos', TipoEstablecimientoViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'hoteles', HotelViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
