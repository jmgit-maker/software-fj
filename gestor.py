"""
Gestores que administran las listas internas de clientes, servicios y reservas.

No hay base de datos: todo vive en memoria mientras corre el programa.
Cada operación crítica está envuelta en try/except para que un error
no detenga toda la aplicación.
"""

from excepciones import (
    ErrorSistemaFJ,
    ClienteDuplicadoError,
    ReservaInvalidaError,
)
from modelo import Reserva


class GestorClientes:
    """Maneja la lista de clientes registrados."""

    def __init__(self):
        self.clientes = []

    def registrar(self, cliente):
        # Verificamos que no exista otro cliente con la misma identificación
        for c in self.clientes:
            if c.identificacion == cliente.identificacion:
                raise ClienteDuplicadoError(
                    f"Ya existe un cliente con ID {cliente.identificacion}"
                )
        self.clientes.append(cliente)
        return cliente

    def buscar(self, identificacion):
        # Recorremos la lista buscando coincidencia exacta
        for c in self.clientes:
            if c.identificacion == identificacion:
                return c
        return None


class GestorServicios:
    """Maneja la lista de servicios ofrecidos por la empresa."""

    def __init__(self):
        self.servicios = []

    def agregar(self, servicio):
        self.servicios.append(servicio)
        return servicio

    def listar_disponibles(self):
        # Solo devolvemos los servicios que están marcados como disponibles
        return [s for s in self.servicios if s.esta_disponible()]


class GestorReservas:
    """Maneja la creación y el ciclo de vida de las reservas."""

    def __init__(self, logger):
        self.reservas = []
        self.logger = logger

    def crear(self, cliente, servicio, duracion):
        """Crea una reserva usando try/except/else/finally para dejar rastro."""
        try:
            # Validamos lo básico antes de instanciar la reserva
            if cliente is None:
                raise ReservaInvalidaError("No se puede reservar sin cliente")
            if not servicio.esta_disponible():
                raise ReservaInvalidaError(
                    f"El servicio {servicio.codigo} no está disponible"
                )
            reserva = Reserva(cliente, servicio, duracion)
            
            # Validación extra agregada por Julieth para asegurar un else explícito
            try:
                if reserva.duracion > 0:
                    pass # La duración es correcta
            except Exception as e:
                raise ReservaInvalidaError("Error inesperado en la duración") from e
            else:
                self.logger.registrar_evento("Validación de duración exitosa (else ejecutado)")

        except ErrorSistemaFJ as e:
            # Registramos el error y lo relanzamos para que main lo sepa
            self.logger.registrar_error(e, "crear reserva")
            raise
        else:
            # Este bloque solo corre si NO hubo excepción
            self.reservas.append(reserva)
            self.logger.registrar_evento(
                f"Reserva creada para {cliente.nombre} - servicio {servicio.codigo}"
            )
            return reserva
        finally:
            # Pase lo que pase, dejamos anotado que hubo un intento de reserva
            self.logger.registrar_evento(
                f"Intento de creación de reserva finalizado para servicio {servicio.codigo}"
            )

    def confirmar(self, reserva):
        try:
            reserva.confirmar()
            self.logger.registrar_evento(f"Reserva confirmada: {reserva.describir()}")
        except Exception as e:
            self.logger.registrar_error(e, "confirmar reserva")
            raise

    def cancelar(self, reserva):
        try:
            reserva.cancelar()
            self.logger.registrar_evento(f"Reserva cancelada: {reserva.describir()}")
        except Exception as e:
            self.logger.registrar_error(e, "cancelar reserva")
            raise

    def procesar(self, reserva):
        try:
            reserva.procesar()
            self.logger.registrar_evento(f"Reserva procesada: {reserva.describir()}")
        except Exception as e:
            self.logger.registrar_error(e, "procesar reserva")
            raise
