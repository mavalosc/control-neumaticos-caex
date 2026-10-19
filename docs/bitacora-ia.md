# Bitácora de uso de Inteligencia Artificial
## Pórtico Dimensional Predictivo de Neumáticos CAEX · Equipo 3

Registro de las interacciones relevantes con asistentes de IA, según la pauta del Ecosistema DSD. Cada entrada tiene cuatro componentes:

1. **Contexto:** estado del código, de Supabase o del problema antes de la consulta.
2. **Intención:** el prompt que escribió el estudiante, citado textualmente.
3. **Restricciones:** condiciones técnicas impuestas a la IA.
4. **Verificación:** pruebas o revisión humana que validaron, corrigieron o descartaron lo generado.

**Herramientas usadas:** Gemini en el entorno Antigravity (11 y 12 de octubre de 2026) y Claude Code en VS Code (14 de octubre de 2026).

> **Regla del equipo:** nada generado por IA se fusiona en `main` sin que un integrante lo haya ejecutado, revisado y pueda explicarlo. La sección final indica qué debe saber explicar cada uno.

---

## IA-01 · Generar el prototipo navegable desde el código base
**Herramienta:** Gemini (Antigravity) · **Fecha:** 11-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | El equipo tenía una SPA de un solo archivo HTML (tablero, camiones, ficha, agenda y órdenes) con 6 CAEX y datos en memoria. Hoy se conserva en `docs/historico/` y `frontend/`. |
| **Intención** | «necesito generar un prototipo, tengo el siguiente codigo fuente: [código HTML completo]» |
| **Restricciones** | Mantener la lógica de negocio: umbral de retiro de 20,0 mm; zonas roja (< 200 h), amarilla (< 500 h) y verde (> 500 h); 6 posiciones por CAEX; ventanas con 3 cupos; motivo obligatorio para modificar o anular una OT. |
| **Verificación** | El prototipo se abrió en el navegador y se revisó el flujo Tablero → Ficha → Agendar → Órdenes antes de subirlo (commit `5ddeb0d`). La IA agregó un simulador de pórtico, el esquema 6x4 y persistencia en `localStorage`. **Hallazgo:** el prototipo cargaba Tailwind desde una URL interna (`gstatic.com/antigravity/web/dev/…`), una dependencia frágil que queda registrada como deuda técnica. |

## IA-02 · Auditoría del proyecto contra las entregas 1 y 2
**Herramienta:** Gemini (Antigravity) · **Fecha:** 11-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | Repositorio con frontend, backend FastAPI y documentos de los avances 1 y 2. No había `.gitignore`, `.env.example`, carpeta `/src` ni esquema de base de datos. |
| **Intención** | «este es el proyecto que tengo (carpeta) y las entregas 1 y 2, necesito que lo revises y encuentres los errores» (adjuntando el contexto del curso y la lista de requisitos de las entregas 3 y 4) |
| **Restricciones** | Stack definido: GitHub (`main` y `dev`), Supabase (PostgreSQL), Vercel, Notion con códigos `HU-XX`; historias INVEST con Gherkin. |
| **Verificación** | Se revisaron a mano los hallazgos en el código: en `backend/app/main.py`, `UMBRAL_MM = 30.0` en vez de 20,0; en `proyeccion.py`, zonas de 300 h y 600 h en vez de 200 h y 500 h. Ambos se corrigieron. Las 4 pruebas de `backend/tests/test_proyeccion.py` (proyección lineal, sin desgaste, tasa y semáforo 200/500 h) se ejecutaron el 14-10-2026 y pasaron. **Corrección humana:** al ejecutar `schema.sql` por segunda vez falló porque no era re-ejecutable; se corrigió en el commit `d44d78a` («hacer esquema idempotente»). |

## IA-03 · Guías para conectar GitHub, Supabase, Vercel y Notion
**Herramienta:** Gemini (Antigravity) · **Fecha:** 11 y 12-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | Repositorio local listo, sin conexión a las plataformas. |
| **Intención** | «no entiendo como hacer el paso 1 de la seccion 4. Guía Paso a Paso para Conectar las Plataformas, necesito más detalles» y «necesito más detalles e instrucciones de como verificar que estoy haciendo lo correcto» |
| **Restricciones** | No compartir contraseñas con la IA; cada paso debe incluir cómo verificar el resultado. |
| **Verificación** | Se siguieron los pasos y se comprobó cada resultado en la plataforma: repositorio `mavalosc/control-neumaticos-caex` con ramas `main` y `dev`, 7 tablas visibles en el Table Editor de Supabase y proyecto creado en Vercel. **Error de la IA detectado después (ver IA-05):** la guía decía que las variables `VITE_SUPABASE_*` en Vercel conectaban el prototipo, pero un HTML estático sin compilación no las lee. |

## IA-04 · Ampliar la flota a 67 CAEX con paginación
**Herramienta:** Gemini (Antigravity) · **Fecha:** 12-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | Prototipo con 6 CAEX; la faena real opera una flota mayor. |
| **Intención** | *(Prompt reconstruido: el texto exacto quedó en la sesión de Antigravity y el equipo debe completarlo.)* Ampliar la flota simulada a 67 camiones (402 neumáticos) y paginar las vistas del tablero y de camiones. |
| **Restricciones** | Conservar los neumáticos y daños conocidos de los 6 CAEX originales. |
| **Verificación** | La sesión quedó interrumpida: la flota se amplió, pero el script de paginación nunca se aplicó. La revisión de IA-05 lo detectó con `git status` y `git diff`. El script se probó primero sobre una copia y luego se aplicó. Se verificó en Chrome headless: «Mostrando 1 a 25 de 402 neumáticos (67 CAEX · 402 neumáticos)», sin errores en la consola. |

## IA-05 · Revisar lo hecho por la IA anterior y conectar el prototipo a Supabase
**Herramienta:** Claude Code (VS Code) · **Fecha:** 14-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | El prototipo guardaba todo en `localStorage`. En Supabase, las tablas existían, pero la API devolvía 0 filas. |
| **Intención** | «te pasaré un chat que tengo con otra IA por un trabajo que estoy haciendo, necesito que lo revises, conozcas el contexto, me ayudes a seguir trabajando» y luego «Conectar de verdad el prototipo a Supabase […] con la librería supabase-js cargada desde un CDN y la URL y clave anon puestas en un config.js, sin necesidad de compilar nada […] confirma si corrió schema.sql en Supabase» |
| **Restricciones** | Sin proceso de compilación (sin npm); solo la clave **anon** en el navegador; si no hay conexión, el prototipo debe seguir funcionando en modo local; sin compartir contraseñas. |
| **Verificación** | **Diagnóstico con prueba real:** una inserción con la clave anon devolvió `42501 new row violates row-level security policy`. Así se comprobó que RLS estaba activo y sin políticas: el esquema sí había corrido, pero nada era visible. Se agregaron políticas RLS y triggers `SECURITY DEFINER` (`docs/schema.sql`), más un seed generado desde el prototipo (`scripts/generar_seed.py`). **Error de la IA corregido al ejecutarlo:** el generador convertía `08:00` dentro de textos en claves JSON y fallaba; se restringió la expresión regular. **Prueba de integración:** tras ejecutar los SQL, el conteo dio 67 · 405 · 7; una OT de prueba (`ot-9001`) movió los cupos 3→2, luego 2→1 y 3→3, y al anularla volvió a 2. El intento de `DELETE` fue rechazado. El sitio en Vercel muestra el indicador «Supabase». |

## IA-06 · Seguridad de credenciales y flujo de ramas
**Herramienta:** Claude Code · **Fecha:** 14-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | `.env.example`, publicado en GitHub, tenía la URL y la clave anon reales. Todos los commits se hacían directo en `main`, y `actualizar.bat` subía a `main`. |
| **Intención** | «Limpiar el repositorio: borrar los scripts temporales, marca la carpeta frontend/ duplicada como versión antigua y corregir actualizar.bat para que trabaje en dev […] Hacer un commit en dev y abrir un Pull Request hacia main» |
| **Restricciones** | No exponer la clave `service_role`; todo cambio entra a `main` por Pull Request. |
| **Verificación** | Se revisó con `git check-ignore -v .env` que `.env` no se versiona. `.env.example` quedó con valores de ejemplo. El cambio se subió a `dev` y se fusionó con el **PR #1**. Vercel desplegó `main` y se comprobó en el sitio publicado que `config.js` y `db.js` responden 200. **Nota:** la clave anon queda en `src/config.js` a propósito: es pública por diseño y la protegen las políticas RLS documentadas en `docs/datos.md`. |

## IA-07 · Auditoría contra la rúbrica de las entregas 3 y 4
**Herramienta:** Claude Code · **Fecha:** 14-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | Faltaban `docs/bitacora-ia.md` y `docs/datos.md`. Los wireframes eran la maqueta antigua y había tres numeraciones de historias (HU-01, HU-F01 y la de los wireframes). |
| **Intención** | «Te daré las instrucciones de las rubricas 3 y 4, ayudame a verificar la entrega» y luego «te dejo lo que tenemos en notion, ayudame a cumplir con la rubrica» |
| **Restricciones** | Los códigos HU deben ser idénticos a los del Roadmap de Notion. Cada escenario Gherkin debe describir lo que el prototipo **hace realmente** (sin funciones inventadas). Los wireframes deben salir del prototipo real. |
| **Verificación** | Se leyó el Roadmap de Notion: HU-01 a HU-08 coinciden en nombre con `historias.md`. Cada «Entonces» se contrastó con el texto real de la interfaz en `src/index.html`. **Defecto detectado y corregido:** HU-08 exigía un motivo obligatorio, pero el prototipo guardaba con «actualización operacional» por defecto. Ahora el botón queda deshabilitado y aparece «El motivo del cambio es obligatorio.». También se agregaron la etiqueta «por confirmar» (HU-04) y el mensaje sin resultados en Camiones (HU-03). Los wireframes W1 a W5 se generaron con Chrome headless sobre el prototipo y se revisaron visualmente: una marca [4] de W4 no apareció porque el botón se llama «Modificar» y no «Modificar o anular»; se corrigió. |

## IA-08 · Ordenar el espacio de Notion según la rúbrica
**Herramienta:** Claude Code con la API de Notion · **Fecha:** 14-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | El Kanban "Registro de tareas" tenía las 3 tareas de ejemplo de la plantilla. Faltaban roles, problema y próximo hito; había dos repositorios enlazados y filas vacías en el Roadmap. |
| **Intención** | «Me ayudas con esto, yo no se como hacerlo, te puedo conseguir una apikey y lo haces tu? necesito que me digas como conseguir la apikey» |
| **Restricciones** | Clave de integración guardada solo en `.env` local (nunca en el chat ni en GitHub); permisos limitados a la página del grupo; no inventar roles (los no definidos quedan «por asignar»); mostrar un plan antes de aplicar cambios. |
| **Verificación** | El script corrió primero en modo plan y se revisó la lista de 45 cambios antes de aplicarlos. Después se leyó Notion de vuelta: 4 integrantes con rol, un solo repositorio y 15 tareas `[HU-XX]`/`[E3]`/`[E4]` con responsable. **Hallazgo:** la integración solo veía una copia de la página, no la publicada originalmente; el equipo la usó en un primer momento. **Decisión final:** la página oficial del equipo está en un espacio donde el integrante no tiene permiso para crear integraciones (Notion: *You don't have permission to create internal connections*). Por eso la IA generó `Kanban.csv`, `Roadmap.csv` y el texto de las secciones, y el integrante los importó y pegó a mano. Después se verificó la página publicada: tabla de roles, Kanban con 4 estados y vista de tablero, Roadmap con HU-01 a HU-08, enlaces a las entregas 3 y 4, sin Roadmap duplicado ni errores de tipeo. Finalmente, el contenido se trasladó a la página **Grupo 3 del espacio del curso (Ecosistema DSD)**, creada por el profesor, que es la página oficial y la única enlazada en el README. |

## IA-09 · Hallazgo humano: los buscadores escribían al revés
**Herramienta:** Claude Code · **Fecha:** 17-10-2026 · **Autor:** Manuel Ávalos (detección en prueba manual)

| Componente | Detalle |
|---|---|
| **Contexto** | Prototipo publicado en Vercel. Al probarlo a mano, el integrante escribió «165» en el buscador de Camiones y apareció «561». El error venía del código base original del equipo (`oninput="…; document.getElementById('q').focus();"`) y la IA lo conservó al generar el prototipo (IA-01). **Ninguna revisión con IA lo detectó** (IA-05, IA-07): las pruebas automáticas asignaban el texto completo de una vez, en lugar de teclearlo carácter por carácter como lo hace una persona. |
| **Intención** | «en el prototipo montado en vercel, el buscador de camiones, escribe de derecha a izquierda, cuando digito 165, en el formulario aparece 561» |
| **Restricciones** | Corregir la causa en todos los buscadores, no solo en el reportado; no cambiar el comportamiento de filtrado; comprobar con una prueba que reproduzca el tecleo real. |
| **Verificación** | **Causa:** cada tecla vuelve a dibujar la pantalla y `focus()` devolvía el cursor a la posición 0, así que cada carácter nuevo quedaba delante del anterior. Afectaba a los 3 buscadores (Tablero, Camiones y Órdenes). **Corrección:** nueva función `enfocarAlFinal()` que deja el cursor al final del texto. **Segundo defecto encontrado al probar:** Tablero y Camiones compartían la variable `searchQuery`, así que lo buscado en una vista aparecía en la otra; Camiones ahora usa `truckSearchQuery`. **Prueba:** página de prueba que teclea «1», «6», «5» en la posición del cursor en cada buscador. Antes daba «561»; después da «165» en los tres, sin errores de consola (commit `0c10148`). **Aprendizaje:** las pruebas de interfaz deben simular la interacción real del usuario; probar a mano el sitio publicado sigue siendo necesario. |

## IA-10 · Metodología y PoC del modelo de desgaste y vida útil remanente
**Herramienta:** Claude Code · **Fecha:** 18-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | El equipo propuso identificar las variables que influyen en el desgaste (presión, temperatura, carga, velocidad, terreno, pendiente, posición, frenadas, entre otras) con un modelo de Deep Learning cuyos coeficientes alimentarían una regresión multivariable. No había datos ni código del modelo. |
| **Intención** | La propuesta completa del equipo («Identificación de variables que influyen en el desgaste de neumáticos… Modelo de Deep Learning para extracción de patrones… Modelo predictivo para toma de decisiones») y luego «ejecuta la opciones 1 y 3» (documento de metodología y PoC con datos sintéticos). |
| **Restricciones** | Datos sintéticos con efectos **conocidos** para comprobar si el método los recupera; modelos interpretables; separación de prueba por camión completo; comparación con el método actual del backend; resultados reproducibles con semilla fija; no presentar recomendaciones como causales. |
| **Verificación** | La IA revisó la propuesta y la ajustó: modelos interpretables con SHAP antes que Deep Learning (pocos datos), separación de desgaste y daño, censura e indicador TKPH. **Calibración humana del simulador:** la primera versión daba 58 % de fallas por daño; se recalibró a 28 %, cercano al ~30 % de la industria. **Resultados en 14 camiones no vistos:** error de horas remanentes a 30 mm de 65 h (método actual: 222 h), con 95 % de estimaciones dentro de ±200 h y 3 % optimistas (método actual: 27,5 %). **Errores corregidos antes de publicar:** la tabla mostraba el TKPH como elasticidad (confuso) y se cambió a «+10 % de TKPH»; el documento atribuía el falso efecto de las frenadas a una correlación con el terreno, pero al revisar los datos la correlación era nula y se corrigió la explicación. **Hallazgo:** SHAP pone la temperatura del neumático en tercer lugar aunque no causa desgaste, lo que confirma que importancia no es causalidad. |

## IA-11 · Telemetría TPMS, temperatura y control de densidad en el simulador del pórtico
**Herramienta:** Claude Code · **Fecha:** 18-10-2026 · **Autor:** Manuel Ávalos

| Componente | Detalle |
|---|---|
| **Contexto** | La vista `#/sim` mostraba la foto del CAEX, las 8 cámaras y la inspección fotográfica. El modelo de datos tenía una sola temperatura (termografía del flanco, `mediciones.temperatura_flanco_c`) con un único umbral crítico de 95 °C, y no existían presión, TPMS, carga ni TKPH en el prototipo. |
| **Intención** | «Necesito expandir esta pantalla integrando la telemetría completa de cada neumático y las variables del sistema según el modelo de datos existente, antes de publicar, para evaluar si la densidad de información es excesiva o si requiere filtros/colapsos.» Con secciones de TPMS por posición (presión en PSI/bar y estado del sensor) y de temperatura con niveles Normal/Advertencia/Crítico. |
| **Restricciones** | Trabajar en la rama `dev` sin abrir PR; conservar la identidad visual oscura/industrial; usar las variables y umbrales del proyecto; agregar controles para comparar la vista resumida con la detallada. |
| **Verificación** | Se revisó primero el código: la vibración no existe en el modelo y no se inventó. Se mantuvo el umbral crítico de 95 °C y se agregó un nivel de advertencia (85 °C) declarado como supuesto, igual que la presión nominal de 102 psi. Los valores TPMS, carga y TKPH son **simulados y deterministas** (no cambian entre renders). **Error de la IA corregido en la prueba:** el contador de densidad marcaba 123 datos en la vista Operador porque contaba valores dentro de secciones plegadas; corregido, muestra 23 (Operador) frente a 125 (Ingeniería). **Prueba funcional:** el sensor recorre Operativo → Sin señal → Falla sin alterar la presión de los otros neumáticos; sin consola de errores en ambas vistas. |

---

## Qué debe saber explicar cada integrante

La pauta aplica **tolerancia cero**: si un integrante no puede explicar un fragmento del repositorio, el ítem se reprueba. Antes de la entrega, cada persona revisa estos puntos:

| Archivo | Qué explicar |
|---|---|
| `src/index.html` | Cómo `getTires()` arma los 402 neumáticos desde `state`; el enrutador `route()` por `#/`; la función `zona()` con sus umbrales de 200 h y 500 h. |
| `src/db.js` | `cargar()` lee `vista_tablero_turno`, `ventanas_taller` y `ordenes_trabajo` y los convierte al formato de `state`; cada escritura inserta o actualiza una tabla y agrega una fila en `historial_ordenes`. |
| `src/index.html`, función `enfocarAlFinal()` | Por qué los buscadores redibujan la pantalla en cada tecla y por qué hay que devolver el cursor al final (hallazgo IA-09). |
| `src/index.html`, función `persistir()` | Patrón optimista: primero cambia la pantalla, luego escribe en Supabase y recarga. Si falla, muestra el error y vuelve al dato de la base. |
| `docs/schema.sql` | Para qué sirve cada trigger de cupos; por qué las funciones son `SECURITY DEFINER`; qué permite cada política RLS y por qué no existe `DELETE`. |
| `scripts/generar_seed.py` | Lee las constantes `INITIAL_*` del prototipo y genera `docs/seed.sql`, para que la base y el modo local tengan los mismos datos. |
| `modelo/generar_datos.py` | Qué efectos verdaderos usa el simulador (constantes `VERDAD_*`) y por qué la temperatura del neumático es consecuencia y no causa. |
| `modelo/entrenar.py` | Por qué se agrupa en ventanas de ~200 h, qué mide SHAP, qué es la censura en el modelo de Cox y cómo se calcula la horas remanentes (`(profundidad − 20) / tasa × 100`). |
| `backend/app/proyeccion.py` | Regresión lineal de la profundidad contra las horas de operación para proyectar el cruce del umbral de 20 mm. |
