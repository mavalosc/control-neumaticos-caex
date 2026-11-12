# Diseño de la prueba con usuarios
## Herramienta predictiva de desgaste de neumáticos CAEX · Equipo 3 · Semanas 7-8 (PROP-09)

> Lo que separa la prueba de concepto (PoC) del producto mínimo viable (MVP) es esta validación: un **experimento diseñado para encontrar dónde falla el diseño**, no una demostración. Si el resultado contradice al equipo, la prueba funcionó.
>
> Pauta de la sesión: [`pauta-validacion.md`](pauta-validacion.md) · Resguardos éticos: [`etica.md`](etica.md) · Recorrido que se valida: [`experiencia-usuario.md`](experiencia-usuario.md)
>
> Versión 1 · 12-11-2026 · Responsable de la prueba: **Nicolás Echeverría** · Plazo de la primera sesión: **21-11-2026**

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

- **Reclutamiento:** Nicolás Echeverría consigue al voluntario. Se prefiere a alguien que planifique o ejecute mantención de neumáticos o de equipos mineros; Héctor Medina puede sugerir contactos del área de reparación de neumáticos.
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

### Sesión 1 · P1 · pendiente (plazo 21-11-2026)

*Completa Nicolás después de la sesión.*

| Dato | Valor |
|---|---|
| Fecha y duración | |
| Perfil del participante | (cargo genérico, años de experiencia, uso de computador; sin nombre) |
| Enlace a la grabación (Drive restringido) | |
| Consentimiento grabado | sí / no |

| Hipótesis | Resultado P1 | Evidencia (minuto de la grabación) |
|---|---|---|
| H1 · emite la orden sin ayuda | | |
| H2 · tiempo de T3 y pedidos de ayuda | | |
| H3 · identifica los 3 más urgentes | | |
| H4 · distingue fórmula y modelo | | |
| H5 · puntaje SUS | | |

**Hallazgos priorizados**

| # | Observado | Interpretación | Severidad | Decisión | Responsable |
|---|---|---|---|---|---|
| | | | | | |

---

## Referencias

- Brooke, J. (1996). SUS: A quick and dirty usability scale. En *Usability evaluation in industry* (pp. 189-194). Taylor & Francis.
- Fitzpatrick, R. (2013). *The Mom Test*. Founder Centric.
- ISO. (2018). *ISO 9241-11:2018. Ergonomía de la interacción persona-sistema: usabilidad*.
- Nielsen, J. (1994). *Severity ratings for usability problems*. Nielsen Norman Group.
- Nielsen, J. y Landauer, T. K. (1993). A mathematical model of the finding of usability problems. *INTERCHI '93*, 206-213.
- Sauro, J. (2011). *A practical guide to the System Usability Scale*. MeasuringU.
