@'
# Festival de la Leyenda Vallenata 2027
## Sistema Web de Votaciones

Proyecto desarrollado para la asignatura **Desarrollo Web** de la Fundación Universitaria del Área Andina.

El aplicativo corresponde a una primera versión funcional de un sistema web de votaciones para el Festival de la Leyenda Vallenata 2027. Permite administrar ediciones, categorías, votaciones y participantes, además de gestionar usuarios y mostrar la información de manera dinámica mediante Django y MySQL.

---

## Tecnologías utilizadas

- Python
- Django
- MySQL
- HTML5
- CSS3
- Django ORM
- Django Authentication
- Git y GitHub

---

## Arquitectura

El proyecto utiliza el patrón **MVT (Model - View - Template)** implementado por Django.

### Model

Define la estructura de los datos y sus relaciones.

Entre las principales entidades se encuentran:

- Edición
- Categoría
- Votación
- Opción o participante
- Voto
- Auditoría de votos

### View

Contiene la lógica que procesa las solicitudes realizadas por los usuarios.

Las vistas permiten:

- Consultar categorías.
- Consultar votaciones.
- Visualizar participantes.
- Registrar votos.
- Validar permisos de usuario.
- Evitar votos duplicados dentro de una misma categoría.

### Template

Corresponde a las interfaces HTML que se muestran al usuario.

El sistema cuenta con interfaces para:

- Página principal.
- Categorías.
- Detalle de categorías.
- Participantes y votaciones.
- Inicio de sesión.
- Registro de usuarios.

---

## Aplicaciones del proyecto

### accounts

Gestiona las funcionalidades relacionadas con los usuarios:

- Registro.
- Inicio de sesión.
- Cierre de sesión.
- Formularios de autenticación.

### votaciones

Contiene la lógica principal del sistema:

- Ediciones del festival.
- Categorías.
- Votaciones.
- Participantes.
- Registro de votos.
- Validaciones.
- Administración de información.

---

## Base de datos

El proyecto utiliza **MySQL** como sistema gestor de base de datos.

La información de conexión se maneja mediante variables de entorno para evitar almacenar credenciales privadas directamente en el código.

Ejemplo de archivo `.env`:

```env
DB_NAME=festival_vallenato_2027
DB_USER=root
DB_PASSWORD=TU_CONTRASENA
DB_HOST=127.0.0.1
DB_PORT=3306