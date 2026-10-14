# Avances

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
