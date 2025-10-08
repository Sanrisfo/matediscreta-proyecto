from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Ticket
from itinerarios.models import Itinerario

@login_required
def detalle_ticket(request, ticket_id):
    """
    Ver ticket con código QR
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, itinerario__turista=request.user)
    
    # Generar QR si no existe
    if not ticket.codigo_qr:
        ticket.generar_qr()
        ticket.save()
    
    context = {
        'ticket': ticket,
    }
    return render(request, 'tickets/ticket_detail.html', context)


@login_required
def generar_ticket(request, itinerario_id):
    """
    Generar ticket para un itinerario
    """
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    # Verificar si ya tiene ticket
    if hasattr(itinerario, 'ticket'):
        ticket = itinerario.ticket
    else:
        # Crear nuevo ticket
        ticket = Ticket.objects.create(
            itinerario=itinerario,
            fecha_validez=itinerario.fecha_fin
        )
        ticket.generar_qr()
        ticket.save()
    
    return redirect('tickets:detalle', ticket_id=ticket.id)
