# Avances

## v0.9 (25-10-2026) · PROP-06
- [x] Supabase: `ciclos_operacion`, `modelo_versiones` y `predicciones_modelo` (origen = simulado, solo lectura para la app)
- [x] Generador de terreno diario y entrenamiento Gradient Boosting + SHAP (`modelo/terreno/`), ejecutados por GitHub Actions
- [x] Tablero con horas de la fórmula y del modelo; Ficha con predicción y 3 causas SHAP


## v0.8 (25-10-2026) · PROP-05
- [x] `docs/respaldo-bibliografico.md`: matriz y citas de Nicolás Echeverría, con el criterio experto de Héctor Medina
- [x] Corrección de 5 afirmaciones sin respaldo (umbral de 20 mm, temperaturas, zonas, ±200 h, 30 % de fallas)


## v0.7 (24-10-2026) · Propuestas PROP-01 a PROP-03 (aprobadas)
- [x] Metodología de propuestas y registro en `docs/propuestas.md`
- [x] PROP-01: `docs/experiencia-usuario.md` (mapa de experiencia, flujo de pantallas y especificaciones)
- [x] PROP-02: «neumático» en lugar de «goma» (+ script de migración para Supabase)
- [x] PROP-03: manual de uso en `#/ayuda`, botón **?** de ayuda contextual y PDF descargable


## v0.6 (19-10-2026) · Datos y modelos visibles en el prototipo
- [x] `#/datos`: explorador de las 8 tablas de Supabase (completas), con búsqueda, orden y descarga CSV
- [x] `#/modelos`: cómo funcionan la proyección actual y los modelos de aprendizaje, con resultados de la PoC
- [x] `modelo/entrenar.py` publica gráficos y métricas en `src/assets/modelo/`


## v0.5 (18-10-2026) · Telemetría en el simulador del pórtico (en evaluación)
- [x] Vista `#/sim`: chasis 6x4 con semáforo por posición y alertas de la pasada
- [x] Secciones TPMS (PSI/bar, estado del sensor), temperatura (flanco e interna, 3 niveles) y carga/velocidad/TKPH
- [x] Vista Operador / Ingeniería, secciones plegables y contador de datos en pantalla para evaluar densidad
- [x] Vista Operador como predeterminada: el simulador siempre parte resumido al entrar (decisión del 19-10-2026)
- [ ] Llevar TPMS, carga y TKPH al modelo de datos de Supabase si se aprueba la vista


## v0.4 (18-10-2026) · PoC del modelo de desgaste
- [x] `docs/modelo.md`: variables, fuentes de datos, TKPH, desgaste vs daño, método y plan de validación
- [x] `modelo/`: datos sintéticos con efectos conocidos, regresión, Gradient Boosting + SHAP y supervivencia (Cox)
- [x] Validación en camiones no vistos: error de horas remanentes a 30 mm de 65 h (método actual: 222 h)
- [x] Registro IA-10 en la bitácora


## v0.3.1 (17-10-2026)
- [x] Buscadores de Tablero, Camiones y Órdenes: el texto ya no se escribe al revés (cursor al final tras redibujar)
- [x] Camiones con búsqueda propia, independiente del Tablero
- [x] Hallazgo registrado en `docs/bitacora-ia.md` (IA-09)


## v0.3 (14-10-2026) · Entregas 3 y 4 según rúbrica
- [x] `docs/bitacora-ia.md`: 7 interacciones con IA (Contexto, Intención, Restricciones, Verificación)
- [x] `docs/datos.md`: diccionario de las 7 tablas, diagrama ER, reglas Tidy Data y matriz RLS
- [x] `docs/historias.md`: Gherkin válido (`Característica`/`Escenario`), flujo principal HU-07 ★, un escenario feliz y uno de excepción por historia, alineado con Notion
- [x] `docs/wireframes/W1-W5.png`: wireframes anotados [1] a [4] generados desde el prototipo real
- [x] Prototipo: motivo obligatorio al modificar una OT (HU-08), etiqueta «por confirmar» (HU-04), mensaje sin resultados en Camiones (HU-03)
- [x] `schema.sql`: `creado_en` en mediciones, daños e historial
- [x] Material reemplazado movido a `docs/historico/`; README con escala de madurez, beneficiarios y guía local


## v0.2 (14-10-2026)
- [x] Flota ampliada a 67 CAEX (402 neumáticos) con paginación en Tablero y Camiones
- [x] Prototipo conectado a Supabase (`src/config.js`, `src/db.js`): lectura de flota, ventanas y órdenes; escritura de órdenes, modificaciones, anulaciones, correcciones de daño y pasadas de pórtico
- [x] `docs/schema.sql`: políticas RLS, trigger de cambio de ventana, vista con `security_invoker`
- [x] `docs/seed.sql` generado desde el prototipo (`scripts/generar_seed.py`)
- [x] `frontend/` marcado como versión antigua; `actualizar.bat` trabaja sobre `dev`
- [x] `.env.example` sin credenciales reales


## v0.1
- [x] Wireframe de 4 pantallas definido
- [x] Prototipo frontend navegable con datos de ejemplo (`frontend/index.html`)
- [x] Backend base con datos de ejemplo: proyección lineal, semáforo, ventanas, creación de órdenes
- [x] Pruebas unitarias de proyección y semáforo

- [x] Borrador de historias de usuario, criterios de aceptación y wireframes anotados (`docs/`)

- [x] Prototipo actualizado: niveles de daño 0 a 3, alerta crítica, foto de ejemplo con daños marcados y corrección de clasificación

- [x] Historias de usuario del front end (HU-F01 a HU-F08) con las capturas de Tablero, Camiones y Órdenes

- [x] Idea de diseño y prompt para la maqueta preliminar y el wireframe anotado en Figma

- [x] Prototipo con las pantallas Tablero, Camiones (seis posiciones por CAEX), Ficha, Agendar y Órdenes de trabajo, con los datos de las capturas

- [x] Modificar y anular órdenes programadas (motivo obligatorio, historial, cupo liberado) en prototipo, historias HU-F09 y HU-F10 y API

## Pendiente
- [ ] Validar recorrido, puntos de dolor y niveles de daño con un planificador
- [ ] Conectar el frontend a la API (reemplazar los datos de ejemplo)
- [ ] Base de datos real (PostgreSQL) y migraciones
- [ ] Captura de imágenes y modelo de visión (detección, OCR del serial, profundidad, daños)
- [ ] Validación de las mediciones contra medición manual en terreno
- [ ] Integración con el ERP y notificación al taller
- [ ] Autenticación y roles (planificador, taller)
- [ ] Despliegue con Docker Compose
