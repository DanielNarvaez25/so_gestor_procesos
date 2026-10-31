"""Lista simplemente enlazada: cada nodo conoce únicamente al siguiente."""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

TipoDato = TypeVar("TipoDato")


class Nodo(Generic[TipoDato]):
    """Guarda un dato y el enlace al próximo nodo."""

    def __init__(self, dato: TipoDato):
        self.dato = dato
        self.siguiente: Nodo[TipoDato] | None = None


class ListaEnlazada(Generic[TipoDato]):
    """Conserva el orden de inserción sin guardar los datos en una lista de Python."""

    def __init__(self, datos: Iterable[TipoDato] = ()):
        self._primero: Nodo[TipoDato] | None = None
        self._ultimo: Nodo[TipoDato] | None = None
        self._cantidad = 0
        for dato in datos:
            self.agregar(dato)

    def agregar(self, dato: TipoDato) -> None:
        """Enlaza un nuevo nodo al final, sin recorrer la lista: O(1)."""
        nuevo_nodo = Nodo(dato)
        if self._ultimo is None:
            self._primero = nuevo_nodo
        else:
            self._ultimo.siguiente = nuevo_nodo
        self._ultimo = nuevo_nodo
        self._cantidad += 1

    def eliminar(self, dato: TipoDato) -> None:
        """Busca y elimina la primera coincidencia, conservando los enlaces: O(n)."""
        nodo_anterior = None
        nodo_actual = self._primero
        while nodo_actual is not None:
            if nodo_actual.dato == dato:
                if nodo_anterior is None:
                    self._primero = nodo_actual.siguiente
                else:
                    nodo_anterior.siguiente = nodo_actual.siguiente
                if nodo_actual is self._ultimo:
                    self._ultimo = nodo_anterior
                self._cantidad -= 1
                return
            nodo_anterior = nodo_actual
            nodo_actual = nodo_actual.siguiente
        raise ValueError("El dato no se encuentra en la lista enlazada")

    def limpiar(self) -> None:
        """Deja la estructura vacía y lista para recibir nuevos datos."""
        self._primero = None
        self._ultimo = None
        self._cantidad = 0

    def __len__(self) -> int:
        """Permite usar len(lista) y comprobar si está vacía con if lista."""
        return self._cantidad

    def __iter__(self) -> Iterator[TipoDato]:
        """Recorre los datos con for; permite eliminar el dato recién entregado.

        Se guarda el siguiente enlace antes de entregar el dato. No se deben
        eliminar otros nodos ni agregar datos durante el mismo recorrido.
        """
        nodo_actual = self._primero
        while nodo_actual is not None:
            nodo_siguiente = nodo_actual.siguiente
            yield nodo_actual.dato
            nodo_actual = nodo_siguiente
