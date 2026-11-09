# Festival de la Leyenda Vallenata 2027

Sistema web de votaciones desarrollado como proyecto académico para el Festival de la Leyenda Vallenata 2027.

El aplicativo permite administrar ediciones, categorías, votaciones y participantes, además de registrar votos de usuarios autenticados mediante validaciones que impiden votos duplicados dentro de una misma categoría y edición.

## Tecnologías utilizadas

- Python
- Django 5.2.18
- MySQL 8.0
- HTML
- CSS
- JavaScript
- Git
- GitHub

## Arquitectura

El proyecto utiliza la arquitectura MVT de Django:

- **Model:** gestiona la estructura y persistencia de los datos.
- **View:** contiene la lógica del sistema y las validaciones.
- **Template:** presenta la información al usuario mediante HTML y CSS.

## Aplicaciones del proyecto

### Accounts

Gestiona las funciones relacionadas con los usuarios:

- Registro de usuarios
- Inicio de sesión
- Cierre de sesión
- Control de autenticación

### Votaciones

Gestiona el funcionamiento principal del sistema:

- Ediciones del festival
- Categorías
- Votaciones
- Participantes u opciones
- Registro de votos
- Validaciones de voto
- Historial de votos
- Auditoría
- API de categorías

## Roles de usuario

### Usuario regular

Puede:

- Consultar las categorías disponibles.
- Consultar participantes.
- Votar en diferentes categorías.
- Emitir solamente un voto por categoría y edición.
- Consultar sus votos registrados.

### Jurado

Puede consultar la información del sistema, pero no puede registrar votos.

### Administrador

Puede administrar:

- Ediciones
- Categorías
- Votaciones
- Opciones o participantes
- Votos
- Registros de auditoría

Los administradores no participan como votantes.

## Regla principal de votación

Cada usuario puede emitir solamente un voto por categoría y edición.

Un usuario puede votar en diferentes categorías, pero después de registrar un voto en una categoría no puede seleccionar otro participante dentro de esa misma categoría.

La restricción se controla tanto desde la lógica de Django como desde la base de datos.

## Validaciones implementadas

El sistema verifica:

- Usuario autenticado.
- Permisos para votar.
- Edición activa.
- Categoría activa.
- Votación activa.
- Opción activa.
- Fechas válidas de votación.
- Correspondencia entre opción y categoría.
- Existencia de un voto previo.
- Protección contra solicitudes duplicadas.
- Restricción de duplicidad a nivel de base de datos.

## Historial de votos

Los usuarios autenticados pueden consultar sus votos desde:

```text
/mis-votos/