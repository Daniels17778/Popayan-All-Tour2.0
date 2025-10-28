from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistroUsuarioForm, UsuarioForm, HotelForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.middleware.csrf import rotate_token
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from .models import Hotel



# Create your views here.


#vista registro
def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegistroUsuarioForm()
    return render(request, "registro/registro.html", {"form": form})
#finregistro

#vista login
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            rotate_token(request)              # rota el CSRF al iniciar sesión
            return redirect("redirect_by_role")            # ✅ éxito: PRG -> form se limpia

        # ❌ error: también PRG para limpiar el form
        messages.error(request, "Correo o contraseña incorrectos")
        return redirect("login")

    # GET normal: form vacío
    return render(request, "login/login.html")
#fin login

#terminos y condiciones
def terminos(request): 
    return render(request, 'registro/terminosYcondiciones.html')
#fin terminos


#home
def home(request):
    return render(request, 'home.html')
#fin home

#entrtenimiento
def entretenimiento(request):
    return render(request, 'entretenimiento.html')
#fin
#perfil user
def perfilUser(request):
    return render(request, 'perfiluser.html')
#fin user

#semana santa
def semanas(request):
    return render(request,'semanaSanta/semana.html')
def procesiones(request):
    return render(request,'semanaSanta/procesiones.html')

#fin semana

#recuperar passwords
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password/password_reset.html'
    email_template_name = 'password/password_reset_email.html'
    subject_template_name = 'password/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password/password_reset_complete.html'

#fin password


#vista de personas al iniciar - FUNCIÓN ÚNICA CORREGIDA
@login_required
def redirect_by_role(request):
    """
    Redirige al usuario según su rol.
    Tu modelo Usuario tiene: rol = models.ForeignKey(Roles, ...)
    Y tu modelo Roles tiene: rol = models.CharField(...)
    """
    print("=" * 50)
    print("DEBUG REDIRECT_BY_ROLE")
    print("=" * 50)
    
    # Crear contexto básico
    context = {
        'usuario': request.user,
    }
    
    try:
        # Debug inicial
        print(f"Usuario: {request.user.nombre_completo} ({request.user.email})")
        print(f"Usuario ID: {request.user.id}")
        
        # Verificar si el usuario tiene rol asignado
        if not request.user.rol:
            print("❌ ERROR: Usuario sin rol asignado")
            context['error'] = 'Usuario sin rol asignado'
            return render(request, 'home.html', context)
        
        # Acceder al rol a través de la ForeignKey
        # request.user.rol es una instancia de Roles
        # request.user.rol.rol es el CharField con el nombre del rol
        user_role = request.user.rol.rol.strip().lower()
        print(f"✅ Rol del usuario: '{user_role}'")
        
        # Redirigir según el rol
        if user_role == 'empresario':
            print("✅ Es empresario - Cargando vista empresario...")
            try:
                hoteles = Hotel.objects.filter(empresario=request.user, activo=True)
                print(f"Hoteles encontrados: {hoteles.count()}")
                
                context['hoteles'] = hoteles
                
                # ⚠️ IMPORTANTE: Verificar que el template existe
                return render(request, 'vista_Empresario/V_empre.html', context)
                
            except Exception as e:
                print(f"❌ Error cargando hoteles: {e}")
                context['error'] = f'Error cargando hoteles: {str(e)}'
                return render(request, 'home.html', context)
            
        elif user_role == 'turista':
            print("✅ Es turista - Redirigiendo a home...")
            return render(request, 'home.html', context)
            
        elif user_role == 'administrador':
            print("✅ Es administrador - Cargando dashboard...")
            return render(request, 'ciudadano/dashboard.html', context)
            
        else:
            print(f"❌ Rol no reconocido: '{user_role}', redirigiendo a home")
            context['error'] = f'Rol no reconocido: {user_role}'
            return render(request, 'home.html', context)
            
    except AttributeError as e:
        print(f"❌ Error de atributo: {e}")
        print("Posible causa: Usuario sin rol o problema en la relación ForeignKey")
        context['error'] = f'Error de configuración de usuario: {str(e)}'
        return render(request, 'home.html', context)
    except Exception as e:
        print(f"❌ Error general en redirect_by_role: {e}")
        import traceback
        traceback.print_exc()
        context['error'] = f'Error del sistema: {str(e)}'
        return render(request, 'home.html', context)

#fin personas

#panel hotel
def vista(request):  # Vista principal de hoteles (manteniendo tu nombre original)
    """Vista para mostrar todos los hoteles"""
    hoteles = Hotel.objects.filter(activo=True)

    # Tu lógica original para botones de establecimiento
    botones = []
    if (request.user.is_authenticated and 
        hasattr(request.user, 'rol') and 
        request.user.rol and 
        request.user.rol.rol.lower() == 'empresario'):
        
        tipo = ""
        if hasattr(request.user, 'tipo_establecimiento') and request.user.tipo_establecimiento:
            tipo = request.user.tipo_establecimiento.nombre.lower()
            
        if "hotel" in tipo:
            botones.append({'nombre': 'Registrar Hotel', 'url': '/agregar-hotel/'})

    context = {
        'hoteles': hoteles,
        'botones_establecimiento': botones,
    }
    return render(request, 'sitios_de_interes/hoteles.html', context)

# Alias para mantener compatibilidad si usas hoteles_view en algún lugar
def hoteles_view(request):
    """Alias de la vista principal"""
    return vista(request)

@login_required
def agregar_hotel(request):
    """Vista para agregar un nuevo hotel"""
    # Verificar que sea empresario - CORREGIDO
    if (not request.user.rol or 
        request.user.rol.rol.strip().lower() != 'empresario'):
        messages.error(request, 'No tienes permisos para agregar hoteles.')
        return redirect('home')
    
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.empresario = request.user  # Asignar el empresario actual
            hotel.save()
            messages.success(request, f'Hotel "{hotel.nombre}" agregado exitosamente!')
            return redirect('redirect_by_role')  # Redirigir al panel del empresario
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = HotelForm()

    context = {
        'form': form,
        'titulo': 'Agregar Nuevo Hotel'
    }
    return render(request, 'sitios_de_interes/agregar_hotel.html', context)

@login_required
def editar_hotel(request, hotel_id):
    """Vista para editar un hotel del empresario"""
    hotel = get_object_or_404(Hotel, id=hotel_id, empresario=request.user)
    
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hotel "{hotel.nombre}" actualizado exitosamente!')
            return redirect('redirect_by_role')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = HotelForm(instance=hotel)
    
    context = {
        'form': form,
        'hotel': hotel,
        'titulo': f'Editar {hotel.nombre}'
    }
    return render(request, 'sitios_de_interes/agregar_hotel.html', context)

@login_required
def eliminar_hotel(request, hotel_id):
    """Vista para eliminar un hotel del empresario"""
    hotel = get_object_or_404(Hotel, id=hotel_id, empresario=request.user)
    
    if request.method == 'POST':
        nombre_hotel = hotel.nombre
        hotel.delete()
        messages.success(request, f'Hotel "{nombre_hotel}" eliminado exitosamente!')
        return redirect('redirect_by_role')
    
    context = {
        'hotel': hotel
    }
    return render(request, 'vistasEmpresario/confirmar_eliminar.html', context)


@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('login')

def hoteles_publicos(request):
    hoteles = Hotel.objects.all()
    puede_gestionar = request.user.is_authenticated and (request.user.rol == 'empresario' or request.user.is_staff)
    return render(request, "hoteles.html", {
        "hoteles": hoteles,
        "puede_gestionar": puede_gestionar
    })

data_por_ano = {
    1537: {
        "ano": 1537,
        "titulo": "Fundación de Popayán",
        "contenido": [
            "Fundada el 13 de enero de 1537 por el conquistador español Sebastián de Belalcázar, su ubicación estratégica entre Quito y Cartagena la convirtió en un punto clave para las rutas comerciales y militares del virreinato. Desde sus inicios, Popayán destacó por su organización administrativa, su influencia eclesiástica y su papel en la expansión de la corona española en América del Sur. Durante el periodo colonial, la ciudad se consolidó como un centro político, religioso y cultural. La llegada de órdenes religiosas como los franciscanos, dominicos y jesuitas permitió la construcción de iglesias, colegios y seminarios, lo que convirtió a Popayán en un bastión del catolicismo y la educación en el Nuevo Reino de Granada. ",
            "Figuras como el propio Belalcázar y otros encomenderos jugaron un rol determinante en el establecimiento del poder colonial, mientras que los pueblos indígenas locales, como los pubenenses, resistieron valientemente antes de ser sometidos a un nuevo orden social. La fundación de Popayán sentó las bases para el desarrollo del suroccidente colombiano y su historia permanece como un testimonio clave del proceso de conquista y colonización en América."
        ],
        "imagenes": {
            "left": "img-historia/1537_left.png",
            "right": "img-historia/1537_right.png"
        },
        "personajes": [
            {
                "nombre": "Sebastián de Belalcázar",
                "fecha": "1479–1551",
                "img_fondo": "img-historia/fondo_1.png",
                "img_sobre": "img-historia/sobre_1.png",
                "descripcion": "Fue el fundador de Popayán en 1537. Como conquistador español, estableció rutas estratégicas entre Quito y Cartagena, lo que consolidó la presencia española en el suroccidente colombiano."
            },
            {
                "nombre": "Juan de Ampudia",
                "fecha": "1479–1541",
                "img_fondo": "img-historia/fondo_2.png",
                "img_sobre": "img-historia/sobre_2.png",
                "descripcion": "Era uno de los capitanes de Belalcázar, participando activamente en la fundación de varias ciudades. Su papel militar fue esencial para controlar la región y someter a las comunidades indígenas."
            },
            {
                "nombre": "Lorenzo de Aldana",
                "fecha": "1508–1571",
                "img_fondo": "img-historia/fondo_3.png",
                "img_sobre": "img-historia/sobre_3.png",
                "descripcion": "Ejerciendo el cargo de gobernador interino tras Belalcázar, su administración ayudó a organizar el sistema colonial local y consolidar el poder español en la zona."
            }
        ],
        "datos_curiosos": [
            "El nombre Popayán proviene del cacique indígena Payán, señor del valle donde se asentaron los españoles",
            "La ciudad fue fundada tres veces: primero en Roldanillo, luego en El Tambo, y finalmente en su ubicación actual.",
            "Popayán fue originalmente pensada como un punto intermedio entre Quito y Cartagena, lo que le dio gran valor estratégico",
            "En sus primeros años, el oro de los ríos del Cauca era lavado por indígenas bajo el sistema de encomienda."
        ]
    },

    1601: {
        "ano": 1601,
        "titulo": "Consolidación de la iglesia",
        "contenido": [
            "Esta etapa, marcada por la institucionalización de la Iglesia Católica en la ciudad, estuvo caracterizada por una intensa actividad misionera, educativa y arquitectónica que definió su identidad religiosa y cultural. La fundación de la diócesis de Popayán en 1546 por el papa Paulo III, con la designación de fray Juan del Valle como su primer obispo, marcó el inicio de un proceso de organización eclesiástica que se afianzó en las décadas posteriores. Desde entonces, obispos, frailes y misioneros trabajaron activamente en la evangelización de la población indígena, la edificación de templos y conventos, y la estructuración de un modelo social basado en la moral católica.",
            "Uno de los acontecimientos clave fue la llegada y expansión de distintas órdenes religiosas. Los franciscanos fueron los primeros en establecerse, seguidos por los dominicos, quienes fundaron el convento de Santo Domingo, y más adelante los jesuitas, que construyeron colegios donde se impartía educación en gramática, latín, teología y filosofía. Estos espacios no solo formaban religiosos, sino también criollos e hijos de encomenderos que más adelante ocuparían cargos importantes en la administración colonial. La Iglesia, además, adquirió grandes extensiones de tierra y riquezas a través de donaciones y herencias, lo que le permitió ejercer una influencia política significativa en la región."
        ],
        "imagenes": {
            "right": "img-historia/anio_1601/1601.png"
        },
        "personajes": [
            {
                "nombre": "Fray Alonso de Zamora",
                "fecha": "1635 -1717 (Aproximación)",
                "img_fondo": "img-historia/anio_1601/fondo_1.png",
                "img_sobre": "img-historia/anio_1601/sobre_1.png",
                "descripcion": "Se data de él como uno de los primeros frailes dominicos que ayudó a establecer el poder de la Iglesia en Popayán, además de promover la evangelización de los indígenas."
            },
            {
                "nombre": "Juan del Valle",
                "fecha": "1500 - 1563",
                "img_fondo": "img-historia/anio_1601/fondo_2.png",
                "img_sobre": "img-historia/anio_1601/sobre_2.png",
                "descripcion": "Fue el primer obispo de Popayán (1546), y aunque anterior a 1601, su legado perduró al estructurar la diócesis y sentar bases para la educación religiosa.",
            },
        ],
        "datos_curiosos": [
            "Fue una de las primeras ciudades con una diócesis propia en el Nuevo Reino de Granada, desde 1546.",
            "Los franciscanos, dominicos y jesuitas compitieron por construir las iglesias más suntuosas, muchas de las cuales aún existen.",
            "En esa época, los misioneros viajaban hasta el Amazonas desde Popayán para evangelizar pueblos indígenas.",
            "Algunas familias criollas donaban grandes fortunas a la Iglesia para asegurar prestigio y poder local.",
        ]
    },

        1701: {
        "ano": 1701,
        "titulo": "Auge económico y minero",
        "contenido": [
            "Popayán vivió un periodo de gran esplendor económico durante el siglo XVIII, consolidándose como uno de los centros más importantes del Virreinato gracias a la minería de oro y al comercio. Su ubicación estratégica en la ruta entre Quito y Cartagena favoreció el tránsito de mercancías, metales preciosos y viajeros, convirtiéndola en un eje clave del suroccidente del virreinato. Las élites criollas, enriquecidas por la minería en Barbacoas y el Chocó, construyeron fastuosas casonas, templos y capillas, que aún hoy conservan el estilo colonial característico de la ciudad.",
            "Este auge económico permitió el desarrollo de una vida cultural y social sofisticada. Las familias aristocráticas promovieron la educación y el arte, y su influencia se hizo sentir en todos los ámbitos de la vida colonial. Aunque profundamente desigual, esta etapa marcó el crecimiento urbano de Popayán, sentando las bases de su arquitectura, su patrimonio y su posición como símbolo de poder y tradición en el suroccidente colombiano."
        ],
        "imagenes": {
            "left": "img-historia/anio_1701/1701_e.png",
            "right": "img-historia/anio_1701/1701_right.png"
        },
        "personajes": [
            {
                "nombre": "Antonio de la Torre y Miranda",
                "fecha": "1734  - 1805",
                "img_fondo": "img-historia/anio_1701/fondo_1.png",
                "img_sobre": "img-historia/anio_1701/sobre_1.png",
                "descripcion": "Fue un encomendero y empresario criollo destacado que impulsó la minería en la región del Cauca, enriqueciendo a la élite local."
            },
            {
                "nombre": "Francisco Antonio de Arboleda Salazar",
                "fecha": "1732  - 1793",
                "img_fondo": "img-historia/anio_1701/fondo_2.png",
                "img_sobre": "img-historia/anio_1701/sobre_2.png",
                "descripcion": "Fue un hacendado, militar y político neogranadino influyente de una familia poderosa de Popayán. Participó en la política colonial el cuál consolidó el poder de las élites criollas.",
            },
            {
                "nombre": "José Ignacio de Pombo",
                "fecha": "1761  - 1812",
                "img_fondo": "img-historia/anio_1701/fondo_3.png",
                "img_sobre": "img-historia/anio_1701/sobre_3.png",
                "descripcion": "Comerciante y político que pertenecía a una de las familias fundadoras. Su actividad económica fortaleció la ciudad como centro minero.",
            }
        ],
        "datos_curiosos": [
            "La ciudad fue escenario de tensiones entre realistas y patriotas, con figuras como Camilo Torres y José María Obando.",
            "Muchos próceres y líderes de la independencia nacieron o estudiaron en Popayán, como Francisco José de Caldas.",
            "La élite tradicionalmente apoyaba al rey, sin embargo, con estos sucesos apoyó a la causa libertadora.",
            "La ciudad sufrió saqueos y represalias en las guerras de independencia.",
        ]
    },
        1801: {
        "ano": 1801,
        "titulo": "Popayán en la independecia",
        "contenido": [
            "En esta ciudad nacieron figuras históricas de gran trascendencia, como Camilo Torres, sacerdote y líder revolucionario, y Francisco José de Caldas, científico, ingeniero y patriota. Ambos fueron esenciales en la lucha por la libertad y participaron activamente en los eventos que marcaron la independencia del país. El fervor patriótico que caracterizó a los habitantes de Popayán impulsó numerosas acciones para lograr la separación de España. Durante los años de la independencia, Popayán fue escenario de intensos enfrentamientos armados, pues su posición como centro político y militar la convirtió en un objetivo estratégico tanto para patriotas como para realistas.",
            "Uno de los momentos más críticos ocurrió en 1820, cuando Simón Bolívar envió al general José María Obando a liberar el Cauca. La ciudad fue nuevamente disputada en sangrientos combates, y Popayán, dividida entre partidarios del rey y defensores de la república, sufrió saqueos, incendios y profundas fracturas sociales. Las calles coloniales, hoy tranquilas y patrimoniales, fueron entonces testigos de luchas callejeras, arrestos masivos y persecuciones políticas. A pesar de la violencia y las transformaciones que sufrió, Popayán se mantuvo como un importante núcleo de resistencia y pensamiento revolucionario. Los ideales de libertad germinaron con fuerza en sus claustros, colegios y tertulias intelectuales, y su legado sigue siendo un pilar fundamental en la historia de la independencia de Colombia. La sangre derramada en sus plazas y los sacrificios de sus hijos libertarios son parte esencial del espíritu nacional."
        ],
        "imagenes": {
            "left": "img-historia/anio_1801/1801_left.png",
            "right": "img-historia/anio_1801/1801_right.png"
        },
        "personajes": [
            {
                "nombre": "Simón Bolivar",
                "fecha": "1783 - 1830",
                "img_fondo": "img-historia/anio_1801/fondo_1.png",
                "img_sobre": "img-historia/anio_1801/sobre_1.png",
                "descripcion": "Simón Bolívar fue clave en la independencia de Colombia, liderando batallas como la de Boyacá en 1819. Su lucha y visión por una América Latina unida lo convirtieron en el principal impulsor de la libertad en la región."
            },
            {
                "nombre": "Antonio Nariño",
                "fecha": "1765 - 1823",
                "img_fondo": "img-historia/anio_1801/fondo_2.png",
                "img_sobre": "img-historia/anio_1801/sobre_2.png",
                "descripcion": 'Conocido como "El Precursor", tradujo y difundió los derechos del hombre, promoviendo ideas republicanas y de libertad. Su valentía y compromiso lo llevaron a ser uno de los primeros en enfrentar el dominio español en el país.',
            },
            {
                "nombre": "Tomás Cipriano de Mosquera",
                "fecha": "1798 - 1878",
                "img_fondo": "img-historia/anio_1801/fondo_3.png",
                "img_sobre": "img-historia/anio_1801/sobre_3.png",
                "descripcion": "Líder de importantes reformas como la abolición de los diezmos y la desamortización de bienes eclesiásticos, promovió la modernización del Estado y la defensa de la soberanía nacional. Su firme carácter y visión lo convirtieron en un actor fundamental en la consolidación de la República.",
            }
        ],
        "datos_curiosos": [
            "La ciudad fue escenario de tensiones entre realistas y patriotas, con figuras como Camilo Torres y José María Obando.",
            "Muchos próceres y líderes de la independencia nacieron o estudiaron en Popayán, como Francisco José de Caldas.",
            "La élite tradicionalmente apoyaba al rey, sin embargo, con estos sucesos apoyó a la causa libertadora.",
            "La ciudad sufrió saqueos y represalias en las guerras de independencia.",
        ]
    },
        1831: {
        "ano": 1831,
        "titulo": "Fin de la Gran Colombia",
        "contenido": [
            "Para Popayán, una ciudad con fuerte tradición política y conservadora, representó un momento de gran agitación ya que había sido centro del poder colonial y que, tras la independencia, se encontró en medio de profundas transformaciones políticas. La disolución de la Gran Colombia, el ambicioso proyecto integracionista de Simón Bolívar, trajo consigo una ruptura en el orden político que afectó directamente la estructura territorial y el rol que Popayán había desempeñado hasta entonces. La ciudad, que había pertenecido al Departamento del Cauca dentro de esa república, pasó a formar parte de la Nueva Granada, en un proceso cargado de tensiones ideológicas y disputas por el poder regional.",
            "En las calles de Popayán, el pueblo vivía con incertidumbre. El final del proyecto de la Gran Colombia no solo implicaba un nuevo mapa político, sino también una reorganización de los impuestos, la justicia, el comercio y las lealtades militares. La ciudad mantenía su arquitectura colonial y su estructura social jerárquica, pero ya se vislumbraban los conflictos que marcarían el siglo XIX: guerras civiles, disputas entre caudillos regionales y la lucha entre Iglesia y Estado."
        ],

#si llega a poner imagenes ese boludo, se ponen aqui abajo 

        "personajes": [
            {
                "nombre": "José Hilario López",
                "fecha": "1798 - 1869",
                "img_fondo": "img-historia/anio_1831/fondo_1.png",
                "img_sobre": "img-historia/anio_1831/sobre_1.png",
                "descripcion": "Nacido en Popayán en 1798, fue presidente de Colombia y líder liberal. Participó en las guerras de independencia desde joven. Como presidente, abolió la esclavitud en 1851. Promovió reformas agrarias y educativas. Representó la transición del poder desde Popayán hacia un Estado más moderno."
            },
            {
                "nombre": "Julio Arboleda Pombo",
                "fecha": "1817 - 1862",
                "img_fondo": "img-historia/anio_1831/fondo_2.png",
                "img_sobre": "img-historia/anio_1831/sobre_2.png",
                "descripcion": "Poeta, político y militar conservador nacido en 1817 en Popayán. Defensor del orden tradicional, fue presidente del Estado Soberano del Cauca. También dirigió fuerzas en guerras civiles. Su obra literaria y liderazgo político influyeron en la identidad regional. Murió asesinado en 1862 durante conflictos internos.",
            },
            {
                "nombre": "Manuel María Mosquera y Arboleda",
                "fecha": "1800 - 1882",
                "img_fondo": "img-historia/anio_1831/fondo_3.png",
                "img_sobre": "img-historia/anio_1831/sobre_3.png",
                "descripcion": "Fue diplomático, político y arzobispo destacado en el siglo XIX colombiano. Hijo del expresidente Joaquín Mosquera, perteneció a una de las familias más influyentes de la época. Se desempeñó como representante diplomático en varias misiones internacionales y fue designado Arzobispo de Bogotá en 1859.",
            }
        ],
        "datos_curiosos": [
            "Con la disolución de la Gran Colombia, Popayán pasó a ser parte del Estado Soberano del Cauca, uno de los más grandes.",
            "El Estado del Cauca tenía tanto poder que llegó a tener su propia constitución y ejército."        ]
    },

        1885: {
        "ano": 1885,
        "titulo": "Guerra civil y la centralización del poder",
        "contenido": [
            "La guerra civil de 1885 surgió como reacción a las reformas liberales y al federalismo que habían dominado décadas anteriores. Las élites de Popayán, ligadas fuertemente a la Iglesia y al poder conservador, se resistieron a la pérdida de influencia que trajo consigo el modelo federalista. Durante el conflicto, la ciudad fue escenario de movilizaciones armadas, enfrentamientos y profundas divisiones internas. Muchos de sus ciudadanos se alistaron en las filas conservadoras, defendiendo un modelo centralista que devolviera el control político al gobierno nacional, alineado con la doctrina católica y el orden tradicional.",
            "Tras la victoria del bando conservador, se impuso una nueva constitución en 1886, que eliminó los Estados Soberanos y fortaleció el poder central en Bogotá. Con ello, Popayán perdió parte de su autonomía política, pero conservó su relevancia cultural y religiosa. El clero, las familias influyentes y las instituciones educativas como el Seminario Mayor y los colegios católicos reforzaron su papel en la formación de las nuevas generaciones bajo los valores del orden conservador."
        ],
        # ARREGLAR ESTA HP COSA QUE ME HIZO PONER EL HP DE ALEJANDRO 
        "imagenes": {
            "left": "img-historia/anio_1885/1885_a.png",
            "right": "img-historia/anio_1885/1885_e.png"
        },
        "personajes": [
            {
                "nombre": "Miguel Arroyo Hurtado",
                "fecha": "1838 - 1890",
                "img_fondo": "img-historia/anio_1885/fondo_1.png",
                "img_sobre": "img-historia/anio_1885/sobre_1.png",
                "descripcion": "Participó en la guerra civil de 1885 como líder de fuerzas conservadoras en el Cauca. Tras el conflicto, ocupó cargos regionales en representación del nuevo gobierno central, encarnando el papel que jugaron los militares locales en la consolidación del orden conservador."
            },
            {
                "nombre": "José María Quijano Wallis",
                "fecha": "1870 - 1923",
                "img_fondo": "img-historia/anio_1885/fondo_2.png",
                "img_sobre": "img-historia/anio_1885/sobre_2.png",
                "descripcion": 'Representó el pensamiento conservador tradicionalista y fue cercano a las posturas que apoyaban la centralización. Su influencia fue notable en los debates legales y constitucionales que siguieron a la guerra civil.',
            },
            {
                "nombre": "Manuel Antonio Arboleda Scarpetta",
                "fecha": "1847 - 1922",
                "img_fondo": "img-historia/anio_1885/fondo_3.png",
                "img_sobre": "img-historia/anio_1885/sobre_3.png",
                "descripcion": "Ejerció como rector de la Universidad del Cauca y participó activamente en la vida intelectual de la ciudad durante las décadas posteriores a la independencia. Durante la guerra civil de 1885, Quijano defendió abiertamente la causa centralista y conservadora, considerando que el federalismo debilitaba la unidad nacional y la moral católica.",
            }
        ],
        "datos_curiosos": [
            "El conflicto provocó el cierre temporal de escuelas y seminarios, pero la Iglesia los retomó rápidamente.",
            "Muchos patojos ricos estudiaban en Europa, pero regresaban para reforzar el modelo colonialista local.",
            "Durante esta época surgieron publicaciones políticas y literarias en Popayán que promovían ideales católicos y orden social.",
        ]
    },
        1937: {
        "ano": 1937,
        "titulo": "Celebración del IV Centenario",
        "contenido": [
            "La celebración del IV Centenario impulsó la recuperación y embellecimiento del centro histórico, reafirmando a Popayán como una de las joyas patrimoniales de Colombia. Se restauraron edificios coloniales, se levantaron monumentos conmemorativos y se promovieron publicaciones académicas que recogieron su historia. Además, este aniversario consolidó el papel de la ciudad como bastión conservador y centro espiritual del suroccidente colombiano, en un momento en que el país atravesaba tensiones sociales y políticas.",
            "Más allá de la festividad, el IV Centenario se convirtió en un símbolo de continuidad entre el pasado y el presente, resaltando la riqueza cultural de Popayán y su vocación intelectual. Fue también una oportunidad para proyectar la ciudad hacia el futuro, celebrando no solo lo que había sido, sino lo que aspiraba a seguir siendo: un referente de tradición, belleza arquitectónica y conciencia histórica."
        ],

        "imagenes": {
            "left": "img-historia/anio_1937/1937_dere.png",
            "right": "img-historia/anio_1937/1937_dere_2.png"
        },
        "personajes": [
            {
                "nombre": "Guillermo Valencia",
                "fecha": "1873 - 1943",
                "img_fondo": "img-historia/anio_1937/fondo_1.png",
                "img_sobre": "img-historia/anio_1937/sobre_1.png",
                "descripcion": "Su presencia y obra reforzaron el aura intelectual y conservadora de Popayán durante las celebraciones. Era considerado símbolo del refinamiento literario y de la tradición patricia de la ciudad."
            },
            {
                "nombre": "Rafael Maya",
                "fecha": "1897 - 1980",
                "img_fondo": "img-historia/anio_1937/fondo_2.png",
                "img_sobre": "img-historia/anio_1937/sobre_2.png",
                "descripcion": 'Participó en la vida cultural de la ciudad en los años 30, y su obra periodística e intelectual se alineaba con el espíritu de exaltación patrimonial e histórica que marcó la conmemoración.',
            },
            {
                "nombre": "Carlos Albán",
                "fecha": "1888 - 1947",
                "img_fondo": "img-historia/anio_1937/fondo_3.png",
                "img_sobre": "img-historia/anio_1937/sobre_3.png",
                "descripcion": "Fue parte del movimiento que promovió investigaciones y publicaciones sobre la historia de la ciudad para conmemorar sus 400 años. Su trabajo ayudó a consolidar la memoria histórica que se destacó en las celebraciones.",
            }
        ],
        "datos_curiosos": [
            "Se construyó el puente del Humilladero, símbolo arquitectónico de la ciudad, para conectar la ciudad alta con la baja.",
            "Durante la conmemoración se revivieron costumbres coloniales como los bailes de salón y vestimenta de época.",
            "Guillermo Valencia, además de poeta, fue embajador y candidato presidencial, y su casa hoy es museo histórico.",
            "Popayán era vista como una ciudad de élite, donde pocas familias concentraban poder político y cultural.",
        ]
    },
        1983: {
        "ano": '1983',
        "titulo": "Terremoto del 31 de marzo",
        "contenido": [
            "El terremoto del 31 de marzo de 1983 marcó un antes y un después en la historia de Popayán, dejando una huella profunda tanto en su arquitectura como en la memoria colectiva de sus habitantes. Aquel Jueves Santo, cuando la ciudad se preparaba para una de las celebraciones religiosas más emblemáticas del país, un sismo de magnitud 5.5 sacudió su territorio con una fuerza inesperada. En pocos segundos, gran parte del centro histórico quedó reducido a escombros. Iglesias, casonas coloniales, calles empedradas y edificios patrimoniales, que durante siglos habían resistido el paso del tiempo, se derrumbaron bajo la violencia de la tierra.",
            "El impacto humano fue igualmente devastador: centenares de muertos, miles de heridos y un número significativo de damnificados que perdieron no solo sus hogares, sino también su tranquilidad y seguridad. La ciudad quedó sumida en el caos, pero al mismo tiempo, el desastre despertó una ola de solidaridad nacional e internacional sin precedentes. Arquitectos, historiadores, ingenieros y ciudadanos de todo el país se unieron en un esfuerzo común por reconstruir Popayán, conservando su esencia colonial y su identidad cultural. La tragedia reveló tanto la fragilidad de un patrimonio edificado como la fortaleza de una comunidad decidida a renacer. Gracias a ese espíritu colectivo, Popayán logró recuperar buena parte de su arquitectura tradicional, convirtiéndose en un símbolo de resiliencia urbana y patrimonial."
        ],

        "imagenes": {
            "right": "img-historia/anio_1983/1983.png"
        },
        "personajes": [
            {
                "nombre": "Gustavo Wilches-Chaux",
                "fecha": "1954 - Actualidad",
                "img_fondo": "img-historia/anio_1937/fondo_1.png",
                "img_sobre": "img-historia/anio_1937/sobre_1.png",
                "descripcion": "Fue uno de los primeros en reflexionar profundamente sobre el concepto de “gestión del riesgo” a partir de la experiencia del terremoto de 1983. Su pensamiento influyó en políticas de prevención y manejo de desastres no solo en Popayán, sino a nivel nacional."
            },
            {
                "nombre": "Rafael Maya",
                "fecha": "1897 - 1980",
                "img_fondo": "img-historia/anio_1937/fondo_2.png",
                "img_sobre": "img-historia/anio_1937/sobre_2.png",
                "descripcion": 'Participó en la vida cultural de la ciudad en los años 30, y su obra periodística e intelectual se alineaba con el espíritu de exaltación patrimonial e histórica que marcó la conmemoración.',
            },
            {
                "nombre": "Carlos Albán",
                "fecha": "1888 - 1947",
                "img_fondo": "img-historia/anio_1937/fondo_3.png",
                "img_sobre": "img-historia/anio_1937/sobre_3.png",
                "descripcion": "Fue parte del movimiento que promovió investigaciones y publicaciones sobre la historia de la ciudad para conmemorar sus 400 años. Su trabajo ayudó a consolidar la memoria histórica que se destacó en las celebraciones.",
            }
        ],
        "datos_curiosos": [
            "Se construyó el puente del Humilladero, símbolo arquitectónico de la ciudad, para conectar la ciudad alta con la baja.",
            "Durante la conmemoración se revivieron costumbres coloniales como los bailes de salón y vestimenta de época.",
            "Guillermo Valencia, además de poeta, fue embajador y candidato presidencial, y su casa hoy es museo histórico.",
            "Popayán era vista como una ciudad de élite, donde pocas familias concentraban poder político y cultural.",
        ]
    },

}
def historia(request, ano=1537):
    datos = data_por_ano.get(ano, data_por_ano[1537])  # Fallback al 1537 si no existe el año
    return render(request, 'historia.html', {'datos': datos})

def historia_1601_view(request, ano=1601):
    datos = data_por_ano.get(ano, data_por_ano[1601])  # Fallback al 1537 si no existe el año
    return render(request, 'historia_1601.html', {'datos': datos})

def historia_1701_view(request, ano=1701):
    datos = data_por_ano.get(ano, data_por_ano[1701])  # Fallback al 1537 si no existe el año
    return render(request, 'historia_1701.html', {'datos': datos})

def historia_1801_view(request, ano=1801):
    datos = data_por_ano.get(ano, data_por_ano[1801])  # Fallback al 1537 si no existe el año
    return render(request, 'historia_1801.html', {'datos': datos})

def historia_1831_view(request, ano=1831):
    datos = data_por_ano.get(ano, data_por_ano[1831])  # Fallback al 1537 si no existe el año
    return render(request, 'historia_1831.html', {'datos': datos})

def historia_1885_view(request, ano=1885):
    datos = data_por_ano.get(ano, data_por_ano[1885])  # Fallback al 1537 si no existe el año
    return render(request, 'historia_1831.html', {'datos': datos})

def historia_1937_view(request, ano=1937):
    datos = data_por_ano.get(ano, data_por_ano[1937])  # Fallback al 1537 si no existe el año
    return render(request, 'historia_1831.html', {'datos': datos})

def historia_1983_view(request, ano=1983):
    datos = data_por_ano.get(ano, data_por_ano[1983])  # Fallback al 1537 si no existe el año
    return render(request, 'historia_1983.html', {'datos': datos})

def memory(request):
    return render(request, 'juego_de_memoria/index.html')

def creditos(request):
    return render(request, 'juegaso/creditos.html')
def menu(request):
    return render(request, 'juegaso/menu.html')
def juegaso(request):
    return render(request, 'juegaso/juego.html')

def noticia(request):
    return render(request, 'noticia.html')