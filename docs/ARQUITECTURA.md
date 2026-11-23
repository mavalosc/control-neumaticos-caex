# Arquitectura Técnica del Sistema
## Proyecto: Pórtico Dimensional Predictivo de Neumáticos CAEX
### Ingeniería Digital en Acción (Ecosistema DSD - USACH) · Unidad 1 · Equipo 3

---

## 0. Qué está implementado hoy (PROP-12, 23-11-2026)

Las secciones siguientes describen la **arquitectura objetivo**. El prototipo publicado implementa una parte; esta tabla dice cuál, para no afirmar lo que no existe.

| Componente de la arquitectura objetivo | Estado en el prototipo |
|---|---|
| Frontend SPA en Vercel | **Implementado** (`src/index.html`) |
| Supabase (PostgreSQL) con triggers de cupos y RLS | **Implementado. Es el backend del prototipo**: recibe cada solicitud de la app por internet y aplica las reglas antes de guardar. RLS con políticas permisivas de prototipo: la clave pública lee todo e inserta; desde PROP-12 ya no modifica órdenes directamente |
| Microservicio FastAPI | **No publicado.** Hay código de ejemplo en `backend/` (proyección lineal, con pruebas), pero la app no lo usa: habla directo con Supabase, y los cálculos están en el navegador y en los scripts de `modelo/` |
| ERP / SAP PM | **No conectado.** Las órdenes quedan solo en la base del prototipo; la app ya no dice que «sincroniza con ERP» |
| Pórtico instrumentado | **Simulado** (pantalla Simulador y datos sintéticos) |

### Capas de validación de la orden de trabajo

| Capa | Dónde vive | Qué hace |
|---|---|---|
| **Navegador** | `src/index.html`, con las reglas de `src/reglas.js` | Valida mientras se escribe: mensaje propio, contador y botón deshabilitado, sin borrar lo escrito |
| **Servidor** | **Supabase**, el backend del prototipo: los **CHECK y triggers de Postgres** (`docs/migraciones/2026-11-23_PROP-12_reglas_y_ordenes_cerradas.sql`) | Rechaza un motivo vacío o de más de 500 caracteres aunque alguien llame a la API REST directamente; aplica cada cambio de estado en una sola transacción; impide modificar o reactivar órdenes anuladas o ejecutadas |
| **Base de datos** | Tipos, `NOT NULL`, claves foráneas y `UNIQUE` del esquema (`docs/schema.sql`) | Estructura: no hay orden sin neumático ni ventana, ni dos órdenes con el mismo código |

**Respuesta del profesor (23-11-2026):** «todos tienen capa de servidor, así que todos tienen backend». Supabase es nuestro backend y sus CHECK y triggers son la capa servidor que pide la Semana 9. La prueba R8 de `docs/pruebas-rotura.md` lo demuestra: llama a la API sin pasar por la pantalla.

**Una regla vive en un solo archivo:** los límites se escriben en `src/reglas.js`. El SQL repite los mismos números, y la prueba `tests/reglas.test.js` falla si no coinciden.

**Pendiente declarado:** con la clave pública se puede seguir **insertando** órdenes y eventos (con las reglas aplicadas). Cerrar eso requiere autenticación real (usuarios con contraseña en Supabase), fuera del alcance de la Semana 9.

---

## 1. Visión General del Stack Tecnológico

El sistema implementa una arquitectura desacoplada y orientada a la nube, diseñada para soportar alta confiabilidad operativa en faenas mineras a cielo abierto:

```
[ PÓRTICO INSTRUMENTADO ] (Captura sensorial en tránsito: 3D LiDAR, Termografía, RFID)
           │
           ▼
[ FRONTEND SPA / VERCEL ] ──(REST / JSON)──► [ BACKEND API FASTAPI ]
           │                                            │
           │                                            ▼
           └────────────(Client SDK)───────────► [ SUPABASE (POSTGRESQL) ]
                                                        │
                                                        ▼
                                                [ ERP / SAP PM ] (Trazabilidad · objetivo, no conectado en el prototipo)
```

1. **Frontend:** Single Page Application (HTML5 / Tailwind CSS / Vanilla JS & React-ready) desplegada en **Vercel** con integración CI/CD automática desde la rama `main` de GitHub.
2. **Backend API:** Microservicio en **FastAPI (Python 3.11)** encargado del cálculo matemático de degradación dimensional y proyecciones de vida remanente.
3. **Persistencia:** **Supabase (PostgreSQL en la nube)** con soporte para constraints relacionales, triggers de liberación de cupos en taller y Row Level Security (RLS).
4. **Gestión y Seguimiento:** **Notion** (Kanban diario y Roadmap de Horizontes vinculado con historias `HU-01` a `HU-08`) y **wireframes anotados W1 a W5** en [`docs/wireframes/`](wireframes/README.md) (la maqueta preliminar sigue en Figma).

---

## 2. Parámetros del Modelo Predictivo y Dominio Operacional

- **Umbral de retiro:** **20,0 mm** de profundidad de banda de rodadura. Criterio experto de taller (Héctor Medina); configurable por neumático y faena ([respaldo](respaldo-bibliografico.md)).
- **Zonas de Criticidad de Vida Útil Remanente:**
  - 🔴 **Zona Roja (< 200 h):** Retiro inmediato programado. Alto riesgo de falla en rampa.
  - 🟡 **Zona Amarilla (< 500 h):** Planificación en la próxima ventana disponible de taller.
  - 🟢 **Zona Verde (> 500 h):** Operación normal dentro de tolerancia.
  - ⚪ **Sin datos (Gris):** Neumático sin lecturas previas suficientes para proyectar.
- **Niveles de Daño Físico (Algoritmo de Visión y Termografía):**
  - **Nivel 0:** Sin daño (operación regular).
  - **Nivel 1:** Leve (seguimiento en pasadas).
  - **Nivel 2:** Moderado (rocas incrustadas o desgaste irregular).
  - **Nivel 3:** Crítico (corte en flanco o sobrecalentamiento >95°C; desvío inmediato por Despacho Mina).

---

## 3. Modelo de Datos Relacional (Supabase PostgreSQL)

El esquema relacional completo se encuentra documentado e implementado en [`docs/schema.sql`](schema.sql):

- `camiones`: Identificación del CAEX (`codigo`, `modelo`, `horometro_h`, `estado_operacional`).
- `neumaticos`: Identidad única por `serial` (`caex_id`, `posicion` 1 a 6, `marca`, `umbral_retiro_mm`).
- `mediciones`: Telemetría del pórtico (`profundidad_mm`, `tasa_desgaste_por_100h`, `temperatura_flanco_c`, `horas_remanentes_calculadas`, `zona_calculada`, `modelo_version`).
- `danos_neumaticos`: Detecciones de visión (`severidad` 0 a 3, `descripcion`, `confianza_ia`, `validado_por_humano`).
- `ventanas_taller`: Turnos de mantenimiento (`dia`, `turno`, `cupos_totales`, `cupos_libres`, `horas_hasta_ventana`).
- `ordenes_trabajo`: Órdenes en ERP (`codigo`, `neumatico_id`, `ventana_id`, `tipo_intervencion`, `estado` programada/ejecutada/anulada).
- `historial_ordenes`: Auditoría inmutable de trazabilidad (`orden_id`, `autor`, `accion`, `motivo_obligatorio`, `detalles`).

Triggers automáticos:
- `trg_decrementar_cupo`: Descuenta automáticamente un cupo libre de la ventana al emitir una orden.
- `trg_liberar_cupo_anulacion`: Libera y restituye el cupo del taller al anular una orden programada.

---

## 4. Endpoints de la API REST (FastAPI)

| Método | Endpoint | Descripción | Códigos de Estado |
|---|---|---|---|
| `GET` | `/turnos/{fecha}/neumaticos` | Retorna los neumáticos de la flota ordenados por criticidad | `200 OK` |
| `GET` | `/neumaticos/{serial}` | Ficha individual, histórico de 8 pasadas y proyección | `200 OK`, `404 Not Found` |
| `GET` | `/neumaticos/{serial}/ventanas` | Ventanas disponibles y validación de margen temporal | `200 OK`, `404 Not Found` |
| `POST` | `/ordenes` | Emite una nueva OT y reserva cupo en taller | `201 Created`, `409 Conflict` (sin cupo) |
| `PATCH` | `/ordenes/{codigo}` | Modifica ventana o nota (motivo obligatorio en historial) | `200 OK`, `422 Unprocessable` (sin motivo) |
| `POST` | `/ordenes/{codigo}/anular` | Anula una orden programada, registra motivo y libera cupo | `200 OK`, `422 Unprocessable` |

---

## 5. Mapeo de Rutas en el Frontend (SPA / Hash Routing)

- `#/`: **Tablero del turno** (KPIs de flota, banner de daño crítico, filtros por zona/tasa y ordenamiento por horas remanentes).
- `#/c`: **Camiones** (Vista de flota y esquema matricial 6x4 de chasis con ruedas P1 a P6).
- `#/n/:serial`: **Ficha del neumático** (Gráfico SVG de degradación, bounding boxes de daño, termografía y human-in-the-loop).
- `#/a/:serial`: **Agendar intervención** (Selección de ventanas, control de capacidad y validación de margen horario).
- `#/o`: **Órdenes de trabajo** (Gestión de OTs, exportación CSV para proveedores y panel de trazabilidad).
- `#/e/:id`: **Modificar / Anular OT** (Modal de reasignación con motivo obligatorio y visualización de auditoría).
- `#/sim`: **Simulador del pórtico dimensional** (Demostración interactiva de captura sensorial sintética a 2-5 km/h).
