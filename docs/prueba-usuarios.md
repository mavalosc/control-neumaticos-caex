# Diseño de la prueba con usuarios
## Herramienta predictiva de desgaste de neumáticos CAEX · Equipo 3 · Semanas 7-8 (PROP-09)

> Lo que separa la prueba de concepto (PoC) del producto mínimo viable (MVP) es esta validación: un **experimento diseñado para encontrar dónde falla el diseño**, no una demostración. Si el resultado contradice al equipo, la prueba funcionó.
>
> Pauta de la sesión: [`pauta-validacion.md`](pauta-validacion.md) · Resguardos éticos: [`etica.md`](etica.md) · Recorrido que se valida: [`experiencia-usuario.md`](experiencia-usuario.md)
>
> Versión 2 · 14-11-2026 · Sesión 1 realizada el 13-11-2026, con resultados en la sección 6 (PROP-10) · Versión 1 · 12-11-2026 (PROP-09)

---

## 1. Qué se valida y qué no

| Pregunta | ¿Entra en esta prueba? | Cómo se responde |
|---|---|---|
| **¿Funciona?** (integración, errores, permisos) | No | Escenarios técnicos y casos límite (Semana 11). Ya hay evidencia parcial: el flujo guarda en Supabase y la base controla los cupos |
| **¿Se entiende y se logra?** | **Sí, es el foco** | Una persona con el perfil correcto intenta completar las tareas **sin ayuda** mientras piensa en voz alta |
| **¿Le importa a alguien?** (valor) | Parcial | Preguntas sobre hechos pasados (*The Mom Test*) antes de las tareas: cómo resuelve hoy el retiro de un neumático |

**Fuera de alcance:** el hardware del pórtico (las mediciones son sintéticas), la precisión del modelo y la integración con el ERP.

---

## 2. Objetivo e hipótesis que pueden fallar

**Objetivo:** saber si un planificador puede **priorizar el turno y dejar programado el cambio de un neumático** sin que nadie le explique la herramienta, y si entiende de dónde salen las horas remanentes.

Los umbrales se fijaron el 12-11-2026, **antes de ver resultados**. Si no se cumplen, el diseño cambia.

| ID | Hipótesis | Métrica (ISO 9241-11) | Umbral de éxito | Tarea |
|---|---|---|---|---|
| H1 | El planificador emite la orden para el neumático más urgente sin ayuda | **Eficacia:** tarea completada sin intervención del facilitador | ≥ 4 de 5 participantes (ronda completa) | T3 ★ |
| H2 | Lo hace con poco esfuerzo | **Eficiencia:** tiempo y pedidos de ayuda | Mediana ≤ 4 min y ≤ 1 pedido de ayuda | T3 |
| H3 | Identifica cuáles neumáticos atender primero en el turno | Eficacia | Nombra los 3 de menos horas en ≤ 3 min | T1 |
| H4 | Entiende de dónde salen las horas y no decide solo con la columna del modelo simulado | Comprensión (respuesta verbal) | ≥ 3 de 5 distinguen la fórmula del modelo; **ninguno** justifica la orden solo con «Modelo · sim» | T6 |
| H5 | La herramienta le resulta usable | **Satisfacción:** escala SUS (0-100) | Promedio ≥ 68 (referencia de Sauro, 2011) | Cierre |

**Regla para una sola sesión:** con un participante no se calculan tasas. Cada hipótesis se marca como *se cumple / no se cumple* para esa persona y se reporta como **indicio**, no como validación. La ronda completa (5 personas del perfil principal) confirma o descarta.

---

## 3. Perfiles y reclutamiento

| Perfil | Rol en la prueba | Qué se le pide | Cuántos |
|---|---|---|---|
| **Planificador de mantención de neumáticos** | Usuario principal | Ejecutar las tareas T1 a T6 | 5 en la ronda completa; **1 voluntario en la primera sesión** |
| Operador del pórtico | Usuario secundario | Simular una pasada y confirmar la captura | Ronda posterior |
| Jefatura de mantención o de neumáticos | **Stakeholder** | No ejecuta tareas: se le pregunta por condiciones de adopción (sección 6 de la pauta) | 1, si es posible |

- **Reclutamiento:** Nicolás Echeverría consigue al voluntario. *Sesión 1: el voluntario lo consiguió Francisco, porque Nicolás no consiguió uno; es un conocido y se declara como sesgo.* **Desde la sesión 2 (decisión del equipo, 14-11-2026): un planificador de neumáticos o de flota sin vínculo con el equipo.** Se prefiere a alguien que planifique o ejecute mantención de neumáticos o de equipos mineros; Héctor Medina puede sugerir contactos del área de reparación de neumáticos.
- **Exclusiones:** integrantes del equipo y personas que ya vieron el prototipo funcionando. Si el voluntario no tiene el perfil de planificador, la sesión se hace igual y el resultado se informa como **perfil aproximado**.
- **Quién queda fuera** (ver `etica.md`): si se recluta solo a personas con práctica digital, la prueba valida al usuario implícito del equipo. Se pregunta al inicio por su uso habitual de computador o tablet.

---

## 4. Plan de levantamiento

| Elemento | Decisión |
|---|---|
| Modalidad | **Google Meet**, con el voluntario compartiendo su pantalla. La herramienta se abre en su navegador: https://control-neumaticos-caex-frontend.vercel.app |
| Roles | Nicolás cumple los tres: **facilita** en la sesión, **registra** después a partir de la grabación (así no interrumpe por tomar notas) y **resguarda la evidencia**. Si otro integrante se une en silencio con cámara y micrófono apagados, registra en vivo |
| Grabación | **Obligatoria**, con la función Grabar de Meet: pantalla y voz, **cámara apagada**. Se inicia **después** de explicar el consentimiento y la primera frase grabada es la aceptación del voluntario |
| Dónde queda | La grabación se guarda en el Drive del organizador. Nicolás la mueve a la carpeta del proyecto en Drive, con acceso restringido al equipo y al profesor, y comparte el enlace con el equipo. En el README se publica el enlace: quien no tenga permiso no puede abrirlo |
| Conservación | Hasta el 31-12-2026; luego se borra |
| Registro | Planilla de observaciones de la sección 5 de la pauta: **una fila por observación**, separando lo observado de la interpretación |
| Datos que deja la prueba | Las órdenes que cree el voluntario quedan en Supabase con su email (o un código, si lo prefiere). Al terminar, Nicolás anota los códigos de orden y el equipo las **anula con el motivo «prueba de usuarios P1»** |
| Ensayo | Antes de la sesión real, Nicolás ensaya la pauta con otro integrante para descubrir tareas ambiguas |

---

## 5. Cómo se clasifican y deciden los hallazgos

Severidad según Nielsen (1994), aplicada a cada observación:

| Severidad | Criterio | Qué se hace |
|---|---|---|
| **Bloquea** | No completa la tarea sin ayuda | Se corrige antes de seguir (Semana 9) |
| **Entorpece** | La completa, pero duda, se desvía, se equivoca o pide ayuda | Se ordena por cuántas personas lo vivieron |
| **Estético** | La completa sin problema y algo le incomoda | Se anota y espera |

Cada hallazgo que bloquea termina en una de tres decisiones: **cambio comprometido** (con responsable y PROP), **riesgo aceptado** (con justificación en `etica.md`) o **pregunta para la ronda siguiente**. Un hallazgo sin decisión es una anécdota.

---

## 6. Resultados

### Sesión 1 · P1 · 13-11-2026

Tablas de la pauta completadas (SUS, planilla de observaciones, resumen por tarea y respuestas): [`sesiones/sesion-1-P1.md`](sesiones/sesion-1-P1.md).

| Dato | Valor |
|---|---|
| Fecha y duración | 13-11-2026 · grabación de 22:55 min; tareas entre 06:24 y 16:33 |
| Perfil del participante | Mantenedor de neumáticos, 8 años de experiencia en neumáticos OTR, gran minería. En terreno usa un celular tipo tablet para controlar presiones. **Perfil aproximado:** ejecuta la mantención, no la planifica |
| Reclutamiento | Conocido de Francisco, integrante del equipo (Nicolás no consiguió voluntario). Se declara **sesgo de amabilidad**: un conocido tiende a evaluar mejor |
| Enlace a la grabación (Drive restringido) | Pendiente: carpeta de Drive del proyecto |
| Consentimiento grabado | Sí (04:52) · email usado en la app: `p1@prueba.cl` |
| Cómo se analizó | La grabación completa se subió a **Gemini**, que la procesó con instrucciones de anonimizar y separar lo observado de lo interpretado (dos entregas: la primera solo con audio y la segunda con pantalla). Los minutos se contrastaron con los registros de Supabase: la hora de la orden, de su modificación y de las correcciones de daño coincide con el video con 10 a 15 s de diferencia. La IA calculó mal el SUS (60); el valor correcto es 70 |

**Datos de partida inconsistentes (falla del diseño de la prueba, no del participante)**

- **T3:** el neumático P3 del CAEX-102 tenía 20 h remanentes. La ventana de 36 h no tenía cupos y las otras estaban a 56 h y 84 h: **ninguna permitía cambiarlo antes del límite**.
- **T4:** la consigna dice «el sistema dice crítico», pero ese neumático estaba en **Moderado desde el 17-10-2026** por pruebas del equipo (5 correcciones). P1 lo bajó a Leve, coherente con lo que veía.

| Hipótesis | Resultado P1 (indicio) | Evidencia (minuto) |
|---|---|---|
| H1 · emite la orden sin ayuda | **Se cumple la emisión; el plazo no era evaluable.** Emitió sin ayuda, pero la ventana llegaba 36 h tarde y pasó por alto la advertencia | 10:59 a 11:36 |
| H2 · tiempo de T3 y pedidos de ayuda | **Se cumple:** 37 s y 0 pedidos de ayuda | 10:59 a 11:36 |
| H3 · identifica los 3 más urgentes | **Se cumple, con sesgo:** a los 20 s nombró 102, 159 y 112, los tres de menos horas (20, 63 y 88 h). El facilitador preguntó «¿esa sería tu respuesta? o querés mirar otro» y P1 cambió a 122, 102 y 162, priorizando por corte profundo | 06:44 · 06:58 · 08:23 |
| H4 · distingue fórmula y modelo | **No se cumple.** No distinguió la fórmula del modelo (pasó el cursor por «253 h según el modelo» sin mencionarlo). Se apoyó en las horas calculadas, no en «Modelo · sim». Respondió sobre otro neumático (P6, 344 h) y leyó «Presión de inflado · reduce» como «presión reducida» | 15:02 a 16:33 |
| H5 · puntaje SUS | **Se cumple: 70** (≥ 68). El ítem 3 («fácil de usar» = 1) contradice sus otras respuestas; si fuera 5, el puntaje sería 80. Por confirmar en el minuto 17:27 | 17:08 a 18:34 |

**Resumen por tarea**

| Tarea | Duración | Pedidos de ayuda | Resultado |
|---|---|---|---|
| T1 | 02:41 | 1 («¿puedo aplicar un solo filtro?») | Primera respuesta correcta; la cambió tras la pregunta del facilitador |
| T2 | 01:12 | 2 (canal y alcance) | Avisó a despacho desde la Ficha del CAEX-122 P1, no desde el banner; la app confirmó el aviso |
| T3 ★ | 00:37 | 0 | Emitió la orden; no leyó la advertencia roja de ventana tardía |
| T4 | 01:41 | 1 («¿se guarda solo?») | No evaluable (datos de partida); dejó Leve tras probar Moderado |
| T5 | 01:06 | 0 | Reprogramó a una ventana aún más tardía, sin advertencia de la app; escribió el motivo sobre la justificación técnica |
| T6 | 01:31 | 0 (el facilitador releyó la consigna) | Parcial: dio horas y causas de otro neumático |

**Desviaciones del guion del facilitador**

| Minuto | Desviación | Efecto |
|---|---|---|
| 06:19 | «Dígame cuáles son, **según la plataforma**» | Orienta a mirar solo la tabla |
| **06:58** | «¿Esa sería tu respuesta? O querés mirar otro» | **Grave:** P1 cambió una respuesta correcta |
| 09:33 | Responde «Sí» a «¿mediante la aplicación?» | Revela el canal |
| 09:59 | Aclara el objetivo de T2 ante la pregunta por el 106 | Leve |
| 12:50 | Ante la duda de guardado devuelve la pregunta | Correcto según la pauta |
| 15:19 | Relee la consigna de T6 | Leve; cuenta como ayuda parcial |
| 16:18 | «Se saltaron corte rocas incrustadas» | Comenta lo que P1 no vio |

**Hallazgos priorizados**

| # | Observado (minuto) | Interpretación | Severidad | Decisión | Responsable |
|---|---|---|---|---|---|
| 1 | T3 (11:18): la app muestra en rojo «el neumático cruzará el umbral 36 h antes de esta ventana»; P1 no la lee y confirma la orden | La advertencia no detiene la decisión: se ignora un aviso de seguridad | Entorpece | **Cambio comprometido:** confirmar explícitamente la advertencia antes de emitir y ofrecer «sacar del ciclo» cuando ninguna ventana alcanza | Manuel · propuesta Semana 9 |
| 2 | T5 (13:54 a 14:38): al reprogramar a una ventana más tardía no aparece ninguna advertencia | La pantalla Modificar no valida el plazo | Entorpece | **Cambio comprometido:** misma advertencia al modificar | Manuel · propuesta Semana 9 |
| 3 | T6 (15:40): lee «Presión de inflado · reduce 21,4 %» como «la presión ha estado reducida» | La redacción de las causas SHAP se lee al revés | Entorpece | **Cambio comprometido:** escribir «reduce el desgaste» o «aumenta el desgaste»; volver a preguntar en la sesión 2 | Manuel · propuesta Semana 9 |
| 4 | T5 (14:10): escribe el motivo en «Justificación de la nota» y borra la justificación técnica; luego escribe «Cambio por HH» en el motivo | Dos campos de texto seguidos; la app reemplaza la justificación original | Entorpece | **Cambio comprometido:** conservar la justificación original y dejar un solo campo de motivo | Manuel · propuesta Semana 9 |
| 5 | T4 (12:40 a 13:20): pregunta si se guarda solo; prueba Moderado y Leve y deja 3 registros en 40 s | El guardado automático no se percibe y las pruebas quedan en la auditoría | Entorpece | **Cambio comprometido:** confirmación visible junto al control (o botón «Guardar corrección») | Manuel · propuesta Semana 9 |
| 6 | T4 (12:40): al cambiar el nivel, la descripción pasa de «roca incrustada» a «desgaste irregular» | La corrección reemplaza lo que detectó la visión artificial | Entorpece | **Cambio comprometido:** conservar la descripción detectada y corregir el nivel aparte | Manuel · propuesta Semana 9 |
| 7 | T1 (07:11 y 07:48): pregunta por un filtro combinado y hace clic en el encabezado «Severidad daño», que no ordena | El experto prioriza combinando horas y daño | Entorpece | **Cambio comprometido:** ordenar por severidad y profundidad | Manuel · propuesta Semana 9 |
| 8 | T6 (15:06): abre el P6 del CAEX-102 en vez del P3 | La consigna «ese neumático» es ambigua después de navegar | Entorpece | **Pregunta para la ronda siguiente:** la pauta v2 nombra la posición | Facilitador |
| 9 | T4 (12:12): tras emitir la orden queda en Órdenes y busca la ficha del neumático | Se pierde el contexto de la Ficha | Entorpece | **Pregunta para la ronda siguiente** | Facilitador |
| 10 | T2 (10:12): avisa a despacho desde la Ficha y no desde el banner; pregunta por el alcance | Valida el daño antes de avisar | Estético | Se anota | — |
| 11 | Cierre: le costó encontrar Órdenes en la barra superior | Jerarquía plana de la navegación | Estético | Se anota; se revisa con la accesibilidad de la Semana 9 | — |
| 12 | Cierre (20:42): busca las horas acumuladas del neumático, además de las remanentes | La jefatura pregunta por las horas de uso | Requisito nuevo (no es severidad) | **Nueva especificación:** horas desde el montaje (requiere el horómetro al montar) | Manuel · propuesta Semana 9 |
| 13 | Base de datos: las 3 correcciones de daño quedaron como «planificador», no con el email | PROP-08 solo registra el autor en las órdenes | Vacío del equipo | **Cambio comprometido:** registrar el email también en las correcciones de daño | Manuel · propuesta Semana 9 |

**Conclusión de la sesión 1:** el flujo principal se aprende rápido (T3 en 37 s, SUS 70), pero **las advertencias no detienen una decisión riesgosa** y **la explicación del modelo se malinterpreta**. Ambos indicios apuntan al riesgo R3 de `etica.md` (sesgo de automatización y explicabilidad) y se priorizan en la Semana 9. Los umbrales de las hipótesis no se cambian: siguen siendo los fijados el 12-11-2026.

**Datos que dejó la prueba:** la ot-0072 se anuló el 14-11-2026 con el motivo «prueba de usuarios P1» y el cupo volvió a la ventana. El daño del P3 del CAEX-102 se restauró a «3 · corte profundo en flanco», el valor original de la detección, con un registro marcado «restauración PROP-10».

---

## Referencias

- Brooke, J. (1996). SUS: A quick and dirty usability scale. En *Usability evaluation in industry* (pp. 189-194). Taylor & Francis.
- Fitzpatrick, R. (2013). *The Mom Test*. Founder Centric.
- ISO. (2018). *ISO 9241-11:2018. Ergonomía de la interacción persona-sistema: usabilidad*.
- Nielsen, J. (1994). *Severity ratings for usability problems*. Nielsen Norman Group.
- Nielsen, J. y Landauer, T. K. (1993). A mathematical model of the finding of usability problems. *INTERCHI '93*, 206-213.
- Sauro, J. (2011). *A practical guide to the System Usability Scale*. MeasuringU.
