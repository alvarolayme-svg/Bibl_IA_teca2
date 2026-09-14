import csv

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from catalogo.forms import LibroForm
from catalogo.models import Libro
from prestamos.forms import PrestamoForm
from prestamos.models import Multa, Notificacion, Prestamo, Reserva
from prestamos.services import (
    ReglaPrestamoError,
    actualizar_sistema,
    crear_prestamo,
    registrar_devolucion,
)
from usuarios.forms import RegistroEstudianteForm


def es_administrador(usuario):
    return usuario.is_authenticated and (
        usuario.is_staff or usuario.is_superuser or usuario.tipo_usuario == 'administrador'
    )


administrador_requerido = user_passes_test(es_administrador)


def inicio(request):
    if request.user.is_authenticated:
        return redirect('panel')
    consulta = request.GET.get('q', '').strip()
    libros = Libro.objects.filter(stock__gte=0).order_by('titulo')
    if consulta:
        libros = libros.filter(titulo__icontains=consulta) | libros.filter(autor__icontains=consulta)
    return render(request, 'inicio.html', {
        'libros': libros[:6],
        'consulta': consulta,
        'total_libros': Libro.objects.count(),
        'total_disponibles': Libro.objects.filter(stock__gt=0).count(),
    })


def registro(request):
    if request.user.is_authenticated:
        return redirect('panel')
    form = RegistroEstudianteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, 'Tu cuenta de estudiante fue creada correctamente.')
        return redirect('panel')
    return render(request, 'registration/registro.html', {'form': form})


def salir(request):
    """Cierra la sesion actual y vuelve al acceso publico."""
    logout(request)
    messages.info(request, 'Sesion cerrada.')
    return redirect('inicio')


@login_required
def panel(request):
    actualizar_sistema()
    if es_administrador(request.user):
        prestamos = Prestamo.objects.select_related('usuario', 'libro').order_by('-fecha_prestamo')
        return render(request, 'panel_admin.html', {
            'prestamos_recientes': prestamos[:6],
            'total_titulos': Libro.objects.count(),
            'total_ejemplares': Libro.objects.aggregate(total=Sum('stock'))['total'] or 0,
            'prestamos_activos': prestamos.filter(estado='activo').count(),
            'prestamos_vencidos': prestamos.filter(estado='vencido').count(),
            'multas_pendientes': Multa.objects.filter(pagada=False).aggregate(total=Sum('monto'))['total'] or 0,
            'categorias': Libro.objects.values('categoria').annotate(total=Count('id')).order_by('-total')[:5],
            'notificaciones': Notificacion.objects.filter(leida=False).count(),
        })

    prestamos = Prestamo.objects.filter(usuario=request.user).select_related('libro').order_by('-fecha_prestamo')
    return render(request, 'panel_usuario.html', {
        'prestamos': prestamos.filter(estado__in=['activo', 'vencido']),
        'historial': prestamos.filter(estado='devuelto')[:5],
        'reservas': Reserva.objects.filter(usuario=request.user, estado='pendiente').select_related('libro'),
        'notificaciones': Notificacion.objects.filter(usuario=request.user, leida=False)[:4],
        'limite_restante': max(0, request.user.limite_prestamos - prestamos.filter(estado__in=['activo', 'vencido']).count()),
    })


def catalogo(request):
    consulta = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    libros = Libro.objects.all().order_by('titulo')
    if consulta:
        libros = libros.filter(titulo__icontains=consulta) | libros.filter(autor__icontains=consulta) | libros.filter(categoria__icontains=consulta)
    if categoria:
        libros = libros.filter(categoria=categoria)
    return render(request, 'catalogo.html', {
        'libros': libros,
        'consulta': consulta,
        'categoria_actual': categoria,
        'categorias': Libro.objects.values_list('categoria', flat=True).distinct().order_by('categoria'),
    })


@administrador_requerido
def administrar_libros(request, libro_id=None):
    libro = get_object_or_404(Libro, pk=libro_id) if libro_id else None
    form = LibroForm(request.POST or None, instance=libro)
    if request.method == 'POST' and form.is_valid():
        item = form.save()
        messages.success(request, f'El libro {item.titulo} fue guardado.')
        return redirect('administrar_libros')
    return render(request, 'administrar_libros.html', {
        'form': form,
        'libro_editando': libro,
        'libros': Libro.objects.all().order_by('titulo'),
    })


@administrador_requerido
def administrar_prestamos(request):
    actualizar_sistema()
    form = PrestamoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            prestamo = crear_prestamo(form.cleaned_data['usuario'], form.cleaned_data['libro'])
            messages.success(request, f'Prestamo registrado. Fecha limite: {prestamo.fecha_limite:%d/%m/%Y}.')
            return redirect('administrar_prestamos')
        except ReglaPrestamoError as error:
            form.add_error(None, str(error))
    return render(request, 'administrar_prestamos.html', {
        'form': form,
        'prestamos': Prestamo.objects.select_related('usuario', 'libro').order_by('-fecha_prestamo'),
    })


@administrador_requerido
def devolver_prestamo(request, prestamo_id):
    if request.method != 'POST':
        return HttpResponseForbidden('Accion no permitida.')
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)
    try:
        retraso = registrar_devolucion(prestamo)
        mensaje = 'Devolucion registrada sin multa.' if not retraso else f'Devolucion registrada con {retraso} dia(s) de retraso.'
        messages.success(request, mensaje)
    except ReglaPrestamoError as error:
        messages.error(request, str(error))
    return redirect('administrar_prestamos')


@login_required
def mis_prestamos(request):
    actualizar_sistema()
    prestamos = Prestamo.objects.filter(usuario=request.user).select_related('libro').order_by('-fecha_prestamo')
    return render(request, 'mis_prestamos.html', {
        'prestamos': prestamos,
        'multas': Multa.objects.filter(prestamo__usuario=request.user, pagada=False).select_related('prestamo__libro'),
    })


@login_required
def crear_reserva(request, libro_id):
    if request.method != 'POST':
        return HttpResponseForbidden('Accion no permitida.')
    if es_administrador(request.user):
        messages.error(request, 'Las reservas estan disponibles para estudiantes y docentes.')
        return redirect('catalogo')
    libro = get_object_or_404(Libro, pk=libro_id)
    if libro.stock > 0:
        messages.info(request, 'Este libro esta disponible. Solicita el prestamo en biblioteca.')
    elif Reserva.objects.filter(usuario=request.user, libro=libro, estado='pendiente').exists():
        messages.info(request, 'Ya tienes una reserva pendiente para este libro.')
    else:
        Reserva.objects.create(usuario=request.user, libro=libro)
        messages.success(request, 'Reserva registrada. Te avisaremos cuando haya un ejemplar disponible.')
    return redirect('catalogo')


@login_required
def reservas(request):
    if es_administrador(request.user):
        reservas_lista = Reserva.objects.select_related('usuario', 'libro').order_by('estado', '-fecha_reserva')
        return render(request, 'reservas_admin.html', {'reservas': reservas_lista})
    return render(request, 'reservas.html', {
        'reservas': Reserva.objects.filter(usuario=request.user).select_related('libro').order_by('-fecha_reserva')
    })


@administrador_requerido
def actualizar_reserva(request, reserva_id, accion):
    if request.method != 'POST' or accion not in ('atendida', 'cancelada'):
        return HttpResponseForbidden('Accion no permitida.')
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    reserva.estado = accion
    reserva.save(update_fields=['estado'])
    messages.success(request, f'Reserva marcada como {accion}.')
    return redirect('reservas')


@login_required
def notificaciones(request):
    actualizar_sistema()
    if request.method == 'POST':
        Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        messages.success(request, 'Las notificaciones fueron marcadas como leidas.')
        return redirect('notificaciones')
    return render(request, 'notificaciones.html', {
        'notificaciones': Notificacion.objects.filter(usuario=request.user)
    })


@administrador_requerido
def reportes(request):
    actualizar_sistema()
    por_categoria = list(Libro.objects.values('categoria').annotate(total=Count('id')).order_by('-total'))
    return render(request, 'reportes.html', {
        'por_categoria': por_categoria,
        'usuarios_por_tipo': list(
            Prestamo.objects.values('usuario__tipo_usuario').annotate(total=Count('id')).order_by('-total')
        ),
        'libros_populares': Prestamo.objects.values('libro__titulo').annotate(total=Count('id')).order_by('-total')[:5],
        'total_prestamos': Prestamo.objects.count(),
        'total_devueltos': Prestamo.objects.filter(estado='devuelto').count(),
    })


@administrador_requerido
def exportar_reporte_prestamos(request):
    actualizar_sistema()
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = 'attachment; filename="reporte_prestamos.csv"'
    respuesta.write('\ufeff')
    escritor = csv.writer(respuesta)
    escritor.writerow(['Usuario', 'Tipo', 'Libro', 'Fecha prestamo', 'Fecha limite', 'Devolucion', 'Estado'])
    prestamos = Prestamo.objects.select_related('usuario', 'libro').order_by('-fecha_prestamo')
    for prestamo in prestamos:
        escritor.writerow([
            prestamo.usuario.get_full_name() or prestamo.usuario.username,
            prestamo.usuario.tipo_usuario,
            prestamo.libro.titulo,
            prestamo.fecha_prestamo,
            prestamo.fecha_limite,
            prestamo.fecha_devolucion or '',
            prestamo.estado,
        ])
    return respuesta
