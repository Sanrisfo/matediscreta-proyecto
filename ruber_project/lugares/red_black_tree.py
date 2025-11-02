from enum import Enum


class Color(Enum):
    RED = 0
    BLACK = 1


class Nodo:
    
    def __init__(self, destino, color=Color.RED):
        self.destino = destino
        self.color = color
        self.izquierdo = None
        self.derecho = None
        self.padre = None
    
    def __repr__(self):
        color_str = "🔴" if self.color == Color.RED else "⚫"
        return f"{color_str} {self.destino.nombre}"


class ArbolRojoNegro:
  
    def __init__(self, criterio='nombre'):
 
        self.NIL = Nodo(None, Color.BLACK)  # Nodo centinela para hojas
        self.raiz = self.NIL
        self.criterio = criterio
        self.cantidad_nodos = 0
    
    def _comparar(self, destino1, destino2):
  
        if self.criterio == 'nombre':
            val1 = destino1.nombre.lower()
            val2 = destino2.nombre.lower()
        elif self.criterio == 'calificacion':
            val1 = float(destino1.calificacion)
            val2 = float(destino2.calificacion)
        elif self.criterio == 'costo_entrada':
            val1 = float(destino1.costo_entrada)
            val2 = float(destino2.costo_entrada)
        else:
            val1 = destino1.nombre.lower()
            val2 = destino2.nombre.lower()
        
        if val1 < val2:
            return -1
        elif val1 > val2:
            return 1
        else:
            return 0
    
    def insertar(self, destino):
 
        # Crear nuevo nodo (inicialmente rojo)
        nuevo_nodo = Nodo(destino, Color.RED)
        nuevo_nodo.izquierdo = self.NIL
        nuevo_nodo.derecho = self.NIL
        
        # Encontrar posición para insertar
        padre = None
        actual = self.raiz
        
        while actual != self.NIL:
            padre = actual
            if self._comparar(nuevo_nodo.destino, actual.destino) < 0:
                actual = actual.izquierdo
            else:
                actual = actual.derecho
        
        # Establecer padre del nuevo nodo
        nuevo_nodo.padre = padre
        
        # Insertar nodo
        if padre is None:
            # Árbol estaba vacío
            self.raiz = nuevo_nodo
        elif self._comparar(nuevo_nodo.destino, padre.destino) < 0:
            padre.izquierdo = nuevo_nodo
        else:
            padre.derecho = nuevo_nodo
        
        self.cantidad_nodos += 1
        
        # Restaurar propiedades del árbol rojo-negro
        self._arreglar_insercion(nuevo_nodo)
    
    def _arreglar_insercion(self, nodo):
 
        while nodo.padre and nodo.padre.color == Color.RED:
            if nodo.padre == nodo.padre.padre.izquierdo:
                # Padre es hijo izquierdo
                tio = nodo.padre.padre.derecho
                
                if tio.color == Color.RED:
                    # Caso 1: Tío es rojo
                    nodo.padre.color = Color.BLACK
                    tio.color = Color.BLACK
                    nodo.padre.padre.color = Color.RED
                    nodo = nodo.padre.padre
                else:
                    if nodo == nodo.padre.derecho:
                        # Caso 2: Nodo es hijo derecho (triángulo)
                        nodo = nodo.padre
                        self._rotar_izquierda(nodo)
                    
                    # Caso 3: Nodo es hijo izquierdo (línea)
                    nodo.padre.color = Color.BLACK
                    nodo.padre.padre.color = Color.RED
                    self._rotar_derecha(nodo.padre.padre)
            else:
                # Padre es hijo derecho (simétrico)
                tio = nodo.padre.padre.izquierdo
                
                if tio.color == Color.RED:
                    # Caso 1: Tío es rojo
                    nodo.padre.color = Color.BLACK
                    tio.color = Color.BLACK
                    nodo.padre.padre.color = Color.RED
                    nodo = nodo.padre.padre
                else:
                    if nodo == nodo.padre.izquierdo:
                        # Caso 2: Nodo es hijo izquierdo (triángulo)
                        nodo = nodo.padre
                        self._rotar_derecha(nodo)
                    
                    # Caso 3: Nodo es hijo derecho (línea)
                    nodo.padre.color = Color.BLACK
                    nodo.padre.padre.color = Color.RED
                    self._rotar_izquierda(nodo.padre.padre)
        
        # La raíz siempre debe ser negra
        self.raiz.color = Color.BLACK
    
    def _rotar_izquierda(self, nodo):

        y = nodo.derecho
        nodo.derecho = y.izquierdo
        
        if y.izquierdo != self.NIL:
            y.izquierdo.padre = nodo
        
        y.padre = nodo.padre
        
        if nodo.padre is None:
            self.raiz = y
        elif nodo == nodo.padre.izquierdo:
            nodo.padre.izquierdo = y
        else:
            nodo.padre.derecho = y
        
        y.izquierdo = nodo
        nodo.padre = y
    
    def _rotar_derecha(self, nodo):
   
        x = nodo.izquierdo
        nodo.izquierdo = x.derecho
        
        if x.derecho != self.NIL:
            x.derecho.padre = nodo
        
        x.padre = nodo.padre
        
        if nodo.padre is None:
            self.raiz = x
        elif nodo == nodo.padre.derecho:
            nodo.padre.derecho = x
        else:
            nodo.padre.izquierdo = x
        
        x.derecho = nodo
        nodo.padre = x
    
    def recorrido_inorden(self):

        resultado = []
        self._inorden_recursivo(self.raiz, resultado)
        return resultado
    
    def _inorden_recursivo(self, nodo, resultado):
        """Recorrido in-orden recursivo"""
        if nodo != self.NIL:
            self._inorden_recursivo(nodo.izquierdo, resultado)
            resultado.append(nodo.destino)
            self._inorden_recursivo(nodo.derecho, resultado)
    
    def recorrido_preorden(self):

        resultado = []
        self._preorden_recursivo(self.raiz, resultado, 0)
        return resultado
    
    def _preorden_recursivo(self, nodo, resultado, nivel):
        """Recorrido pre-orden recursivo"""
        if nodo != self.NIL:
            resultado.append((nodo.destino, nodo.color, nivel))
            self._preorden_recursivo(nodo.izquierdo, resultado, nivel + 1)
            self._preorden_recursivo(nodo.derecho, resultado, nivel + 1)
    
    def buscar(self, valor):

        nodo = self._buscar_nodo(self.raiz, valor)
        return nodo.destino if nodo != self.NIL else None
    
    def _buscar_nodo(self, nodo, valor):
        """Búsqueda recursiva"""
        if nodo == self.NIL:
            return self.NIL
        
        if self.criterio == 'nombre':
            valor_nodo = nodo.destino.nombre.lower()
            valor_busqueda = valor.lower()
        else:
            valor_nodo = getattr(nodo.destino, self.criterio)
            valor_busqueda = valor
        
        if valor_busqueda == valor_nodo:
            return nodo
        elif valor_busqueda < valor_nodo:
            return self._buscar_nodo(nodo.izquierdo, valor)
        else:
            return self._buscar_nodo(nodo.derecho, valor)
    
    def altura(self):
        """Calcula la altura del árbol"""
        return self._altura_recursiva(self.raiz)
    
    def _altura_recursiva(self, nodo):
        """Altura recursiva"""
        if nodo == self.NIL:
            return 0
        
        altura_izq = self._altura_recursiva(nodo.izquierdo)
        altura_der = self._altura_recursiva(nodo.derecho)
        return 1 + max(altura_izq, altura_der)
    
    def verificar_propiedades(self):
        """
        Verifica que el árbol cumple todas las propiedades de RB
        Útil para debugging
        
        Returns:
            tuple: (es_valido, mensaje)
        """
        if self.raiz == self.NIL:
            return True, "Árbol vacío es válido"
        
        # Propiedad 2: La raíz es negra
        if self.raiz.color != Color.BLACK:
            return False, "La raíz debe ser negra"
        
        # Verificar otras propiedades recursivamente
        valido, caminos = self._verificar_recursivo(self.raiz)
        
        if not valido:
            return False, "Violación de propiedades de nodos rojos"
        
        # Propiedad 5: Todos los caminos tienen mismo número de nodos negros
        if len(set(caminos)) > 1:
            return False, f"Diferentes números de nodos negros en caminos: {set(caminos)}"
        
        return True, "Árbol válido"
    
    def _verificar_recursivo(self, nodo):
        """Verificación recursiva de propiedades"""
        if nodo == self.NIL:
            return True, [1]  # Contar NIL como negro
        
        # Propiedad 4: Si un nodo es rojo, sus hijos son negros
        if nodo.color == Color.RED:
            if (nodo.izquierdo.color == Color.RED or 
                nodo.derecho.color == Color.RED):
                return False, []
        
        # Verificar subárboles
        valido_izq, caminos_izq = self._verificar_recursivo(nodo.izquierdo)
        valido_der, caminos_der = self._verificar_recursivo(nodo.derecho)
        
        if not valido_izq or not valido_der:
            return False, []
        
        # Agregar este nodo a los caminos si es negro
        incremento = 1 if nodo.color == Color.BLACK else 0
        caminos = [c + incremento for c in caminos_izq + caminos_der]
        
        return True, caminos
    
    def visualizar(self):

        if self.raiz == self.NIL:
            return "Árbol vacío"
        
        lineas = []
        self._visualizar_recursivo(self.raiz, "", True, lineas)
        return "\n".join(lineas)
    
    def _visualizar_recursivo(self, nodo, prefijo, es_ultimo, lineas):
        """Visualización recursiva del árbol"""
        if nodo != self.NIL:
            color_emoji = "🔴" if nodo.color == Color.RED else "⚫"
            lineas.append(prefijo + ("└── " if es_ultimo else "├── ") + 
                         f"{color_emoji} {nodo.destino.nombre}")
            
            extension = "    " if es_ultimo else "│   "
            
            if nodo.izquierdo != self.NIL or nodo.derecho != self.NIL:
                self._visualizar_recursivo(
                    nodo.izquierdo, 
                    prefijo + extension, 
                    False, 
                    lineas
                )
                self._visualizar_recursivo(
                    nodo.derecho, 
                    prefijo + extension, 
                    True, 
                    lineas
                )


# ===================================
# FUNCIÓN HELPER PARA VISTAS
# ===================================

def ordenar_destinos_rb(destinos_queryset, criterio='nombre', reverso=False):
    # Crear árbol
    arbol = ArbolRojoNegro(criterio=criterio)
    
    # Insertar todos los destinos
    for destino in destinos_queryset:
        arbol.insertar(destino)
    
    # Obtener destinos ordenados
    destinos_ordenados = arbol.recorrido_inorden()
    
    # Invertir si se requiere orden descendente
    if reverso:
        destinos_ordenados.reverse()
    
    # Información de debug
    print(f"✓ Árbol Rojo-Negro creado")
    print(f"  - Criterio: {criterio}")
    print(f"  - Nodos: {arbol.cantidad_nodos}")
    print(f"  - Altura: {arbol.altura()}")
    print(f"  - Altura máxima teórica: {2 * (arbol.cantidad_nodos + 1).bit_length()}")
    
    # Verificar validez
    valido, mensaje = arbol.verificar_propiedades()
    print(f"  - Válido: {valido} - {mensaje}")
    
    return destinos_ordenados, arbol
