# 🌍 Álbum Mundial 2026 — API con FastAPI

## Cómo ejecutar

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# Swagger UI → http://127.0.0.1:8000/docs
```

---

## Modelos de datos

| Modelo | Atributos clave | Estado (soft delete) |
|---|---|---|
| **Jugador** | id, nombre, pais, posicion, numero_camiseta, edad, foto_url | ✅ activo / inactivo |
| **Lamina** | id, numero_lamina, jugador_id, tengo, cantidad_repetidas | ✅ activo / inactivo |
| **Intercambio** | id, lamina_id, tipo, precio, lamina_deseada_id, propietario, contacto, estado | ✅ disponible / completado / cancelado |

---

## Mapa de Endpoints

### 👤 Jugadores  `/jugadores`

| Método | Endpoint | Descripción | Criterio |
|--------|----------|-------------|---------|
| GET | `/jugadores/` | Listar jugadores activos | CRUD Read |
| GET | `/jugadores/todos` | Historial completo (activos + inactivos) | Historial |
| GET | `/jugadores/buscar?nombre=` | **Búsqueda por nombre** (no por ID) | Criterio 5 |
| GET | `/jugadores/filtrar?pais=&posicion=` | **Filtrar** por país y/o posición | Criterio 4 |
| GET | `/jugadores/{id}` | Obtener jugador por ID | CRUD Read |
| POST | `/jugadores/` | Crear jugador | CRUD Create |
| PUT | `/jugadores/{id}` | Actualizar jugador | CRUD Update |
| DELETE | `/jugadores/{id}` | **Soft delete** → estado=inactivo | Criterio 3 |

### 🗂️ Láminas  `/laminas`

| Método | Endpoint | Descripción | Criterio |
|--------|----------|-------------|---------|
| GET | `/laminas/` | Listar láminas activas | CRUD Read |
| GET | `/laminas/todas` | Historial completo | Historial |
| GET | `/laminas/faltantes` | Láminas que NO tengo | Regla negocio |
| GET | `/laminas/repetidas` | Láminas para intercambiar | Regla negocio |
| GET | `/laminas/buscar/{numero}` | **Búsqueda por número** de lámina (no ID) | Criterio 5 |
| GET | `/laminas/filtrar?tengo=&jugador_id=` | **Filtrar** por tengo/no tengo | Criterio 4 |
| GET | `/laminas/{id}` | Obtener lámina por ID | CRUD Read |
| POST | `/laminas/` | Registrar lámina | CRUD Create |
| PUT | `/laminas/{id}` | Actualizar (tengo / repetidas) | CRUD Update |
| DELETE | `/laminas/{id}` | **Soft delete** → estado=inactivo | Criterio 3 |

### 🔄 Marketplace  `/intercambios`

| Método | Endpoint | Descripción | Criterio |
|--------|----------|-------------|---------|
| GET | `/intercambios/` | Intercambios disponibles | CRUD Read |
| GET | `/intercambios/historial` | **Historial** (disponibles + completados + cancelados) | Criterio 3 |
| GET | `/intercambios/buscar?nombre=` | **Búsqueda por propietario** (no ID) | Criterio 5 |
| GET | `/intercambios/filtrar?tipo=&estado=` | **Filtrar** por tipo y estado | Criterio 4 |
| GET | `/intercambios/{id}` | Obtener intercambio por ID | CRUD Read |
| POST | `/intercambios/` | Publicar lámina en marketplace | CRUD Create |
| PUT | `/intercambios/{id}` | Actualizar publicación | CRUD Update |
| PATCH | `/intercambios/{id}/completar` | Marcar como completado | Regla negocio |
| DELETE | `/intercambios/{id}` | **Soft delete** → estado=cancelado | Criterio 3 |

---

## Reglas de negocio

| Regla | Modelo | Descripción |
|-------|--------|-------------|
| ❌ No duplicar camiseta+país | Jugador | No 2 jugadores activos del mismo país con igual número |
| 🔗 Integridad jugador | Lámina | No se puede crear lámina si el jugador no existe |
| 🔒 Proteger jugador con láminas | Jugador | No se puede desactivar si tiene láminas activas |
| 🔒 Proteger lámina con intercambios | Lámina | No se puede desactivar si tiene intercambios disponibles |
| 📦 Solo repetidas al marketplace | Intercambio | Solo se publican láminas con `cantidad_repetidas >= 1` |
| 💰 Precio obligatorio en ventas | Intercambio | Tipo=venta requiere precio |
| 🔁 Lámina deseada en intercambios | Intercambio | Tipo=intercambio requiere `lamina_deseada_id` |
| 🚫 Sin duplicados por propietario | Intercambio | Un propietario no puede tener 2 publicaciones de la misma lámina |
| 🗂️ Historial siempre disponible | Todos | El DELETE nunca borra físicamente, solo cambia estado |

---

## Manejo de excepciones (Criterio 7)

- `404` — ID no encontrado → mensaje descriptivo, servidor no cae
- `400` — Regla de negocio violada → detalle específico del error  
- `422` — Error de validación Pydantic → campos inválidos
- `500` — Error inesperado → mensaje genérico, servidor no expone stack trace
