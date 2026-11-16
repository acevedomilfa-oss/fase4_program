#Milton Fabian Acevedo Suarez
#Ingenieria de Sistemas - UNAD - Programacion


"""Sistema de gestion de clientes, Software FJ."""

# ABC y dataclass definen las entidades; json, datetime, Path y Any apoyan su gestion.
# Se importa logging para registrar eventos y errores, math para validaciones numericas, re para expresiones regulares y typing para anotaciones de tipos.
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
from datetime import datetime
import logging
import math
from pathlib import Path
import re
from typing import Any, Callable, ClassVar

# Clase abstracta usando decoradores, representa entidades generales del sistema.
@dataclass
class EntidadSistema(ABC):
    id: int

    @abstractmethod
    def a_diccionario(self) -> dict[str, Any]:
        #Convierte la entidad a la estructura que se almacena en JSON.
        ...

# Clase Cliente con validaciones robustas y encapsulación de datos personales.
class Cliente(EntidadSistema):
    _PATRON_CORREO = re.compile(
        r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
    )
    _PATRON_TELEFONO = re.compile(r"\+?[0-9().\s-]+")

    def __init__(
        self,
        id: int,
        nombre: str,
        correo: str,
        telefono: str,
        activo: bool = True,
    ) -> None:
        super().__init__(id)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.activo = activo

    @staticmethod
    def validar_nombre(valor: str) -> str:
        if not isinstance(valor, str):
            raise ValueError("El nombre debe ser texto.")
        nombre = " ".join(valor.split())
        if not nombre or len(nombre) > 100:
            raise ValueError("El nombre debe tener entre 1 y 100 caracteres.")
        if not any(caracter.isalpha() for caracter in nombre) or any(
            not (caracter.isalpha() or caracter in " .'-’") for caracter in nombre
        ):
            raise ValueError("El nombre solo puede contener letras, espacios, apostrofes, puntos o guiones.")
        return nombre

    @staticmethod
    def validar_correo(valor: str) -> str:
        if not isinstance(valor, str):
            raise ValueError("El correo debe ser texto.")
        correo = valor.strip()
        if correo.count("@") != 1:
            raise ValueError("El correo debe incluir exactamente un signo @.")
        local, dominio = correo.split("@", 1)
        if (
            len(correo) > 254
            or len(local) > 64
            or local.startswith(".")
            or local.endswith(".")
            or ".." in local
            or len(dominio) > 253
            or len(dominio.rsplit(".", 1)[-1]) < 2
            or not Cliente._PATRON_CORREO.fullmatch(correo)
        ):
            raise ValueError("Ingresa un correo valido, por ejemplo nombre@dominio.com.")
        return correo

    @staticmethod
    def validar_telefono(valor: str) -> str:
        if not isinstance(valor, str):
            raise ValueError("El telefono debe ser texto.")
        telefono = valor.strip()
        digitos = "".join(caracter for caracter in telefono if caracter in "0123456789")
        if (
            not Cliente._PATRON_TELEFONO.fullmatch(telefono)
            or not 7 <= len(digitos) <= 15
        ):
            raise ValueError("El telefono debe tener entre 7 y 15 digitos y usar un formato valido.")
        return ("+" if telefono.startswith("+") else "") + digitos

    #Encapsulamiento de atributos privados con propiedades y validaciones.
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre = self.validar_nombre(valor)

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        self.__correo = self.validar_correo(valor)

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self.__telefono = self.validar_telefono(valor)

    def __repr__(self) -> str:
        return f"Cliente(id={self.id}, datos_personales=<privados>)"

    def a_diccionario(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "telefono": self.telefono,
            "activo": self.activo,
        }


# Clase abstracta Servicio
@dataclass
class Servicio(EntidadSistema, ABC):
    nombre: str
    precio: float
    activo: bool = True

    TIPO: ClassVar[str] = ""

    def __post_init__(self) -> None:
        if not isinstance(self.nombre, str) or not self.nombre.strip():
            raise ValueError("El nombre del servicio no puede estar vacio.")
        if (
            isinstance(self.precio, bool)
            or not isinstance(self.precio, (int, float))
            or not math.isfinite(self.precio)
            or self.precio < 0
        ):
            raise ValueError("La tarifa debe ser un numero finito igual o mayor que cero.")
        if not isinstance(self.activo, bool):
            raise ValueError("El estado del servicio debe ser verdadero o falso.")

    @abstractmethod
    def calcular_costo(self, parametros: dict[str, Any]) -> float:
        ...

    @abstractmethod
    def calcular_descuento(self, parametros: dict[str, Any]) -> float:
        ...

    @abstractmethod
    def describir(self) -> str:
        ...

    @abstractmethod
    def validar_parametros(self, parametros: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def solicitar_parametros(self) -> dict[str, Any]:
        ...

    def a_diccionario(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": self.precio,
            "activo": self.activo,
            "tipo": self.TIPO,
        }


# Clases hijas de Servicio para diferentes tipos de servicios
# Implementan polimorfismo y sobreescriben calculo de costo, descripcion y validacion de parametros.
#Sobrecarga los metodos de la clase base para calcular descuentos a cada tipo de servicio.
@dataclass
class ServicioSala(Servicio):
    TIPO: ClassVar[str] = "sala"

    def calcular_costo(self, parametros: dict[str, Any]) -> float:
        horas = self.validar_parametros(parametros)["horas"]
        subtotal = self.precio * horas
        return round(subtotal - self.calcular_descuento({"horas": horas}), 2)

    def calcular_descuento(self, parametros: dict[str, Any]) -> float:
        horas = self.validar_parametros(parametros)["horas"]
        if horas > 12:
            return round(self.precio * horas * 0.20, 2)
        return 0.0

    def describir(self) -> str:
        return f"{self.nombre} | ${self.precio:.0f} por hora"

    def validar_parametros(self, parametros: dict[str, Any]) -> dict[str, Any]:
        horas = parametros.get("horas") if isinstance(parametros, dict) else None
        if type(horas) is not int or not 1 <= horas <= 24:
            raise ValueError("Las horas de reserva deben ser un entero entre 1 y 24.")
        return {"horas": horas}

    def solicitar_parametros(self) -> dict[str, Any]:
        while True:
            try:
                return self.validar_parametros(
                    {"horas": pedir_entero("Horas de reserva (1-24): ")}
                )
            except ValueError as error:
                LOGGER.warning("Parametro de reserva de sala rechazado: %s", error)
                print(error)


@dataclass
class ServicioEquipos(Servicio):
    TIPO: ClassVar[str] = "equipos"

    def calcular_costo(self, parametros: dict[str, Any]) -> float:
        cantidad = self.validar_parametros(parametros)["cantidad"]
        subtotal = self.precio * cantidad
        return round(subtotal - self.calcular_descuento({"cantidad": cantidad}), 2)

    def calcular_descuento(self, parametros: dict[str, Any]) -> float:
        cantidad = self.validar_parametros(parametros)["cantidad"]
        if cantidad > 20:
            return round(self.precio * cantidad * 0.20, 2)
        return 0.0

    def describir(self) -> str:
        return f"{self.nombre} | ${self.precio:.0f} por equipo"

    def validar_parametros(self, parametros: dict[str, Any]) -> dict[str, Any]:
        cantidad = parametros.get("cantidad") if isinstance(parametros, dict) else None
        if type(cantidad) is not int or not 1 <= cantidad <= 100:
            raise ValueError("La cantidad de equipos debe ser un entero entre 1 y 100.")
        return {"cantidad": cantidad}

    def solicitar_parametros(self) -> dict[str, Any]:
        while True:
            try:
                return self.validar_parametros(
                    {"cantidad": pedir_entero("Cantidad de equipos (1-100): ")}
                )
            except ValueError as error:
                LOGGER.warning("Parametro de alquiler de equipos rechazado: %s", error)
                print(error)


@dataclass
class ServicioAsesoria(Servicio):
    TIPO: ClassVar[str] = "asesoria"

    def calcular_costo(self, parametros: dict[str, Any]) -> float:
        horas = self.validar_parametros(parametros)["horas"]
        subtotal = self.precio * horas
        return round(subtotal - self.calcular_descuento({"horas": horas}), 2)

    def calcular_descuento(self, parametros: dict[str, Any]) -> float:
        horas = self.validar_parametros(parametros)["horas"]
        if horas > 5:
            return round(self.precio * horas * 0.20, 2)
        return 0.0

    def describir(self) -> str:
        return f"{self.nombre} | ${self.precio:.0f} por hora"

    def validar_parametros(self, parametros: dict[str, Any]) -> dict[str, Any]:
        horas = parametros.get("horas") if isinstance(parametros, dict) else None
        if (
            isinstance(horas, bool)
            or not isinstance(horas, (int, float))
            or not math.isfinite(horas)
            or not 1 <= horas <= 8
        ):
            raise ValueError("Las horas de asesoria deben estar entre 1 y 8.")
        return {"horas": float(horas)}

    def solicitar_parametros(self) -> dict[str, Any]:
        while True:
            try:
                return self.validar_parametros(
                    {"horas": pedir_numero("Horas de asesoria (1-8): ")}
                )
            except ValueError as error:
                LOGGER.warning("Parametro de asesoria rechazado: %s", error)
                print(error)


TIPOS_SERVICIO: dict[str, type[Servicio]] = {
    ServicioSala.TIPO: ServicioSala,
    ServicioEquipos.TIPO: ServicioEquipos,
    ServicioAsesoria.TIPO: ServicioAsesoria,
}


def servicio_desde_diccionario(registro: dict[str, Any]) -> Servicio:
    tipo = registro.get("tipo")
    clase = TIPOS_SERVICIO.get(tipo)
    if clase is None:
        raise ValueError(f"El tipo de servicio {tipo!r} no esta reconocido.")
    return clase(
        id=registro["id"],
        nombre=registro["nombre"],
        precio=registro["precio"],
        activo=registro.get("activo", True),
    )


#Clase Reserva integra cliente, servicio, duración y estado.
@dataclass
class Reserva(EntidadSistema):
    cliente_id: int
    servicio_id: int
    fecha: str
    hora: str
    estado: str = "Activa"
    parametros: dict[str, Any] = field(default_factory=dict)
    costo: float = 0.0
    descuento: float = 0.0

    def a_diccionario(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "servicio_id": self.servicio_id,
            "fecha": self.fecha,
            "hora": self.hora,
            "estado": self.estado,
            "parametros": self.parametros,
            "costo": self.costo,
            "descuento": self.descuento,
        }


ARCHIVO_DATOS = Path(__file__).with_name("software_fj_datos.json")
ARCHIVO_LOG = Path(__file__).with_name("software_fj.log")
LOGGER = logging.getLogger("software_fj")


def configurar_logging() -> None:
    if any(getattr(handler, "_software_fj_handler", False) for handler in LOGGER.handlers):
        return

    handler = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    setattr(handler, "_software_fj_handler", True)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False

SERVICIOS_INICIALES = [
    {"id": 1, "nombre": "Reserva de salas", "precio": 0.0, "tipo": "sala"},
    {"id": 2, "nombre": "Alquiler de equipos", "precio": 0.0, "tipo": "equipos"},
    {"id": 3, "nombre": "Asesorias especializadas", "precio": 0.0, "tipo": "asesoria"},
]


def guardar_datos(datos: dict[str, Any]) -> None:
    """Guarda los datos de forma legible para el usuario."""
    with ARCHIVO_DATOS.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    LOGGER.info("Datos guardados.")


def cargar_datos() -> dict[str, Any]:
    if not ARCHIVO_DATOS.exists():
        datos = {"clientes": [], "servicios": SERVICIOS_INICIALES.copy(), "reservas": []}
        guardar_datos(datos)
        LOGGER.info("Archivo de datos inicializado.")
        return datos

    with ARCHIVO_DATOS.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    if not isinstance(datos, dict):
        raise ValueError("El archivo de datos no tiene el formato esperado.")

    datos_actualizados = False
    for clave in ("clientes", "servicios", "reservas"):
        if clave not in datos:
            datos[clave] = []
            datos_actualizados = True
        elif not isinstance(datos[clave], list):
            raise ValueError(f"El campo {clave} debe contener una lista.")

    servicios_por_id = {servicio["id"]: servicio for servicio in datos["servicios"]}
    if len(servicios_por_id) != len(datos["servicios"]):
        raise ValueError("Hay servicios con numeros duplicados en el archivo de datos.")

    catalogo_actualizado = datos_actualizados
    servicios = []
    for servicio_inicial in SERVICIOS_INICIALES:
        servicio = servicios_por_id.pop(servicio_inicial["id"], None)
        if servicio is None:
            servicio = servicio_inicial.copy()
            catalogo_actualizado = True
        else:
            for campo in ("nombre", "tipo"):
                if servicio.get(campo) != servicio_inicial[campo]:
                    servicio[campo] = servicio_inicial[campo]
                    catalogo_actualizado = True
            if "activo" not in servicio:
                servicio["activo"] = True
                catalogo_actualizado = True
        servicios.append(servicio)

    servicios.extend(servicios_por_id.values())
    for servicio in servicios:
        categoria_anterior = servicio.pop("categoria", "")
        if categoria_anterior:
            catalogo_actualizado = True
        if "tipo" not in servicio:
            descripcion_anterior = f"{categoria_anterior} {servicio.get('nombre', '')}".lower()
            if "sala" in descripcion_anterior:
                servicio["tipo"] = ServicioSala.TIPO
            elif "equipo" in descripcion_anterior:
                servicio["tipo"] = ServicioEquipos.TIPO
            else:
                servicio["tipo"] = ServicioAsesoria.TIPO
            catalogo_actualizado = True
    if len(servicios) != len(datos["servicios"]):
        catalogo_actualizado = True
    datos["servicios"] = servicios
    if catalogo_actualizado:
        guardar_datos(datos)
        LOGGER.info("Estructura del archivo de datos actualizada.")
    LOGGER.info(
        "Datos cargados: %d clientes, %d servicios, %d reservas.",
        len(datos["clientes"]),
        len(datos["servicios"]),
        len(datos["reservas"]),
    )
    return datos


def siguiente_id(registros: list[dict[str, Any]]) -> int:
    return max((registro["id"] for registro in registros), default=0) + 1


def pedir_texto(mensaje: str) -> str:
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        LOGGER.warning("Se rechazo un campo de texto vacio.")
        print("El valor no puede quedar vacio.")


def pedir_dato_cliente(mensaje: str, validar: Callable[[str], str]) -> str:
    while True:
        try:
            return validar(input(mensaje))
        except ValueError as error:
            LOGGER.warning("Se rechazo un dato de cliente: %s", error)
            print(error)


def pedir_precio(mensaje: str) -> float:
    while True:
        try:
            precio = float(input(mensaje).replace(",", ".").strip())
            if math.isfinite(precio) and precio >= 0:
                return precio
        except ValueError:
            pass
        LOGGER.warning("Se ingreso un precio invalido.")
        print("Ingresa un precio finito igual o mayor que cero.")


def pedir_entero(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje).strip())
        except ValueError:
            LOGGER.warning("Se ingreso un valor que no es entero.")
            print("Ingresa un numero entero valido.")


def pedir_numero(mensaje: str) -> float:
    while True:
        try:
            numero = float(input(mensaje).replace(",", ".").strip())
            if math.isfinite(numero):
                return numero
        except ValueError:
            pass
        LOGGER.warning("Se ingreso un valor numerico invalido.")
        print("Ingresa un numero valido.")


def registrar_cliente(datos: dict[str, Any]) -> None:
    print("\n--- Registrar cliente ---")
    nombre = pedir_dato_cliente("Nombre completo: ", Cliente.validar_nombre)
    correo = pedir_dato_cliente("Correo electronico (debe incluir @): ", Cliente.validar_correo)
    telefono = pedir_dato_cliente("Telefono: ", Cliente.validar_telefono)
    cliente = Cliente(
        id=siguiente_id(datos["clientes"]),
        nombre=nombre,
        correo=correo,
        telefono=telefono,
    ).a_diccionario()
    datos["clientes"].append(cliente)
    guardar_datos(datos)
    LOGGER.info("Cliente registrado: id=%s.", cliente["id"])
    print(f"Cliente registrado con el numero {cliente['id']}.")


def listar_clientes(datos: dict[str, Any]) -> None:
    print("\n--- Clientes ---")
    clientes = [c for c in datos["clientes"] if c.get("activo", True)]
    if not clientes:
        print("No hay clientes activos registrados.")
        return
    for cliente in clientes:
        print(
            f"#{cliente['id']} | {cliente['nombre']} | "
            f"{cliente['correo']} | {cliente['telefono']}"
        )


def modificar_cliente(datos: dict[str, Any]) -> None:
    print("\n--- Modificar cliente ---")
    listar_clientes(datos)
    clientes = [c for c in datos["clientes"] if c.get("activo", True)]
    registro = elegir_registro(clientes, "clientes")
    if registro is None:
        return

    cliente = Cliente(
        id=registro["id"],
        nombre=registro["nombre"],
        correo=registro["correo"],
        telefono=registro["telefono"],
        activo=registro.get("activo", True),
    )
    print("1. Modificar nombre\n2. Modificar correo\n3. Modificar telefono")
    opcion = input("Selecciona el dato que deseas modificar: ").strip()
    if opcion == "1":
        cliente.nombre = pedir_dato_cliente("Nuevo nombre: ", Cliente.validar_nombre)
    elif opcion == "2":
        cliente.correo = pedir_dato_cliente(
            "Nuevo correo (debe incluir @): ", Cliente.validar_correo
        )
    elif opcion == "3":
        cliente.telefono = pedir_dato_cliente("Nuevo telefono: ", Cliente.validar_telefono)
    else:
        LOGGER.warning(
            "Opcion invalida al modificar cliente %s: %s.", cliente.id, opcion
        )
        print("Opcion no valida; no se realizaron cambios.")
        return

    registro.update(cliente.a_diccionario())
    guardar_datos(datos)
    LOGGER.info("Cliente modificado: id=%s.", cliente.id)
    print(f"Cliente #{cliente.id} actualizado.")


def eliminar_cliente(datos: dict[str, Any]) -> None:
    print("\n--- Eliminar cliente ---")
    listar_clientes(datos)
    clientes = [c for c in datos["clientes"] if c.get("activo", True)]
    cliente = elegir_registro(clientes, "clientes")
    if cliente is None:
        return

    cliente["activo"] = False
    guardar_datos(datos)
    LOGGER.info("Cliente eliminado: id=%s.", cliente["id"])
    print(
        f"Cliente #{cliente['id']} eliminado. "
        "Las reservas anteriores se conservan."
    )


def listar_servicios(datos: dict[str, Any]) -> None:
    print("\n--- Servicios de Software FJ ---")
    servicios = [s for s in datos["servicios"] if s.get("activo", True)]
    if not servicios:
        print("No hay servicios disponibles.")
        return
    for registro in servicios:
        servicio = servicio_desde_diccionario(registro)
        print(f"#{servicio.id} | {servicio.describir()}")


def modificar_servicio(datos: dict[str, Any]) -> None:
    print("\n--- Modificar servicio ---")
    listar_servicios(datos)
    servicios = [s for s in datos["servicios"] if s.get("activo", True)]
    if not servicios:
        return

    try:
        identificador = int(input("Numero de servicio: ").strip())
    except ValueError:
        LOGGER.warning("Numero de servicio invalido durante la modificacion.")
        print("Numero de servicio no valido. Volviendo al menu principal.")
        return
    servicio = next(
        (registro for registro in servicios if registro["id"] == identificador),
        None,
    )
    if servicio is None:
        LOGGER.warning("No existe el servicio %s para modificar.", identificador)
        print("No se encontro el servicio. Volviendo al menu principal.")
        return

    servicio["precio"] = pedir_precio("Nueva tarifa: $")
    guardar_datos(datos)
    LOGGER.info("Tarifa de servicio modificada: id=%s.", servicio["id"])
    print(f"Tarifa del servicio #{servicio['id']} actualizada.")


def crear_servicio(datos: dict[str, Any]) -> None:
    print("\n--- Crear servicio ---")
    print("1. Reserva de salas\n2. Alquiler de equipos\n3. Asesoria especializada")
    clases = {
        "1": ServicioSala,
        "2": ServicioEquipos,
        "3": ServicioAsesoria,
    }
    while True:
        clase = clases.get(input("Tipo de servicio: ").strip())
        if clase is not None:
            break
        LOGGER.warning("Tipo de servicio invalido al crear uno.")
        print("Selecciona una de las opciones disponibles.")

    servicio = clase(
        id=siguiente_id(datos["servicios"]),
        nombre=pedir_texto("Nombre del servicio: "),
        precio=pedir_precio("Tarifa: $"),
    ).a_diccionario()
    datos["servicios"].append(servicio)
    guardar_datos(datos)
    LOGGER.info("Servicio creado: id=%s, tipo=%s.", servicio["id"], servicio["tipo"])
    print(f"Servicio #{servicio['id']} creado.")


def elegir_registro(registros: list[dict[str, Any]], tipo: str) -> dict[str, Any] | None:
    if not registros:
        print(f"No hay {tipo} disponibles.")
        return None

    while True:
        try:
            identificador = int(input(f"Numero de {tipo[:-1]}: "))
        except ValueError:
            LOGGER.warning("Se ingreso un identificador de %s invalido.", tipo)
            print("Ingresa un numero valido.")
            continue
        for registro in registros:
            if registro["id"] == identificador:
                return registro
        print(f"No se encontro ese {tipo[:-1]}.")
        LOGGER.warning("No se encontro el identificador de %s %s.", tipo, identificador)


# Implementa confirmación, cancelación y procesamiento con manejo de excepciones.
def crear_reserva(datos: dict[str, Any]) -> None:
    print("\n--- Crear reserva ---")
    clientes = [c for c in datos["clientes"] if c.get("activo", True)]
    cliente = elegir_registro(clientes, "clientes")
    if cliente is None:
        return
    servicios = [s for s in datos["servicios"] if s.get("activo", True)]
    registro_servicio = elegir_registro(servicios, "servicios")
    if registro_servicio is None:
        return
    servicio = servicio_desde_diccionario(registro_servicio)

    while True:
        fecha = input("Fecha (AAAA-MM-DD): ").strip()
        hora = input("Hora (HH:MM): ").strip()
        try:
            datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            break
        except ValueError:
            LOGGER.warning("Fecha u hora de reserva invalida.")
            print("Fecha u hora no valida. Usa los formatos indicados.")

    ocupada = any(
        reserva["servicio_id"] == servicio.id
        and reserva["fecha"] == fecha
        and reserva["hora"] == hora
        and reserva["estado"] == "Activa"
        for reserva in datos["reservas"]
    )
    if ocupada:
        LOGGER.warning(
            "Intento de reservar un servicio ocupado: servicio=%s, fecha=%s, hora=%s.",
            servicio.id,
            fecha,
            hora,
        )
        print("Ese servicio ya tiene una reserva activa en esa fecha y hora.")
        return

    parametros = servicio.solicitar_parametros()
    descuento = servicio.calcular_descuento(parametros)
    costo = servicio.calcular_costo(parametros)
    reserva = Reserva(
        id=siguiente_id(datos["reservas"]),
        cliente_id=cliente["id"],
        servicio_id=servicio.id,
        fecha=fecha,
        hora=hora,
        parametros=parametros,
        costo=costo,
        descuento=descuento,
    ).a_diccionario()
    datos["reservas"].append(reserva)
    guardar_datos(datos)
    LOGGER.info(
        "Reserva creada: reserva=%s, cliente=%s, servicio=%s, descuento=%.2f, costo=%.2f.",
        reserva["id"],
        reserva["cliente_id"],
        reserva["servicio_id"],
        reserva["descuento"],
        reserva["costo"],
    )
    print(f"Reserva #{reserva['id']} creada para {cliente['nombre']}.")
    if descuento:
        print(
            f"Subtotal: ${reserva['costo'] + descuento:.2f} | "
            f"Descuento: ${descuento:.2f} | Total: ${reserva['costo']:.2f}"
        )
    else:
        print(f"Costo estimado: ${reserva['costo']:.2f}.")


def listar_reservas(datos: dict[str, Any]) -> None:
    print("\n--- Reservas ---")
    if not datos["reservas"]:
        print("Todavia no hay reservas registradas.")
        return

    clientes = {cliente["id"]: cliente["nombre"] for cliente in datos["clientes"]}
    servicios = {servicio["id"]: servicio["nombre"] for servicio in datos["servicios"]}
    for reserva in datos["reservas"]:
        nombre_cliente = clientes.get(reserva["cliente_id"], "Cliente eliminado")
        nombre_servicio = servicios.get(reserva["servicio_id"], "Servicio eliminado")
        print(
            f"#{reserva['id']} | {nombre_cliente} | {nombre_servicio} | "
            f"{reserva['fecha']} {reserva['hora']} | {reserva['estado']}"
            + (
                f" | Descuento: ${reserva['descuento']:.0f}"
                if reserva.get("descuento", 0) > 0
                else ""
            )
            + (f" | Costo: ${reserva['costo']:.0f}" if "costo" in reserva else "")
        )


def cancelar_reserva(datos: dict[str, Any]) -> None:
    activas = [reserva for reserva in datos["reservas"] if reserva["estado"] == "Activa"]
    if not activas:
        print("No hay reservas activas para cancelar.")
        return

    listar_reservas(datos)
    while True:
        try:
            identificador = int(
                input("Numero de la reserva que deseas cancelar (0 para salir): ")
            )
        except ValueError:
            LOGGER.warning("Se ingreso un identificador de reserva invalido.")
            print("Ingresa un numero valido.")
            continue
        if identificador == 0:
            LOGGER.info("Cancelacion de reserva abandonada por el usuario.")
            print("Cancelacion cancelada. Volviendo al menu principal.")
            return
        reserva = next((item for item in activas if item["id"] == identificador), None)
        if reserva is None:
            LOGGER.warning("No se encontro una reserva activa con id=%s.", identificador)
            print("No se encontro una reserva activa con ese numero.")
            continue
        reserva["estado"] = "Cancelada"
        guardar_datos(datos)
        LOGGER.info("Reserva cancelada: id=%s.", identificador)
        print(f"Reserva #{identificador} cancelada.")
        return


def mostrar_menu() -> None:
    print(
        "\n=== Software FJ: clientes, servicios y reservas ===\n"
        "1. Registrar cliente\n"
        "2. Listar clientes\n"
        "3. Modificar cliente\n"
        "4. Eliminar cliente\n"
        "5. Listar servicios\n"
        "6. Modificar servicios\n"
        "7. Crear reserva\n"
        "8. Listar reservas\n"
        "9. Cancelar reserva\n"
        "0. Salir"
    )


def main() -> None:
    try:
        configurar_logging()
    except OSError as error:
        print(f"No se pudo iniciar el archivo de logs: {error}")
        return

    LOGGER.info("Inicio del sistema.")
    try:
        datos = cargar_datos()
    except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as error:
        LOGGER.exception("Error al cargar los datos.")
        print(f"No se pudieron cargar los datos de Software FJ: {error}")
        return

    opciones = {
        "1": lambda: registrar_cliente(datos),
        "2": lambda: listar_clientes(datos),
        "3": lambda: modificar_cliente(datos),
        "4": lambda: eliminar_cliente(datos),
        "5": lambda: listar_servicios(datos),
        "6": lambda: modificar_servicio(datos),
        "7": lambda: crear_reserva(datos),
        "8": lambda: listar_reservas(datos),
        "9": lambda: cancelar_reserva(datos),
    }

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opcion: ").strip()
        if opcion == "0":
            LOGGER.info("Cierre del sistema.")
            print("Gracias por usar el sistema de Software FJ.")
            return
        accion = opciones.get(opcion)
        if accion is None:
            LOGGER.warning("Opcion de menu invalida: %s.", opcion)
            print("Opcion no valida.")
            continue
        LOGGER.info("Accion de menu seleccionada: %s.", opcion)
        try:
            accion()
        except (OSError, ValueError, KeyError, TypeError) as error:
            LOGGER.exception("Error durante la opcion de menu %s.", opcion)
            print(f"No se pudo completar la opcion: {error}")


if __name__ == "__main__":
    main()