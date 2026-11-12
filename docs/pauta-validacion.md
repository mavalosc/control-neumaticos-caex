# Pauta de validación con usuarios
## Herramienta predictiva de desgaste de neumáticos CAEX · Equipo 3 (PROP-09)

> Guion para la sesión. Lo usa **quien facilita** (Nicolás Echeverría). El diseño, las hipótesis y los umbrales están en [`prueba-usuarios.md`](prueba-usuarios.md).
>
> Duración estimada: **40 minutos** · Modalidad: Google Meet con pantalla compartida y grabación.

---

## 0. Antes de la sesión (checklist del facilitador)

- [ ] Ensayar esta pauta completa con otro integrante del equipo.
- [ ] Abrir https://control-neumaticos-caex-frontend.vercel.app y anotar, **sin decírselo al participante**:
  - los 3 neumáticos con menos horas remanentes del Tablero (respuesta correcta de T1);
  - el neumático con menos horas del **CAEX-102** y si tiene daño crítico (respuesta de T3 y T4).
- [ ] Crear la reunión de Meet y verificar que el botón **Grabar** está disponible (cuenta institucional).
- [ ] Tener a mano el cronómetro, la planilla de la sección 5 y el cuestionario SUS de la sección 4.
- [ ] Pedir al participante que use un computador (no el celular) con Chrome o Edge.

**Reglas del facilitador:** leer cada tarea tal como está escrita. **No explicar, no ayudar, no defender el diseño.** Si pregunta qué hacer, responder: *«¿Qué haría usted si estuviera solo?»*. El silencio y la duda son el dato que se busca.

---

## 1. Bienvenida y consentimiento (5 min · antes de grabar)

> «Gracias por ayudarnos. Somos estudiantes de Ingeniería Digital de la USACH y estamos probando una herramienta para planificar el cambio de neumáticos de camiones mineros. **No lo estamos evaluando a usted, evaluamos la herramienta**: si algo no se entiende, es un problema del diseño y justamente eso buscamos. No hay respuestas correctas.
>
> Le pediré que haga algunas tareas y que **piense en voz alta**: diga qué busca, qué espera que pase y qué le sorprende. Yo no podré ayudarle durante las tareas, porque queremos ver qué pasaría si estuviera solo.»

**Consentimiento** (leerlo y, ya grabando, pedir la aceptación en voz alta):

> «Vamos a **grabar la pantalla y la voz**, con la cámara apagada. La grabación la verán solo el equipo del proyecto y el profesor del curso, se guarda en una carpeta privada y se elimina el 31 de diciembre de 2026. En nuestras notas aparecerá como "P1", sin su nombre.
>
> La herramienta le pedirá un email para registrar quién hace cada cambio. Puede usar el suyo o, si lo prefiere, escribir **p1@prueba.cl**. Las órdenes que cree se anularán al terminar.
>
> Puede detener la sesión cuando quiera. **¿Está de acuerdo con participar y con que grabemos?**»

▶ **Iniciar la grabación** y repetir la última pregunta para que la aceptación quede grabada.

---

## 2. Preguntas sobre su experiencia (5 min · *The Mom Test*)

Preguntar por hechos pasados, no por opiniones futuras. **No mostrar todavía la herramienta.**

1. Cuénteme de la **última vez** que hubo que retirar o cambiar un neumático. ¿Cómo supo que había que hacerlo?
2. ¿Qué información usó para decidir **cuándo** hacerlo? ¿De dónde la sacó?
3. ¿Qué pasó la última vez que un neumático falló **antes** de lo previsto? ¿Qué hicieron?
4. ¿Cómo queda registrado hoy quién decidió el cambio y por qué?
5. ¿Usa computador o tablet en su trabajo diario? ¿Para qué?

*Si el participante no trabaja en neumáticos, preguntar por una tarea de planificación de mantención que haya hecho y anotar «perfil aproximado».*

❌ No preguntar: «¿Le serviría una herramienta que…?», «¿Usaría esto?».

---

## 3. Tareas (25 min)

Leer el **escenario** tal como está. Anotar la hora de inicio y de término de cada tarea. La columna «No revelar» es solo para el facilitador.

> Antes de la T1: «Ahora le comparto el enlace de la herramienta. Ábralo, compártame su pantalla y empecemos.»

| # | Escenario (leer en voz alta) | Criterio de éxito (observable) | No revelar |
|---|---|---|---|
| **T1** | «Usted es el planificador de neumáticos y empieza su turno de la mañana. Su jefe le pide saber **cuáles son los tres neumáticos que hay que atender primero**. Dígame cuáles son.» | Ingresa a la herramienta y nombra los 3 de menos horas remanentes en ≤ 3 min | Que el Tablero está ordenado por horas; los filtros |
| **T2** | «Le avisan por radio que uno de los camiones tiene un neumático con un **daño grave**. Asegúrese de que el despacho de la mina se entere.» | Encuentra el aviso de daño crítico y lo envía a despacho | El banner de alerta y su botón |
| **T3 ★** | «El neumático más urgente del **camión 102** tiene que cambiarse antes de que se gaste. **Deje programado ese trabajo en el taller.**» | Queda emitida una orden para ese neumático, en un turno con cupo y antes de que llegue al límite, en ≤ 4 min y con ≤ 1 pedido de ayuda | Ficha, botón de agendar, ventanas, órdenes |
| **T4** | «Revisando la foto de ese neumático, usted cree que el daño **no es tan grave** como dice el sistema: es moderado. **Deje registrado su criterio.**» | Cambia el nivel del daño a 2 y queda guardado | La corrección de daño en la Ficha |
| **T5** | «El taller le avisa que **no podrá atender en el turno** que usted eligió. Cambie el trabajo a otro turno y deje constancia de por qué.» | Modifica la orden con un motivo escrito | Órdenes, Modificar, motivo obligatorio |
| **T6** | «Su jefe le pregunta **cuántas horas le quedan** a ese neumático y **por qué se está gastando** así. Respóndale con lo que ve en la herramienta.» | Da una cifra de horas, dice de dónde sale (cálculo o modelo) y menciona al menos una causa; anotar si se apoya solo en «Modelo · sim» | Columnas de horas, causas SHAP, página Modelos |

Durante las tareas, si el participante se queda en silencio: *«¿Qué está pensando ahora?»*. Si pregunta si lo hizo bien: *«¿Usted qué cree?»*. Si a los **5 minutos** de una tarea no avanza, se pasa a la siguiente y se marca como **no completada**.

---

## 4. Cierre (5 min)

**4.1 Escala de usabilidad del sistema (SUS).** Leer cada frase; el participante responde de 1 (*totalmente en desacuerdo*) a 5 (*totalmente de acuerdo*).

| # | Frase | 1-5 |
|---|---|---|
| 1 | Creo que me gustaría usar esta herramienta con frecuencia. | |
| 2 | Encontré la herramienta innecesariamente compleja. | |
| 3 | Pensé que la herramienta era fácil de usar. | |
| 4 | Creo que necesitaría ayuda de una persona con conocimientos técnicos para usarla. | |
| 5 | Encontré que las distintas funciones de la herramienta estaban bien integradas. | |
| 6 | Pensé que había demasiadas inconsistencias en la herramienta. | |
| 7 | Imagino que la mayoría de las personas aprendería a usarla muy rápido. | |
| 8 | Encontré la herramienta muy engorrosa de usar. | |
| 9 | Me sentí muy seguro usando la herramienta. | |
| 10 | Necesité aprender muchas cosas antes de poder usarla. | |

**Cálculo:** a las frases impares se les resta 1; a las pares se les resta su valor a 5; se suma todo y se multiplica por 2,5. Resultado de 0 a 100 (referencia: 68).

**4.2 Preguntas abiertas**

1. ¿Qué fue lo más difícil o confuso?
2. ¿Hubo algún momento en que no supo qué hacer? ¿Cuál?
3. Pensando en la última vez que cambiaron un neumático, ¿qué parte de lo que hizo hoy le habría servido y qué parte no?

> «Muchas gracias. Lo que encontró difícil es justamente lo que vamos a mejorar.»

⏹ **Detener la grabación.** Anotar los códigos de las órdenes que creó (Órdenes de trabajo) para anularlas con el motivo «prueba de usuarios P1».

---

## 5. Planilla de observaciones (se completa desde la grabación)

Una fila por observación. **Observado** = lo que otra persona podría verificar en la grabación (acciones, palabras, tiempos). **Interpretado** = la hipótesis del equipo sobre por qué ocurrió.

| # | Minuto | Tarea | Observado | Cita textual | Interpretado | Severidad (bloquea / entorpece / estético) |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |

**Resumen por tarea**

| Tarea | Completó sin ayuda (sí/no) | Tiempo | Pedidos de ayuda | Desvíos (pantallas equivocadas) |
|---|---|---|---|---|
| T1 | | | | |
| T2 | | | | |
| T3 ★ | | | | |
| T4 | | | | |
| T5 | | | | |
| T6 | | | | |

Los resultados se trasladan a la sección 6 de [`prueba-usuarios.md`](prueba-usuarios.md).

---

## 6. Preguntas para un stakeholder (si se consigue)

No ejecuta tareas. Se le muestra el Tablero y se le pregunta por condiciones de adopción:

1. ¿Quién tendría que aprobar que el área use una herramienta así?
2. ¿Con qué sistemas tendría que conectarse (ERP, TPMS, despacho) para que no signifique doble trabajo?
3. ¿Qué tendría que demostrar un piloto para que lo mantengan después del curso?
4. ¿Qué datos de la faena podrían compartirse y bajo qué condiciones?
