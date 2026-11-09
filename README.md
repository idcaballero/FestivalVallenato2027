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

Los usuarios autenticados pueden consultar los votos que han registrado desde:

```text
/mis-votos/
```

Esta sección muestra la información correspondiente a cada voto activo del usuario:

- Categoría.
- Participante seleccionado.
- Edición.
- Fecha y hora del voto.
- Estado del voto.

Los votos anulados no se presentan como votos activos dentro del historial del usuario.

## API GET

El proyecto incluye un endpoint GET que permite consultar las categorías activas y sus opciones registradas en la base de datos.

```text
/api/categorias/
```

En el entorno local puede consultarse desde:

```text
http://127.0.0.1:8000/api/categorias/
```

La información es generada dinámicamente a partir de los registros almacenados en MySQL y se devuelve en formato JSON.

Ejemplo de la estructura de respuesta:

```json
{
  "categorias": [
    {
      "id": 1,
      "nombre": "Acordeonero Infantil",
      "edicion": 2027,
      "activa": true,
      "votaciones": [
        {
          "id": 1,
          "nombre": "Votación Acordeonero Infantil 2027"
        }
      ],
      "opciones": [
        {
          "id": 1,
          "nombre": "Samuel Rojas",
          "votacion_id": 1,
          "votacion": "Votación Acordeonero Infantil 2027"
        }
      ]
    }
  ]
}
```

## Base de datos

El sistema utiliza MySQL 8.0 como motor de base de datos.

La persistencia de los votos fue verificada directamente mediante MySQL Workbench y comparada con los registros visibles desde Django Admin.

Cada voto almacena información relacionada con:

- Usuario.
- Edición.
- Categoría.
- Opción seleccionada.
- Fecha y hora del voto.
- Estado de anulación.
- Usuario responsable de una anulación, cuando corresponda.

## Protección contra votos duplicados

El sistema controla la duplicidad de votos desde dos niveles.

En la lógica de Django se verifica si el usuario ya cuenta con un voto activo para la misma categoría y edición antes de registrar uno nuevo.

Adicionalmente, la base de datos contiene una restricción que impide mantener más de un voto activo para la misma combinación de usuario, edición y categoría.

Esta protección también permite controlar solicitudes concurrentes. Durante las pruebas se enviaron dos solicitudes de voto de manera simultánea y solamente un voto válido permaneció registrado.

## Auditoría de votos

El sistema conserva un registro de las operaciones relacionadas con los votos.

Se manejan eventos como:

- Registro de voto.
- Anulación de voto.
- Usuario responsable de la anulación.
- Fecha de la operación.
- Motivo de anulación, cuando corresponde.

Los votos anulados permanecen separados de los votos válidos para conservar el historial y facilitar la revisión administrativa.

## Casos de prueba realizados

Para comprobar el funcionamiento del módulo se realizaron los siguientes casos:

- **CP-01:** registro correcto de un voto válido por un usuario autenticado.
- **CP-02:** rechazo de un segundo voto dentro de la misma categoría y edición.
- **CP-03:** voto permitido en una categoría diferente.
- **CP-04:** usuario no autenticado no puede registrar votos.
- **CP-05:** una categoría inactiva deja de estar disponible para votación.
- **CP-06:** rechazo de una opción que no corresponde a la categoría indicada.
- **CP-07:** consulta del historial de votos mediante la sección “Mis votos”.
- **CP-08:** comparación de los votos registrados entre Django Admin y MySQL.
- **CP-09:** dos solicitudes simultáneas producen solamente un voto válido.
- **CP-10:** consulta de categorías y opciones mediante el endpoint GET `/api/categorias/`.

## Instalación del proyecto

Clonar el repositorio:

```bash
git clone https://github.com/idcaballero/FestivalVallenato2027.git
```

Ingresar al proyecto:

```bash
cd FestivalVallenato2027
```

Crear el entorno virtual:

```bash
python -m venv venv
```

Activarlo en Windows:

```bash
venv\Scripts\activate
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

Crear un archivo `.env` con las variables necesarias para la conexión a MySQL.

El archivo `.env` no está incluido en el repositorio por razones de seguridad.

Aplicar las migraciones:

```bash
python manage.py migrate
```

Verificar la configuración del proyecto:

```bash
python manage.py check
```

Ejecutar el servidor:

```bash
python manage.py runserver
```

Abrir la aplicación desde:

```text
http://127.0.0.1:8000/
```

## Seguridad

El proyecto implementa diferentes medidas para proteger el proceso de votación:

- Autenticación obligatoria para registrar votos.
- Protección CSRF en los formularios.
- Uso de solicitudes POST para el registro de votos.
- Validación de roles y permisos.
- Validación del estado de la edición, categoría, votación y opción.
- Validación de correspondencia entre categoría y opción.
- Prevención de votos duplicados.
- Restricción de duplicidad a nivel de base de datos.
- Conservación de registros de auditoría.

Las credenciales de MySQL se almacenan en el archivo `.env`, el cual está excluido del repositorio mediante `.gitignore`.

## Estructura principal del proyecto

```text
FestivalVallenato2027/
│
├── accounts/
├── festival_vallenato/
├── media/
│   ├── categorias/
│   └── opciones/
├── static/
│   ├── css/
│   └── images/
├── templates/
│   └── base.html
├── votaciones/
│   ├── migrations/
│   ├── templates/
│   │   └── votaciones/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## Proyecto académico

Proyecto desarrollado para la asignatura **Desarrollo Web** de la **Fundación Universitaria del Área Andina**.

**Entrega 3:** Implementación del módulo de votaciones, validaciones y API GET.

El repositorio contiene la versión funcional del sistema, las migraciones de la base de datos, los templates, archivos estáticos, imágenes utilizadas por la aplicación y la documentación necesaria para su ejecución.