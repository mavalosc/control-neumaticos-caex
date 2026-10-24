# Registro de propuestas

**Metodología acordada (24-10-2026):**
1. **Conversación:** se plantea la necesidad; se puede analizar el proyecto, sin modificar nada.
2. **Propuesta:** código **PROP-NN · nombre corto**, con qué, por qué, archivos o plataformas afectados, riesgos y cómo se verifica.
3. **Revisión:** se ajusta las veces necesarias (v1, v2…).
4. **Aprobación explícita** del equipo («apruebo PROP-NN»).
5. **Implementación** en la rama `dev`; cada commit lleva el código de la propuesta.
6. **Revisión del resultado** con evidencias, antes de publicar.
7. **Publicación:** Pull Request de `dev` a `main`, aprobación de Héctor y despliegue en Vercel.

## Estado

| Código | Nombre | Estado | Versión | Propuesta | Implementación |
|---|---|---|---|---|---|
| PROP-01 | Experiencia de usuario y especificaciones | Implementada en `dev` · **pendiente de revisión, no publicar** | v1 | 24-10-2026 | 24-10-2026 |
| PROP-02 | Terminología: «neumático» en lugar de «goma» | Implementada en `dev` · pendiente de revisión y de ejecutar el SQL en Supabase | v1 | 24-10-2026 | 24-10-2026 |
| PROP-03 | Manual de uso dentro de la app | Implementada en `dev` · pendiente de revisión | v1 | 24-10-2026 | 24-10-2026 |

---

## PROP-01 · Experiencia de usuario y especificaciones
- **Qué:** documento con los usuarios, el mapa de experiencia del planificador, el flujo de pantallas, el recorrido de la pasada a la decisión, puntos de dolor y especificaciones con identificador y estado.
- **Por qué:** reunir en un solo lugar quién usa la herramienta, cómo la recorre y qué debe cumplir; base para la prueba con el planificador (Semana 7) y el MVP.
- **Archivos:** `docs/experiencia-usuario.md` (nuevo), `README.md` (enlace).
- **Riesgos:** los puntajes del mapa de experiencia son una hipótesis del equipo; los umbrales de 85 °C y 102 psi son supuestos.
- **Verificación:** los 3 diagramas Mermaid se renderizan sin errores; cada especificación indica su estado real.
- **Historial:**
  - 24-10-2026 · v1 creada antes de acordar la metodología; tratada como primera propuesta. Aprobada para implementar con la indicación de **no publicar aún**.
  - 24-10-2026 · se agregaron ESP-F-16 y ESP-F-17 (manual y ayuda contextual, PROP-03) y el perfil «Profesor y evaluadores».

## PROP-02 · Terminología: «neumático» en lugar de «goma»
- **Qué:** reemplazar «goma» por «neumático» en la interfaz, los documentos, los datos de demostración y las 2 órdenes guardadas en Supabase.
- **Por qué:** el equipo usa solo el término «neumático».
- **Archivos:** `src/index.html`, `docs/seed.sql`, `docs/historias.md`, `docs/modelo.md`, `docs/migraciones/2026-10-24_PROP-02_terminologia.sql` (nuevo).
- **Fuera de alcance:** `frontend/` y `docs/historico/` (versiones antiguas que se conservan tal cual); tarjetas de Notion (sin acceso de edición: corrección manual).
- **Riesgos:** bajo. Las notas de ot-0068 y ot-0052 en Supabase se corrigen con el script de migración, que ejecuta el equipo.
- **Verificación:** 0 apariciones de «goma» en `src/` y `docs/` (fuera de `historico/`); el script termina con una consulta que debe devolver 0.
- **Historial:** 24-10-2026 · v1 propuesta, aprobada e implementada en `dev`.

## PROP-03 · Manual de uso dentro de la app
- **Qué:** manual escrito una sola vez (`src/manual.md`) que se lee en la app (`#/ayuda`), en GitHub y en PDF; botón **?** de ayuda contextual en cada pantalla.
- **Para:** planificador, operador del pórtico, profesor y evaluadores.
- **Decisiones:** alternativa A (un solo archivo Markdown mostrado con la librería `marked`); ayuda contextual incluida; PDF descargable desde la página de ayuda.
- **Archivos:** `src/manual.md` (nuevo), `src/index.html` (botón Ayuda, ruta `#/ayuda`, botón **?**), `src/assets/manual/` (9 capturas y PDF), `scripts/manual/` (generador de capturas y PDF).
- **Riesgos:** que el manual quede desactualizado cuando cambie la interfaz. Mitigación: `bash scripts/manual/generar.sh` regenera capturas y PDF; toda propuesta que cambie la interfaz debe actualizar el manual. Dependencia de la librería `marked` por CDN (versión fija 12.0.2).
- **Verificación:** el botón **?** abre la sección correcta desde Tablero, Camiones, Órdenes, Simulador y Datos; el índice muestra 16 secciones; las 9 capturas y el PDF cargan; sin errores de consola.
- **Historial:** 24-10-2026 · v1 propuesta, aprobada e implementada en `dev`.
