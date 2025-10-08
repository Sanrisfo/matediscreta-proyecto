import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

def generar_codigo_qr(ticket):
    '''
    Genera un código QR para el ticket
    '''
    # Crear objeto QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Datos del QR (puede ser URL, JSON, etc.)
    datos_qr = f"RUBER-TICKET-{ticket.codigo}"
    qr.add_data(datos_qr)
    qr.make(fit=True)
    
    # Crear imagen
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar en BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Guardar en el campo del modelo
    filename = f'ticket_{ticket.codigo}.png'
    ticket.codigo_qr.save(filename, File(buffer), save=False)
    
    return ticket

# Actualizar método en el modelo Ticket:
def generar_qr(self):
    from .qr_generator import generar_codigo_qr
    generar_codigo_qr(self)