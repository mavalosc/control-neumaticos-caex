# Pruebas de rotura · orden de trabajo (PROP-12)

> Evidencia de la Semana 9. Cada intento se registra **dos veces**: **antes** de PROP-12 (sitio publicado sin cambios) y **después** (sitio con PROP-12 y SQL aplicado). En cada momento se anota lo que se ve en **pantalla** y lo que quedó en la **base**.
>
> **Regla:** un resultado solo se escribe si la prueba se **ejecutó**, con fecha y captura. Lo que no se ha probado dice «pendiente». Las pruebas automáticas de `tests/` usan una base simulada: respaldan, pero **no reemplazan**, la prueba en el sitio.
>
> **Órdenes de prueba:** las pruebas 2 y 4 crean órdenes reales. Cada una se anula al terminar con «Otro motivo: PRUEBA DE ROTURA» y se anota su número aquí.

## 1. Los 5 intentos del profesor

| # | Intento | Cómo se hace | Antes · pantalla | Antes · base | Después · pantalla | Después · base |
|---|---|---|---|---|---|---|
| T1 | Campo vacío | Modificar una orden: dejar el motivo vacío o con solo espacios y presionar Guardar | **Pasa** (22-11): el botón queda deshabilitado | **Falla** (22-11, por el esquema): `motivo` acepta texto vacío; no hay regla de largo | pendiente | pendiente |
| T2 | Enviar dos veces | Doble clic rápido en «Confirmar y emitir orden»; repetir en «Guardar Modificaciones» y en «Sí, anular» | pendiente | pendiente | pendiente | pendiente |
| T3 | Texto larguísimo | Pegar 5.000 caracteres en el motivo | **Falla** (22-11): lo acepta y Guardar queda habilitado, pero no guarda | pendiente | pendiente | pendiente |
| T4 | Cortar la conexión y enviar | En el navegador: F12 → Red → «Sin conexión»; emitir una orden | pendiente (por el código: aviso de éxito primero, error técnico después) | pendiente | pendiente | pendiente |
| T5 | Abrir un registro que no existe | Escribir en la dirección `#/e/ot-9999` | **Falla** (22-11): vuelve a Órdenes sin explicar | No aplica | pendiente | No aplica |

## 2. Pruebas agregadas por la revisión del equipo

| # | Intento | Cómo se hace | Antes · pantalla | Antes · base | Después · pantalla | Después · base |
|---|---|---|---|---|---|---|
| R1 | Orden anulada abierta por su dirección | Escribir `#/e/ot-0072` (anulada en la sesión 1) | **Falla** (22-11): se abre el formulario de modificar | pendiente | pendiente | pendiente |
| R2 | Contadores | Comparar los contadores de Órdenes con la lista filtrada | **Falla** (22-11): Ejecutadas 55 y Anuladas 10, con 1 y 3 en la lista | No aplica | pendiente | No aplica |
| R3 | Pantalla de carga | Recargar la app con la red en «3G lenta» | **Falla** (22-11): pantalla en blanco | No aplica | pendiente | No aplica |
| R4 | Sin conexión al abrir | Activar «Sin conexión» y recargar | pendiente (por el código: pasa a «modo local» y todo dice éxito) | pendiente | pendiente | pendiente |
| R5 | Agendar un neumático que no existe | Escribir `#/a/NO-EXISTE` | pendiente | No aplica | pendiente | No aplica |
| R6 | Historial sin ERP | Abrir una orden nueva y leer su historial | **Falla** (22-11): «sincronizada con ERP» | **Falla**: el texto queda en la base | pendiente | pendiente |
| R7 | Dos pestañas | Abrir la misma orden en dos pestañas; anular en una y modificar en la otra | pendiente | pendiente | pendiente | pendiente |
| R8 | Llamada directa a la API | Insertar un evento con motivo vacío usando la clave pública, sin pasar por la pantalla | No aplica | pendiente | No aplica | pendiente |

## 3. Pruebas automáticas (base simulada)

| Archivo | Qué cubre | Resultado (23-11-2026) |
|---|---|---|
| `tests/reglas.test.js` | Los números del SQL coinciden con `src/reglas.js`; mensajes de T1 y T3 | 9 de 9 |
| `tests/pantalla-prop12.test.js` | Carga, error al abrir y Reintentar; contadores y estado vacío; T1 a T5; R1, R2, R4, R5 y R7; anular con «PRUEBA DE ROTURA»; marcar como ejecutada; corrección de daño sin red | 35 de 35 |
| Pruebas de PROP-11 (modo local) | Sin regresiones en Tablero, Camiones, Ficha, Agendar, Modificar y Datos | 25 de 25 |

## 4. Órdenes de prueba creadas en la base real

| Orden | Fecha | Prueba | Anulada con «PRUEBA DE ROTURA» |
|---|---|---|---|
| — | — | — | — |
