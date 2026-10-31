"""Lista simplemente enlazada: cada nodo conoce únicamente al siguiente."""


class Nodo:
    """Guarda un dato y el enlace al próximo nodo."""

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaEnlazada:
    """Conserva el orden de inserción sin guardar los datos en una lista de Python."""

    def __init__(self, datos = ()):
        self._primero = None
        self._ultimo = None
        self._cantidad = 0
        for dato in datos:
            self.agregar(dato)

    def agregar(self, dato):
        """Enlaza un nuevo nodo al final, sin recorrer la lista: O(1)."""
        nuevo_nodo = Nodo(dato)
        lista_esta_vacia = self._ultimo is None
        if lista_esta_vacia:
            # El primer nodo también será el último.
            self._primero = nuevo_nodo
        else:
            self._ultimo.siguiente = nuevo_nodo
        self._ultimo = nuevo_nodo
        self._cantidad += 1

    def eliminar(self, dato):
        """Busca y elimina la primera coincidencia, conservando los enlaces: O(n)."""
        nodo_anterior = None
        nodo_actual = self._primero
        while nodo_actual is not None:
            dato_encontrado = nodo_actual.dato == dato
            if dato_encontrado:
                nodo_siguiente = nodo_actual.siguiente
                es_primer_nodo = nodo_anterior is None
                es_ultimo_nodo = nodo_actual is self._ultimo

                # 1. Saltamos el nodo eliminado al reparar el enlace de entrada.
                if es_primer_nodo:
                    self._primero = nodo_siguiente
                else:
                    nodo_anterior.siguiente = nodo_siguiente

                # 2. Si era el último, su anterior pasa a ser el nuevo final.
                if es_ultimo_nodo:
                    self._ultimo = nodo_anterior

                # 3. Actualizamos el tamaño y terminamos la búsqueda.
                self._cantidad -= 1
                return

            # Todavía no lo encontramos: avanzamos un nodo, conservando el anterior.
            nodo_anterior = nodo_actual
            nodo_actual = nodo_actual.siguiente
        raise ValueError("El dato no se encuentra en la lista enlazada")

    def limpiar(self):
        """Deja la estructura vacía y lista para recibir nuevos datos."""
        self._primero = None
        self._ultimo = None
        self._cantidad = 0

    def __len__(self):
        """Permite usar len(lista) y comprobar si está vacía con if lista."""
        return self._cantidad

    def __iter__(self):
        """Recorre los datos con for; permite eliminar el dato recién entregado.

        Se guarda el siguiente enlace antes de entregar el dato. No se deben
        eliminar otros nodos ni agregar datos durante el mismo recorrido.
        """
        nodo_actual = self._primero
        while nodo_actual is not None:
            nodo_siguiente = nodo_actual.siguiente
            dato_actual = nodo_actual.dato
            yield dato_actual
            nodo_actual = nodo_siguiente
