"""Sistema de gestion de clientes, Software FJ."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ARCHIVO_DATOS = Path(__file__).with_name("software_fj_datos.json")

SERVICIOS_INICIALES = [
    {"id": 1, "nombre": "Reserva de sala de reuniones", "categoria": "Salas", "precio": 0.0},
    {"id": 2, "nombre": "Alquiler de equipos", "categoria": "Equipos", "precio": 0.0},
    {"id": 3, "nombre": "Asesoria especializada", "categoria": "Asesorias", "precio": 0.0},
]


def guardar_datos(datos: dict[str, Any]) -> None:
    """Guarda los datos de forma legible para el usuario."""
    with ARCHIVO_DATOS.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def cargar_datos() -> dict[str, Any]:
    if not ARCHIVO_DATOS.exists():
        datos = {"clientes": [], "servicios": SERVICIOS_INICIALES.copy(), "reservas": []}
        guardar_datos(datos)
        return datos

    with ARCHIVO_DATOS.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    if not isinstance(datos, dict) or any(
        not isinstance(datos.get(clave), list)
        for clave in ("clientes", "servicios", "reservas")
    ):
        raise ValueError("El archivo de datos no tiene el formato esperado.")
    return datos


def siguiente_id(registros: list[dict[str, Any]]) -> int:
    return max((registro["id"] for registro in registros), default=0) + 1


def pedir_texto(mensaje: str) -> str:
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("El valor no puede quedar vacio.")


def pedir_precio(mensaje: str) -> float:
    while True:
        try:
            precio = float(input(mensaje).replace(",", ".").strip())
            if precio >= 0:
                return precio
        except ValueError:
            pass
        print("Ingresa un precio numerico igual o mayor que cero.")


def registrar_cliente(datos: dict[str, Any]) -> None:
    print("\n--- Registrar cliente ---")
    nombre = pedir_texto("Nombre completo: ")
    correo = pedir_texto("Correo electronico: ")
    telefono = pedir_texto("Telefono: ")
    cliente = {
        "id": siguiente_id(datos["clientes"]),
        "nombre": nombre,
        "correo": correo,
        "telefono": telefono,
    }
    datos["clientes"].append(cliente)
    guardar_datos(datos)
    print(f"Cliente registrado con el numero {cliente['id']}.")


def listar_clientes(datos: dict[str, Any]) -> None:
    print("\n--- Clientes ---")
    if not datos["clientes"]:
        print("Todavia no hay clientes registrados.")
        return
    for cliente in datos["clientes"]:
        print(
            f"#{cliente['id']} | {cliente['nombre']} | "
            f"{cliente['correo']} | {cliente['telefono']}"
        )


def listar_servicios(datos: dict[str, Any]) -> None:
    print("\n--- Servicios de Software FJ ---")
    servicios = [s for s in datos["servicios"] if s.get("activo", True)]
    if not servicios:
        print("No hay servicios disponibles.")
        return
    for servicio in servicios:
        print(
            f"#{servicio['id']} | {servicio['nombre']} | "
            f"{servicio['categoria']} | ${servicio['precio']:.2f}"
        )


def agregar_servicio(datos: dict[str, Any]) -> None:
    print("\n--- Agregar servicio ---")
    nombre = pedir_texto("Nombre del servicio: ")
    categoria = pedir_texto("Categoria (salas, equipos, asesorias, etc.): ")
    precio = pedir_precio("Precio: $")
    servicio = {
        "id": siguiente_id(datos["servicios"]),
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "activo": True,
    }
    datos["servicios"].append(servicio)
    guardar_datos(datos)
    print(f"Servicio agregado con el numero {servicio['id']}.")


def modificar_servicio(datos: dict[str, Any]) -> None:
    print("\n--- Modificar servicio ---")
    servicios = [s for s in datos["servicios"] if s.get("activo", True)]
    if not servicios:
        print("No hay servicios disponibles para modificar.")
        return
    listar_servicios(datos)
    servicio = elegir_registro(servicios, "servicios")
    if servicio is None:
        return

    print("1. Modificar nombre\n2. Modificar categoria\n3. Modificar tarifa")
    opcion = input("Selecciona el dato que deseas modificar: ").strip()
    if opcion == "1":
        servicio["nombre"] = pedir_texto("Nuevo nombre: ")
    elif opcion == "2":
        servicio["categoria"] = pedir_texto("Nueva categoria: ")
    elif opcion == "3":
        servicio["precio"] = pedir_precio("Nueva tarifa: $")
    else:
        print("Opcion no valida; no se realizaron cambios.")
        return

    guardar_datos(datos)
    print(f"Servicio #{servicio['id']} actualizado.")


def eliminar_servicio(datos: dict[str, Any]) -> None:
    print("\n--- Eliminar servicio ---")
    servicios = [s for s in datos["servicios"] if s.get("activo", True)]
    if not servicios:
        print("No hay servicios disponibles para eliminar.")
        return
    listar_servicios(datos)
    servicio = elegir_registro(servicios, "servicios")
    if servicio is None:
        return

    servicio["activo"] = False
    guardar_datos(datos)
    print(
        f"Servicio #{servicio['id']} eliminado del catalogo. "
        "Sus reservas anteriores se conservan."
    )


def elegir_registro(registros: list[dict[str, Any]], tipo: str) -> dict[str, Any] | None:
    if not registros:
        print(f"No hay {tipo} disponibles.")
        return None

    while True:
        try:
            identificador = int(input(f"Numero de {tipo[:-1]}: "))
        except ValueError:
            print("Ingresa un numero valido.")
            continue
        for registro in registros:
            if registro["id"] == identificador:
                return registro
        print(f"No se encontro ese {tipo[:-1]}.")


def crear_reserva(datos: dict[str, Any]) -> None:
    print("\n--- Crear reserva ---")
    cliente = elegir_registro(datos["clientes"], "clientes")
    if cliente is None:
        return
    servicios = [s for s in datos["servicios"] if s.get("activo", True)]
    servicio = elegir_registro(servicios, "servicios")
    if servicio is None:
        return

    while True:
        fecha = input("Fecha (AAAA-MM-DD): ").strip()
        hora = input("Hora (HH:MM): ").strip()
        try:
            datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            break
        except ValueError:
            print("Fecha u hora no valida. Usa los formatos indicados.")

    ocupada = any(
        reserva["servicio_id"] == servicio["id"]
        and reserva["fecha"] == fecha
        and reserva["hora"] == hora
        and reserva["estado"] == "Activa"
        for reserva in datos["reservas"]
    )
    if ocupada:
        print("Ese servicio ya tiene una reserva activa en esa fecha y hora.")
        return

    reserva = {
        "id": siguiente_id(datos["reservas"]),
        "cliente_id": cliente["id"],
        "servicio_id": servicio["id"],
        "fecha": fecha,
        "hora": hora,
        "estado": "Activa",
    }
    datos["reservas"].append(reserva)
    guardar_datos(datos)
    print(f"Reserva #{reserva['id']} creada para {cliente['nombre']}.")


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
        )


def cancelar_reserva(datos: dict[str, Any]) -> None:
    activas = [reserva for reserva in datos["reservas"] if reserva["estado"] == "Activa"]
    if not activas:
        print("No hay reservas activas para cancelar.")
        return

    listar_reservas(datos)
    while True:
        try:
            identificador = int(input("Numero de la reserva que deseas cancelar: "))
        except ValueError:
            print("Ingresa un numero valido.")
            continue
        reserva = next((item for item in activas if item["id"] == identificador), None)
        if reserva is None:
            print("No se encontro una reserva activa con ese numero.")
            continue
        reserva["estado"] = "Cancelada"
        guardar_datos(datos)
        print(f"Reserva #{identificador} cancelada.")
        return


def mostrar_menu() -> None:
    print(
        "\n=== Software FJ: clientes, servicios y reservas ===\n"
        "1. Registrar cliente\n"
        "2. Listar clientes\n"
        "3. Listar servicios\n"
        "4. Agregar servicio\n"
        "5. Crear reserva\n"
        "6. Listar reservas\n"
        "7. Cancelar reserva\n"
        "8. Modificar servicio\n"
        "9. Eliminar servicio\n"
        "0. Salir"
    )


def main() -> None:
    try:
        datos = cargar_datos()
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"No se pudieron cargar los datos de Software FJ: {error}")
        return

    opciones = {
        "1": lambda: registrar_cliente(datos),
        "2": lambda: listar_clientes(datos),
        "3": lambda: listar_servicios(datos),
        "4": lambda: agregar_servicio(datos),
        "5": lambda: crear_reserva(datos),
        "6": lambda: listar_reservas(datos),
        "7": lambda: cancelar_reserva(datos),
        "8": lambda: modificar_servicio(datos),
        "9": lambda: eliminar_servicio(datos),
    }

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opcion: ").strip()
        if opcion == "0":
            print("Gracias por usar el sistema de Software FJ.")
            return
        accion = opciones.get(opcion)
        if accion is None:
            print("Opcion no valida.")
            continue
        try:
            accion()
        except OSError as error:
            print(f"No se pudieron guardar los cambios: {error}")


if __name__ == "__main__":
    main()