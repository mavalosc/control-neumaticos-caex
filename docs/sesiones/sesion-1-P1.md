# Sesión 1 · P1 · tablas de la pauta completadas
## Herramienta predictiva de desgaste de neumáticos CAEX · Equipo 3 (PROP-10)

> Registro de la sesión del **13-11-2026** con las tablas de [`pauta-validacion.md`](../pauta-validacion.md) completadas. El resumen, las hipótesis y las decisiones están en la sección 6 de [`prueba-usuarios.md`](../prueba-usuarios.md).
>
> **Fuentes:** grabación de Meet (22:55 min), transcrita y analizada con Gemini (segunda entrega, con pantalla) y contrastada con los registros de Supabase (orden ot-0072 y correcciones de daño). Los minutos corresponden a la grabación.
>
> **Anonimización:** el participante es **P1** y la faena, «gran minería». En las citas, los nombres se reemplazan por `[nombre]`. `NO CONSTA` indica un dato que no aparece en la grabación.

| Dato | Valor |
|---|---|
| Participante | P1 · mantenedor de neumáticos, 8 años de experiencia en neumáticos OTR, gran minería · **perfil aproximado** |
| Facilitador | Integrante del equipo; no hubo observador con intervención audible |
| Consentimiento | Explicado de 00:47 a 01:08 · aceptación grabada en 04:52: «Sí, sí, obvio» |
| Ingreso a la app | 04:32 a 04:44 con `p1@prueba.cl`, sin dificultad |

---

## 2. Preguntas sobre su experiencia (*The Mom Test*)

| # | Pregunta | Respuesta de P1 (resumen fiel) |
|---|---|---|
| 1 | La última vez que hubo que retirar o cambiar un neumático | «Por imprevisto fue el día de ayer, por un pinchazo.» Los cambios son programados o por imprevisto |
| 2 | Qué información usó para decidir cuándo | «Nos basamos tanto en las horas que lleva el neumático rodando como en el desgaste que tiene» |
| 3 | La última vez que falló antes de lo previsto | El mismo pinchazo: «teníamos el seguimiento de ese camión por nivel de remanente, pero falló antes de lo previsto» |
| 4 | Cómo queda registrado quién decidió el cambio | «Tenemos un papel de registro de cambio de neumático, en el cual ponemos el neumático que salió, y autoriza el supervisor» |
| 5 | Uso de computador o tablet | «Un celular adaptado a tablet que nos permite acercarnos a las presiones de los equipos» |

**Lectura:** el registro actual es en papel y lo autoriza el supervisor; las horas de uso y el desgaste son los dos criterios de decisión. Esto respalda el hallazgo 12 (horas acumuladas).

---

## 4.1 Escala de usabilidad del sistema (SUS)

| # | Frase | 1-5 | Minuto | Aporte |
|---|---|---|---|---|
| 1 | Creo que me gustaría usar esta herramienta con frecuencia. | 4 | 17:08 | 3 |
| 2 | Encontré la herramienta innecesariamente compleja. | 1 | 17:17 | 4 |
| 3 | Pensé que la herramienta era fácil de usar. | 1 (confirmado) | 17:27 | 0 |
| 4 | Creo que necesitaría ayuda de una persona con conocimientos técnicos para usarla. | 3 | 17:39 | 2 |
| 5 | Encontré que las distintas funciones de la herramienta estaban bien integradas. | 5 | 17:49 | 4 |
| 6 | Pensé que había demasiadas inconsistencias en la herramienta. | 1 | 17:58 | 4 |
| 7 | Imagino que la mayoría de las personas aprendería a usarla muy rápido. | 4 | 18:07 | 3 |
| 8 | Encontré la herramienta muy engorrosa de usar. | 2 | 18:16 | 3 |
| 9 | Me sentí muy seguro usando la herramienta. | 4 | 18:24 | 3 |
| 10 | Necesité aprender muchas cosas antes de poder usarla. | 3 | 18:34 | 2 |

**Puntaje:** impares (respuesta − 1) = 13; pares (5 − respuesta) = 15; (13 + 15) × 2,5 = **70** (referencia 68).

**Ítem 3 confirmado en la grabación (21-11-2026):** P1 respondió 1. Contradice los ítems 2 y 8 y lo que dijo en el cierre («está fácil de interpretar»); puede ser una confusión con el sentido de la escala. El puntaje queda en **70**.

## 4.2 Preguntas abiertas

| # | Pregunta | Respuesta de P1 (resumen fiel) |
|---|---|---|
| 1 | ¿Qué fue lo más difícil o confuso? | Por ser primera vez: «el tema de hacer órdenes fue buscarlo arriba», en la barra superior. «Fue acomodación, pero de por sí está fácil de interpretar y acostumbrarse» |
| 2 | ¿Hubo algún momento en que no supo qué hacer? | «Sí, por no conocer el sistema al ser primerizo»; el mismo ejemplo de las órdenes |
| 3 | ¿Qué parte de lo de hoy le habría servido la última vez y cuál no? | (20:42) «Más allá de cuántas horas le quedan al neumático, generalmente nos preguntan cuántas horas tenía el neumático ya rodando»: le agregaría las horas acumuladas de uso junto a la proyección |

---

## 5. Planilla de observaciones

Severidad según la escala de la pauta: **bloquea**, **entorpece** o **estético**. Las filas 12 y 13 no tienen severidad de usabilidad (requisito nuevo y vacío detectado en la base de datos).

| # | Minuto | Tarea | Observado | Cita textual | Interpretado | Severidad |
|---|---|---|---|---|---|---|
| 1 | 07:11 | T1 | Pasa el cursor por los filtros de zona sin hacer clic y pregunta si puede filtrar | «¿Puedo aplicar un solo filtro? […] el filtro de profundidad en conjunto a la severidad» | Quiere combinar profundidad y severidad; los filtros solo son por zona y tipo de tasa | Entorpece |
| 2 | 07:48 | T1 | Hace clic en el encabezado «Severidad daño»; la tabla sigue ordenada por horas | «Ayuda bastante guiarse bajo la profundidad con las horas proyectadas junto a la severidad» (08:10) | Espera poder ordenar por severidad | Entorpece |
| 3 | 09:48 | T2 | Pregunta qué camión debe reportar | «¿Podría ser el 106 o tiene que ser dentro de los que elegí recién?» | La consigna no dice el camión; debe buscar el daño crítico | Estético |
| 4 | 10:12 | T2 | No usa el botón «Avisar Despacho Mina» del banner; entra a la Ficha del CAEX-122 P1 y avisa desde ahí (10:20). La app confirma el aviso (10:22) | «Aquí avisaría a despacho […] ya aplicando acá debiese informarle al despacho» | Valida el daño en la Ficha antes de avisar | Estético |
| 5 | 11:18 | T3 | Elige la ventana de 56 h para un neumático de 20 h; aparece en rojo «el neumático cruzará el umbral 36 h antes de esta ventana»; no la comenta y confirma (11:24) | «Si es crítico lo ocuparía dentro de las 56 horas, quizás lo más pronto posible» | La advertencia no detiene la decisión; era la única ventana con cupo | Entorpece |
| 6 | 12:12 | T4 | Sale de Órdenes, abre el CAEX-102 P6 y vuelve al P3 (12:18) | NO CONSTA (navega en silencio) | Tras emitir la orden pierde el contexto de la Ficha | Entorpece |
| 7 | 12:44 | T4 | Tras marcar Leve aparece un aviso breve arriba a la derecha; pregunta si se guardó | «¿Y ahí se guardaría solo, cierto? O hay que apretar un botón de guardar» | El guardado automático no se percibe | Entorpece |
| 8 | 13:16 | T4 | Prueba Moderado y vuelve a Leve: 3 registros de corrección en 40 s. Al cambiar el nivel, la descripción pasa de «roca incrustada» a «desgaste irregular» (12:40) | «Puedes ir jugando […] si después me arrepiento lo vuelvo a cambiar» | Las pruebas quedan en la auditoría y la corrección reemplaza la descripción detectada | Entorpece |
| 9 | 14:10 | T5 | Escribe el motivo en «Justificación de la nota» y borra la justificación técnica; luego escribe «Cambio por HH» en el motivo (14:34) | «Motivo del cambio, voy a borrar, ayayay» | Dos campos de texto seguidos; el primero reemplaza la justificación original | Entorpece |
| 10 | 13:58 | T5 | Reprograma a la ventana de 84 h (aún más tarde) y la pantalla Modificar no muestra advertencia | NO CONSTA | La validación de plazo no existe al modificar | Entorpece |
| 11 | 15:40 | T6 | En la Ficha del CAEX-102 **P6** (no el P3 de las tareas anteriores) lee las causas SHAP | «Me están quedando 344 horas. Generalmente porque la presión de inflado ha estado reducida y el terreno ha andado bien» | Lee «Presión de inflado · reduce» como presión baja; no distingue las 344 h de la fórmula de las 253 h del modelo | Entorpece |
| 12 | 20:42 | Cierre | Busca las horas acumuladas de uso del neumático | «Nos preguntan cuántas horas tenía el neumático ya rodando» | Para decidir el retiro se contrasta la vida cumplida con la remanente | Requisito nuevo |
| 13 | — | T4 | En Supabase las 3 correcciones quedaron con autor «planificador», no con el email | — | El ingreso por email (PROP-08) solo registra al autor en las órdenes | Vacío del equipo |

**Resumen por tarea**

| Tarea | Inicio | Término | Duración | Completó sin ayuda | Pedidos de ayuda | Desvíos (pantallas equivocadas) |
|---|---|---|---|---|---|---|
| T1 | 06:24 | 09:05 | 02:41 | Sí: primera respuesta correcta (06:44); la cambió tras la pregunta del facilitador (06:58) | 1 (07:11) | Fichas del CAEX-122 P1 (07:56) y del CAEX-162 P1 (08:38) |
| T2 | 09:27 | 10:39 | 01:12 | Sí | 2 (09:32 canal; 09:48 alcance) | Avisó desde la Ficha del CAEX-122 P1 y no desde el banner |
| T3 ★ | 10:59 | 11:36 | 00:37 | Sí, la emisión; el plazo no era evaluable (ninguna ventana con cupo llegaba antes de 20 h) | 0 | Ninguno |
| T4 | 11:48 | 13:29 | 01:41 | No evaluable: el neumático ya estaba en Moderado (pruebas del equipo del 17-10); terminó en Leve | 1 (12:44) | Camiones → CAEX-102 P6 → vuelta al P3 |
| T5 | 13:41 | 14:47 | 01:06 | Sí | 0 | Ninguno |
| T6 | 15:02 | 16:33 | 01:31 | Parcial: horas y causas de otro neumático (P6) | 0 (el facilitador releyó la consigna en 15:19) | Abrió el CAEX-102 P6 en vez del P3 |

---

## 6. Preguntas para un stakeholder

No se realizó en la sesión 1: no participó una jefatura.

---

**Datos que dejó la prueba:** la ot-0072 se anuló el 14-11-2026 con el motivo «prueba de usuarios P1» y el daño del P3 del CAEX-102 se restauró a «3 · corte profundo en flanco» (registro «restauración PROP-10»).
