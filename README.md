# Software FJ

Aplicacion de consola en Python para gestionar clientes, servicios y reservas.
Las entidades Cliente, Servicio y Reserva heredan de la clase abstracta
EntidadSistema. Cliente valida nombre, correo y telefono, y mantiene esos
datos personales en atributos privados con acceso mediante propiedades.
Servicio tambien es abstracta. ServicioSala, ServicioEquipos y
ServicioAsesoria sobrescriben la descripcion, validacion de parametros y
calculo del costo: por horas de sala, por cantidad de equipos o por horas de
asesoria, respectivamente.
Se aplica un descuento del 20% al superar 12 horas de sala, 20 equipos o
5 horas de asesoria. La reserva guarda y muestra el descuento y el total final.

## Uso

Ejecuta `python fase4.py` desde esta carpeta. El menu permite registrar,
consultar, modificar y eliminar clientes; ver y modificar servicios;
crear reservas y cancelar reservas activas. Los clientes eliminados
se retiran de nuevas reservas, pero el historial se conserva. El catalogo inicial incluye reserva de salas,
alquiler de equipos y asesorias especializadas. Los servicios agregados pueden
seleccionarse para nuevas reservas. Al eliminar un servicio, se retira de
nuevas reservas, pero el historial se conserva.

La informacion se guarda localmente en `software_fj_datos.json`, junto al
programa. Los eventos y errores se registran en `software_fj.log` en la misma
carpeta. No requiere instalar paquetes adicionales.

