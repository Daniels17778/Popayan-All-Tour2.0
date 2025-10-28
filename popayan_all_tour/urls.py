"""
URL configuration for popayan_all_tour project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from popayan_all_tour1.views import registro,noticia, login_view, terminos, home, entretenimiento, perfilUser, semanas, procesiones, hoteles_publicos,login_view,logout_view, terminos, home, agregar_hotel, editar_hotel, eliminar_hotel, hoteles_view, redirect_by_role, historia, historia_1601_view, historia_1701_view, historia_1801_view, historia_1831_view, memory
from popayan_all_tour1.views import (
    CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registro', registro, name='registro'),
    path('', login_view, name='login'),
    path('terminos', terminos, name='terminos'),
    path('home', home, name='home'),
    path('noticia/', noticia, name='noticia'),
    path('semana/', semanas, name='semanaSanta'),
    path('procesiones/', procesiones, name='procesiones'),
    path('perfilUser', perfilUser, name='perfilUser'),
    path('entretenimiento', entretenimiento, name='entretenimiento'),
    path('recuperar/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('recuperar/enviado/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('recuperar/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('recuperar/completado/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('agregar-hotel/', agregar_hotel, name='agregar_hotel'),
    path('editar-hotel/<int:hotel_id>/', editar_hotel, name='editar_hotel'),
    path('eliminar-hotel/<int:hotel_id>/', eliminar_hotel, name='eliminar_hotel'),
    path('hoteles/', hoteles_view, name='hoteles_view'),
    path('redirect-by-role/', redirect_by_role, name='redirect_by_role'),
    path('logout/', logout_view, name='logout'),
    path("hoteles/", hoteles_publicos, name="hoteles_publicos"),
    path('memori', memory, name='memori'),
    path('histori/', historia, name='historia_1537'),
    path('historia-1601/', historia_1601_view, name='historia_1601'),
    path('historia-1701/', historia_1701_view, name='historia_1701'),
    path('historia-1801/', historia_1801_view, name='historia_1801'),
    path('historia-1831/', historia_1831_view, name='historia_1831'),
    path('juegaso/', lambda request: render(request, 'juegaso/juego.html'), name='juegaso'),
    path('menu/', lambda request: render(request, 'juegaso/menu.html'), name='menu'),
    path('creditos/', lambda request: render(request, 'juegaso/creditos.html'), name='creditos'),

    #coso api
    path("", include("popayan_all_tour1.urls"))

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

