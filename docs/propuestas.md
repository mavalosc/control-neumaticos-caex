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
| PROP-01 | Experiencia de usuario y especificaciones | **Publicada** (PR #6, 24-10-2026) | v1 | 24-10-2026 | 24-10-2026 |
| PROP-02 | Terminología: «neumático» en lugar de «goma» | **Publicada** (PR #6, 24-10-2026) · SQL ejecutado en Supabase | v1 | 24-10-2026 | 24-10-2026 |
| PROP-03 | Manual de uso dentro de la app | **Publicada** (PR #6, 24-10-2026) | v1 | 24-10-2026 | 24-10-2026 |
| PROP-04 | (Reservada) Revisión del PR #5 de Héctor: wireframes en el README | Sin conversar | — | — | — |
| PROP-05 | Respaldo bibliográfico y corrección de afirmaciones | **Publicada** (PR #7, 26-10-2026) | v1 | 24-10-2026 | 25-10-2026 |
| PROP-06 | Datos de terreno simulados, Gradient Boosting y SHAP en Supabase | **Publicada** (PR #8, 26-10-2026) | v2 | 24-10-2026 | 25-10-2026 |
| PROP-07 | Datos reales de TPMS y velocidad (anonimizados) y modelo de riesgo | Aprobada para publicar · en revisión (PR #9) | v1 | 28-10-2026 | 29-10-2026 a 07-11-2026 |

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
  - 24-10-2026 · revisión aprobada; publicada en `main` con el PR #6.

## PROP-02 · Terminología: «neumático» en lugar de «goma»
- **Qué:** reemplazar «goma» por «neumático» en la interfaz, los documentos, los datos de demostración y las 2 órdenes guardadas en Supabase.
- **Por qué:** el equipo usa solo el término «neumático».
- **Archivos:** `src/index.html`, `docs/seed.sql`, `docs/historias.md`, `docs/modelo.md`, `docs/migraciones/2026-10-24_PROP-02_terminologia.sql` (nuevo).
- **Fuera de alcance:** `frontend/` y `docs/historico/` (versiones antiguas que se conservan tal cual); tarjetas de Notion (sin acceso de edición: corrección manual).
- **Riesgos:** bajo. Las notas de ot-0068 y ot-0052 en Supabase se corrigen con el script de migración, que ejecuta el equipo.
- **Verificación:** 0 apariciones de «goma» en `src/` y `docs/` (fuera de `historico/`); el script termina con una consulta que debe devolver 0.
- **Historial:** 24-10-2026 · v1 propuesta, aprobada e implementada en `dev`; publicada con el PR #6; script ejecutado en Supabase (resultado 0).

## PROP-03 · Manual de uso dentro de la app
- **Qué:** manual escrito una sola vez (`src/manual.md`) que se lee en la app (`#/ayuda`), en GitHub y en PDF; botón **?** de ayuda contextual en cada pantalla.
- **Para:** planificador, operador del pórtico, profesor y evaluadores.
- **Decisiones:** alternativa A (un solo archivo Markdown mostrado con la librería `marked`); ayuda contextual incluida; PDF descargable desde la página de ayuda.
- **Archivos:** `src/manual.md` (nuevo), `src/index.html` (botón Ayuda, ruta `#/ayuda`, botón **?**), `src/assets/manual/` (9 capturas y PDF), `scripts/manual/` (generador de capturas y PDF).
- **Riesgos:** que el manual quede desactualizado cuando cambie la interfaz. Mitigación: `bash scripts/manual/generar.sh` regenera capturas y PDF; toda propuesta que cambie la interfaz debe actualizar el manual. Dependencia de la librería `marked` por CDN (versión fija 12.0.2).
- **Verificación:** el botón **?** abre la sección correcta desde Tablero, Camiones, Órdenes, Simulador y Datos; el índice muestra 16 secciones; las 9 capturas y el PDF cargan; sin errores de consola.
- **Historial:** 24-10-2026 · v1 propuesta, aprobada e implementada en `dev`; publicada en `main` con el PR #6.


## PROP-05 · Respaldo bibliográfico y corrección de afirmaciones
- **Qué:** llevar al repositorio la matriz de respaldo bibliográfico y las citas APA de Nicolás Echeverría (`docs/respaldo-bibliografico.md`), corregir el DOI de Roberts et al. (2017), enlazarla desde la página Modelos y `docs/modelo.md`, y corregir 5 afirmaciones sin respaldo.
- **Por qué:** la revisión de Nicolás mostró que el prototipo presentaba como hechos valores que son supuestos o requisitos propuestos.
- **Correcciones:** (1) «umbral de retiro seguro de 20 mm» → umbral de retiro de 20 mm por **criterio experto de taller** (Héctor Medina), configurable; (2) 85/95 °C → umbrales de alerta no validados; (3) zonas 200/500 h y meta de 200 h → requisitos propuestos; (4) «±200 h» → se aclara que es error de estimación, no anticipación; (5) «~30 % de fallas» → dato de una operación (Lindeque, 2016).
- **Archivos:** `docs/respaldo-bibliografico.md` (nuevo), `docs/modelo.md`, `docs/experiencia-usuario.md`, `docs/ARQUITECTURA.md`, `README.md`, `src/manual.md`, `src/index.html` (Ficha y Modelos), `modelo/entrenar.py` y `modelo/resultados/REPORTE.md`, capturas y PDF del manual.
- **Fuera de alcance:** la tarjeta de Notion con el DOI incorrecto (sin acceso de edición; corrección manual del equipo).
- **Verificación:** 0 apariciones de «retiro seguro» fuera del documento de respaldo; los resultados del modelo no cambian (semilla fija).
- **Historial:** 24-10-2026 · propuesta. 25-10-2026 · aprobada («ejecuta y publica PROP-05») e implementada en `dev`.

## PROP-06 · Datos de terreno simulados, Gradient Boosting y SHAP en Supabase
- **Qué:** (1) tres tablas nuevas en Supabase con la marca `origen = 'simulado'`, solo lectura para la app; (2) generador de terreno que simula ciclos de operación de los 402 neumáticos montados; (3) entrenamiento de Gradient Boosting y SHAP que lee y escribe en Supabase, con marca «Simulado»; (4) ejecución automática diaria con GitHub Actions, con la clave `service_role` solo en los Secrets de GitHub; (5) la Ficha muestra la predicción del modelo y sus 3 causas SHAP como «Modelo entrenado con datos de terreno simulados».
- **Decisiones del equipo (25-10-2026):** el generador **no** escribe en `mediciones`; el Tablero muestra **ambas** horas remanentes en columnas separadas (fórmula y modelo); ejecución **diaria**.
- **Riesgo declarado:** el modelo aprende las reglas del simulador; demuestra que la cadena completa funciona, no el comportamiento real de los neumáticos.
- **Archivos:** `docs/migraciones/2026-10-25_PROP-06_terreno_simulado.sql` y `docs/schema.sql`; `modelo/terreno/` (generador, entrenamiento y cliente de Supabase); `.github/workflows/terreno-diario.yml`; `src/db.js` y `src/index.html` (Tablero, Ficha, Datos, Modelos); `docs/datos.md`, `docs/modelo.md`, `src/manual.md`, `docs/experiencia-usuario.md`.
- **Verificación (25-10-2026):** tablas creadas por el equipo con RLS activado; primera carga de 60.300 ciclos y 402 predicciones (versión `gb-terreno-20261025`, error de tasa 0,138 mm/100 h en camiones no vistos, contra 0,654 del promedio de flota); segunda ejecución sin duplicados (0 ciclos nuevos); la clave pública de la app no puede escribir (error 42501); Tablero y Ficha muestran las predicciones sin errores de consola.
- **Historial:** 24-10-2026 · v1 propuesta. 25-10-2026 · v2 con las decisiones del equipo; aprobada para implementar y publicar; implementada y verificada con datos en Supabase. 26-10-2026 · publicada con el PR #8, aprobado por Héctor.

## PROP-07 · Datos reales de TPMS y velocidad (anonimizados) y modelo de riesgo
- **Qué:** (1) dos tablas con datos **reales** de una faena, `alertas_tpms` (30.382 alertas de presión y temperatura, 2024-2026) y `eventos_velocidad` (11.352 excesos, julio a octubre de 2026), con `origen = 'real'`; (2) un script de carga que descarta duplicados y equipos de prueba y **anonimiza** equipos y sensores; (3) un modelo Gradient Boosting + SHAP entrenado con datos reales que estima el riesgo de una alerta crítica del TPMS en los próximos 7 días por equipo y posición (`riesgo_versiones`, `riesgo_posiciones`); (4) la sección «Datos reales» en la página Modelos y 4 pestañas nuevas en Datos; (5) calibración de la presión nominal del simulador TPMS y del generador de terreno: de 102 a 110 psi.
- **Por qué:** el equipo recibió datos de terreno (Héctor Medina). Al revisarlos se vio que son **alertas** (el TPMS solo registra excesos) y no traen profundidad de banda, horas ni motivos de baja: no sirven para entrenar el modelo de horas remanentes, pero sí para calibrar umbrales y para un modelo de riesgo con datos reales.
- **Decisión del equipo (28-10-2026):** opción (b): mostrar los datos **sin nombres de faena ni de empresas**, porque el repositorio y la app son públicos y algunos documentos fuente son de uso interno. Los archivos originales (Excel, cartas técnicas, estándares y presentaciones) **no entran al repositorio**; la tabla de equivalencias queda solo en el computador del equipo (`modelo/datos/reales/`, ignorada por git).
- **Hallazgos de calibración:** presión nominal en frío de 110 psi con alertas a ±5, ±7 y ±10 %; temperatura interna del TPMS con alertas a 75, 80 y 85 °C en camiones; límites de velocidad de 50 km/h en ruta y de 20 o 15 km/h en curvas. Un fabricante de neumáticos OTR define el desgaste total con una banda remanente de 15 mm o menos y recomienda rotar del eje delantero al trasero con 1/3 de la vida; el umbral del prototipo sigue en 20 mm (criterio experto).
- **Notion (edición manual del equipo, agregada a pedido el 29-10-2026):** subsección «Datos reales» dentro de «9. Modelo predictivo», tarjetas de PROP-07 en el Kanban y nota en [META-01] del Roadmap. Sin nombres de faena ni de empresas, porque el sitio de Notion también es público.
- **Fuera de alcance:** cambiar los umbrales de temperatura del flanco (85/95 °C; la termografía del pórtico no es la misma medición que el sensor interno del TPMS); modelar la rotación de neumáticos en el simulador; reentrenar el modelo de horas remanentes con datos reales (faltan profundidad, horas y motivos de baja).
- **Archivos:** `docs/migraciones/2026-10-29_PROP-07_datos_reales.sql` y `docs/schema.sql`; `modelo/real/` (carga y modelo de riesgo); `modelo/requirements.txt` (`openpyxl`); `modelo/terreno/generar_terreno.py` (110 psi); `src/db.js` y `src/index.html` (Modelos, Datos, Simulador); `docs/datos.md`, `docs/modelo.md`, `docs/respaldo-bibliografico.md`, `docs/experiencia-usuario.md`, `src/manual.md`.
- **Riesgos:** (1) una alerta crítica no es una falla del neumático; (2) si un sensor deja de transmitir, la falta de alertas se lee como «sin riesgo»; (3) los cargadores tienen otros umbrales y pocos datos; (4) el cambio de 102 a 110 psi crea un salto en la columna `presion_psi` de los ciclos simulados (el modelo usa la desviación en %, que no cambia).
- **Verificación:** 0 nombres de faena, empresa o códigos originales de equipo en Supabase, en el repositorio y en la app; modelo evaluado con corte por fecha (entrena antes del 01-04-2026 y prueba después) contra una regla simple.
- **Historial:** 28-10-2026 · v1 propuesta, con la opción (b) de anonimización elegida por el equipo. 29-10-2026 · aprobada («avanza con PROP-07») e implementada en la rama `feature/prop-07`. 07-11-2026 · tablas creadas por el equipo con RLS; carga de 30.382 alertas y 11.352 excesos; modelo `gb-riesgo-20261107` publicado (AUC 0,82 vs 0,75; 4 de 80 posiciones a vigilar al 27-10-2026); la clave pública no puede escribir (42501).

---

## Notas de publicación
- **PR #6 (24-10-2026):** fusionado por el propietario del repositorio usando el **bypass** de la protección de `main`, sin la aprobación de un segundo revisor. Queda pendiente que Héctor (QA) deje su revisión en el PR para conservar la evidencia de revisión entre pares.
