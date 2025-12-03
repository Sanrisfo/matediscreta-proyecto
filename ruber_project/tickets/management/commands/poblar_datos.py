from django.core.management.base import BaseCommand
from lugares.models import Categoria, Destino, Actividad
from rutas.models import Ruta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Poblar base de datos con datos de prueba de Lima'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Iniciando carga de datos de prueba...')
        
        # ===== CREAR CATEGORÍAS =====
        self.stdout.write('📁 Creando categorías...')
        categorias_data = [
            {'nombre': 'Playas', 'icono': 'fas fa-umbrella-beach', 'descripcion': 'Destinos de playa y mar'},
            {'nombre': 'Museos', 'icono': 'fas fa-landmark', 'descripcion': 'Museos y galerías de arte'},
            {'nombre': 'Gastronomía', 'icono': 'fas fa-utensils', 'descripcion': 'Restaurantes y mercados'},
            {'nombre': 'Aventura', 'icono': 'fas fa-mountain', 'descripcion': 'Deportes y aventura'},
            {'nombre': 'Vida Nocturna', 'icono': 'fas fa-cocktail', 'descripcion': 'Bares y discotecas'},
            {'nombre': 'Naturaleza', 'icono': 'fas fa-tree', 'descripcion': 'Parques y naturaleza'},
        ]
        
        for cat_data in categorias_data:
            cat, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  ✓ {cat.nombre}')
        
        # ===== CREAR DESTINOS =====
        self.stdout.write('📍 Creando destinos turísticos...')
        
        # Obtener categorías
        playa_cat = Categoria.objects.get(nombre='Playas')
        museo_cat = Categoria.objects.get(nombre='Museos')
        gastro_cat = Categoria.objects.get(nombre='Gastronomía')
        aventura_cat = Categoria.objects.get(nombre='Aventura')
        naturaleza_cat = Categoria.objects.get(nombre='Naturaleza')
        
        destinos_data = [
            {
                'nombre': 'Playa Costa Verde',
                'descripcion': 'Hermosa playa en el malecón de Miraflores con vista al océano Pacífico. Ideal para surfear, correr o simplemente relajarse.',
                'categoria': playa_cat,
                'latitud': Decimal('-12.119100'),
                'longitud': Decimal('-77.035000'),
                'direccion': 'Malecón Cisneros, Miraflores',
                'costo_entrada': Decimal('0.00'),
                'tiempo_visita_estimado': 120,
                'calificacion': Decimal('4.5'),
                'tags_preferencias': ['playa', 'relax', 'aventura']
            },
            {
                'nombre': 'Museo Larco',
                'descripcion': 'Museo con la colección más completa de arte precolombino del Perú. Incluye sala erótica y hermosos jardines.',
                'categoria': museo_cat,
                'latitud': Decimal('-12.069400'),
                'longitud': Decimal('-77.071200'),
                'direccion': 'Av. Bolívar 1515, Pueblo Libre',
                'costo_entrada': Decimal('30.00'),
                'tiempo_visita_estimado': 90,
                'calificacion': Decimal('4.8'),
                'tags_preferencias': ['museos', 'cultura']
            },
            {
                'nombre': 'Mercado de Surquillo',
                'descripcion': 'Mercado tradicional limeño famoso por sus jugos frescos y comida peruana auténtica a precios populares.',
                'categoria': gastro_cat,
                'latitud': Decimal('-12.111500'),
                'longitud': Decimal('-77.027700'),
                'direccion': 'Pasaje Raygada, Surquillo',
                'costo_entrada': Decimal('0.00'),
                'tiempo_visita_estimado': 60,
                'calificacion': Decimal('4.3'),
                'tags_preferencias': ['gastronomia']
            },
            {
                'nombre': 'Parque Kennedy',
                'descripcion': 'Parque central de Miraflores, famoso por sus gatos y ambiente bohemio. Rodeado de cafés y artesanos.',
                'categoria': naturaleza_cat,
                'latitud': Decimal('-12.120900'),
                'longitud': Decimal('-77.029700'),
                'direccion': 'Av. Larco, Miraflores',
                'costo_entrada': Decimal('0.00'),
                'tiempo_visita_estimado': 45,
                'calificacion': Decimal('4.2'),
                'tags_preferencias': ['naturaleza', 'relax']
            },
            {
                'nombre': 'Larcomar',
                'descripcion': 'Centro comercial al aire libre con vista al mar. Restaurantes, tiendas y entretenimiento con vista espectacular.',
                'categoria': gastro_cat,
                'latitud': Decimal('-12.131600'),
                'longitud': Decimal('-77.030000'),
                'direccion': 'Malecón de la Reserva 610, Miraflores',
                'costo_entrada': Decimal('0.00'),
                'tiempo_visita_estimado': 90,
                'calificacion': Decimal('4.6'),
                'tags_preferencias': ['gastronomia', 'compras', 'vida_nocturna']
            },
            {
                'nombre': 'Circuito Mágico del Agua',
                'descripcion': 'Parque con 13 fuentes ornamentales cibernéticas. Espectáculo de luces, agua y música por las noches.',
                'categoria': aventura_cat,
                'latitud': Decimal('-12.073500'),
                'longitud': Decimal('-77.052300'),
                'direccion': 'Jr. Madre de Dios, Cercado de Lima',
                'costo_entrada': Decimal('4.00'),
                'tiempo_visita_estimado': 75,
                'calificacion': Decimal('4.4'),
                'tags_preferencias': ['aventura', 'naturaleza']
            },
        ]
        
        destinos_creados = []
        for dest_data in destinos_data:
            destino, created = Destino.objects.get_or_create(
                nombre=dest_data['nombre'],
                defaults=dest_data
            )
            destinos_creados.append(destino)
            if created:
                self.stdout.write(f'  ✓ {destino.nombre}')
        
        # ===== CREAR ACTIVIDADES =====
        self.stdout.write(' Creando actividades...')
        
        playa_costa_verde = Destino.objects.get(nombre='Playa Costa Verde')
        museo_larco = Destino.objects.get(nombre='Museo Larco')
        mercado = Destino.objects.get(nombre='Mercado de Surquillo')
        
        actividades_data = [
            {
                'destino': playa_costa_verde,
                'nombre': 'Clases de Surf',
                'tipo': 'deporte',
                'descripcion': 'Clases de surf para principiantes con instructor',
                'costo': Decimal('50.00'),
                'duracion_minutos': 120
            },
            {
                'destino': museo_larco,
                'nombre': 'Tour Guiado',
                'tipo': 'visita_guiada',
                'descripcion': 'Recorrido guiado por las salas del museo',
                'costo': Decimal('20.00'),
                'duracion_minutos': 60
            },
            {
                'destino': mercado,
                'nombre': 'Tour Gastronómico',
                'tipo': 'degustacion',
                'descripcion': 'Degustación de jugos y platos típicos',
                'costo': Decimal('25.00'),
                'duracion_minutos': 90
            },
        ]
        
        for act_data in actividades_data:
            actividad, created = Actividad.objects.get_or_create(
                nombre=act_data['nombre'],
                destino=act_data['destino'],
                defaults=act_data
            )
            if created:
                self.stdout.write(f'  ✓ {actividad.nombre} en {actividad.destino.nombre}')
        
        # ===== CREAR RUTAS =====
        self.stdout.write('🛣️ Creando rutas entre destinos...')
        
        rutas_data = [
            {
                'origen': playa_costa_verde,
                'destino': museo_larco,
                'distancia_km': Decimal('5.2'),
                'tiempo_minutos': 20,
                'medio_transporte': 'auto',
                'costo_transporte': Decimal('15.00')
            },
            {
                'origen': museo_larco,
                'destino': mercado,
                'distancia_km': Decimal('3.8'),
                'tiempo_minutos': 15,
                'medio_transporte': 'auto',
                'costo_transporte': Decimal('12.00')
            },
            {
                'origen': mercado,
                'destino': playa_costa_verde,
                'distancia_km': Decimal('2.1'),
                'tiempo_minutos': 10,
                'medio_transporte': 'auto',
                'costo_transporte': Decimal('8.00')
            },
        ]
        
        for ruta_data in rutas_data:
            ruta, created = Ruta.objects.get_or_create(
                origen=ruta_data['origen'],
                destino=ruta_data['destino'],
                medio_transporte=ruta_data['medio_transporte'],
                defaults=ruta_data
            )
            if created:
                self.stdout.write(f'  ✓ {ruta.origen.nombre} → {ruta.destino.nombre}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ ¡Datos de prueba cargados exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   📊 {Categoria.objects.count()} categorías'))
        self.stdout.write(self.style.SUCCESS(f'   📍 {Destino.objects.count()} destinos'))
        self.stdout.write(self.style.SUCCESS(f'   🎯 {Actividad.objects.count()} actividades'))
        self.stdout.write(self.style.SUCCESS(f'   🛣️ {Ruta.objects.count()} rutas'))