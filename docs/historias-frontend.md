# Historias de usuario del front end

> Borrador del Equipo 3. Parte de las tres pantallas ya construidas (capturas en [`img/`](img/)) y propone mejoras que integran el **nivel de daño** detectado en las fotos. Cada historia indica si **ya existe** en la interfaz o es una **mejora propuesta**. El recorrido y los criterios deben validarse con un planificador de Mantención de Neumáticos.

## Pantallas actuales

| Pantalla | Captura | Qué hace hoy |
|---|---|---|
| Tablero del turno | ![Tablero](img/ui-tablero.jpg) | Flota ordenada por horas de vida útil remanente, con resumen por zona y filtros |
| Camiones | ![Camiones](img/ui-camiones.jpg) | Seis posiciones por CAEX, cada una abre la ficha del neumático |
| Órdenes de trabajo | ![Órdenes](img/ui-ordenes.jpg) | Órdenes con estado, tipo y trazabilidad a la medición que las originó |

**Zonas de vida útil (según el tablero):** rojo, menos de 200 h, programar el retiro ahora · amarillo, menos de 500 h, entra a la próxima ventana · verde, más de 500 h · sin datos, sin mediciones y por tanto sin proyección.

## Backlog

| Código | Historia | Pantalla | Estado |
|---|---|---|---|
| HU-F01 ★ | Ver la flota ordenada por horas remanentes y zona | Tablero | Existe |
| HU-F02 | Buscar y filtrar el tablero | Tablero | Existe |
| HU-F03 ★ | Ver los camiones con sus seis posiciones | Camiones | Existe |
| HU-F04 ★ | Abrir la ficha y registrar una medición | Ficha | Existe |
| HU-F05 | Ver el daño detectado con la foto marcada y corregirlo | Ficha | Mejora |
| HU-F06 | Ver el nivel de daño y las alertas críticas en tablero y camiones | Tablero, Camiones | Mejora |
| HU-F07 ★ | Consultar y filtrar las órdenes de trabajo | Órdenes | Existe |
| HU-F08 | Ver la trazabilidad de una orden hasta su evidencia | Órdenes | Parcial |
| HU-F09 | Modificar una orden programada | Órdenes | Mejora |
| HU-F10 | Anular una orden con su motivo | Órdenes | Mejora |

★ = flujo principal. Orden según la secuencia real de uso.

---

## HU-F01 ★ Ver la flota ordenada por horas remanentes y zona
**Como** planificador de Mantención de Neumáticos, **quiero** ver al iniciar el turno la flota ordenada por horas de vida útil remanente y agrupada por zona, **para** programar primero los retiros más urgentes sin revisar neumático por neumático.

**Escenario principal**
- **Dado** que existen mediciones de la flota
- **Cuando** abro el tablero del turno
- **Entonces** veo cuatro tarjetas (rojo, amarillo, verde, sin datos) con su cantidad, y una tabla ordenada de menos a más horas remanentes con camión, posición, serial, profundidad, tasa, horas, zona y última medición

**Escenario alternativo**
- **Dado** que un neumático no tiene mediciones
- **Cuando** abro el tablero
- **Entonces** cuenta en «sin datos» y su fila indica que no hay proyección

## HU-F02 Buscar y filtrar el tablero
**Como** planificador, **quiero** buscar por serial, camión o modelo y filtrar por zona y por tipo de tasa, **para** llegar rápido al neumático o grupo que me interesa.

**Escenario principal**
- **Dado** que estoy en el tablero
- **Cuando** elijo la zona «rojo» y la tasa «observada»
- **Entonces** la tabla muestra solo los neumáticos que cumplen ambas condiciones

**Escenario alternativo**
- **Dado** que mi búsqueda no coincide con ningún neumático
- **Cuando** termino de escribir
- **Entonces** veo un mensaje «sin resultados» y la opción de limpiar los filtros

## HU-F03 ★ Ver los camiones con sus seis posiciones
**Como** planificador, **quiero** ver cada CAEX con sus seis posiciones coloreadas por zona, **para** entender el estado de un camión completo de un vistazo.

**Escenario principal**
- **Dado** que estoy en la pantalla Camiones
- **Cuando** se muestra cada camión
- **Entonces** veo su modelo, su horómetro, la cantidad de posiciones en rojo y las posiciones P1 a P6 con sus horas remanentes

**Escenario alternativo**
- **Dado** que una posición no tiene neumático medido
- **Cuando** se dibuja el camión
- **Entonces** la posición aparece como «sin datos» y sigue siendo seleccionable

## HU-F04 ★ Abrir la ficha y registrar una medición
**Como** planificador, **quiero** abrir la ficha de un neumático desde el tablero o desde un camión y registrar una nueva medición, **para** mantener actualizada su proyección.

**Escenario principal**
- **Dado** que selecciono un neumático
- **Cuando** abro su ficha y registro una medición válida
- **Entonces** la ficha, el tablero y el camión muestran la proyección recalculada

**Escenario alternativo**
- **Dado** que la medición tiene un valor imposible (por ejemplo, mayor que la anterior)
- **Cuando** intento guardarla
- **Entonces** el sistema la rechaza con el motivo y conserva la proyección vigente

## HU-F05 Ver el daño detectado con la foto marcada y corregirlo *(mejora)*
**Como** planificador, **quiero** ver en la ficha la foto del neumático con cada daño marcado, su tipo y su nivel, y poder corregirlo, **para** confirmar la gravedad con evidencia y no con una impresión.

**Escenario principal**
- **Dado** que el neumático tiene una foto procesada
- **Cuando** abro su ficha
- **Entonces** veo la foto con cada daño marcado, su tipo, su nivel (0 a 3), su confianza y la fecha de la pasada

**Escenario alternativo**
- **Dado** que el modelo clasificó mal un daño
- **Cuando** lo corrijo e indico el motivo
- **Entonces** la ficha muestra la corrección con mi nombre y la fecha, y la foto queda guardada para reentrenar

## HU-F06 Ver el nivel de daño y las alertas críticas *(mejora)*
**Como** planificador, **quiero** ver el nivel de daño junto a la zona de vida útil en el tablero y en cada posición del camión, y una alerta cuando un neumático esté en nivel 3, **para** no depender solo de las horas cuando hay un daño grave.

**Escenario principal**
- **Dado** que un neumático está en nivel 3
- **Cuando** abro el tablero
- **Entonces** aparece una alerta que lleva a su ficha, y la fila y la posición del camión muestran el nivel además de la zona

**Escenario alternativo**
- **Dado** que un neumático está en zona verde pero con daño nivel 3
- **Cuando** se ordena el tablero
- **Entonces** sube al primer lugar, porque el daño crítico prevalece sobre las horas

## HU-F07 ★ Consultar y filtrar las órdenes de trabajo
**Como** planificador, **quiero** ver las órdenes con su estado, tipo, fecha programada y turno, y filtrarlas, **para** saber qué está pendiente y qué ya se hizo.

**Escenario principal**
- **Dado** que existen órdenes
- **Cuando** abro Órdenes de trabajo
- **Entonces** veo los contadores por estado (programada, ejecutada, anulada) y la tabla con orden, neumático, intervención y nota, fecha programada, horas al emitir, origen y estado

**Escenario alternativo**
- **Dado** que filtro por estado «programada» y tipo «retiro»
- **Cuando** no existe ninguna con ambas condiciones
- **Entonces** veo «sin resultados» y los contadores no cambian

## HU-F08 Ver la trazabilidad de una orden hasta su evidencia *(parcial)*
**Como** planificador, **quiero** que cada orden muestre la medición que la originó y la evidencia asociada, **para** sustentar el retiro frente al taller y reclamar al proveedor.

**Escenario principal**
- **Dado** que abro una orden de retiro
- **Cuando** reviso su origen
- **Entonces** veo la medición (por ejemplo, profundidad y tasa observada), la proyección con que se emitió y, en la mejora, la foto con los daños de ese momento

**Escenario alternativo**
- **Dado** que la orden es anterior al registro de fotos
- **Cuando** la abro
- **Entonces** muestra la medición y avisa que no tiene foto asociada

## HU-F09 Modificar una orden programada *(mejora)*
**Como** planificador, **quiero** cambiar la ventana o la nota de una orden que aún está programada, **para** ajustarla cuando cambian las condiciones sin tener que anularla y emitirla de nuevo.

**Escenario principal**
- **Dado** que una orden está en estado «programada»
- **Cuando** elijo otra ventana con cupos, indico el motivo del cambio y guardo
- **Entonces** la orden muestra la nueva ventana, se libera el cupo anterior y se ocupa el nuevo, el taller es notificado y el historial registra quién, cuándo y por qué

**Escenario alternativo**
- **Dado** que una orden ya está ejecutada o anulada
- **Cuando** intento modificarla
- **Entonces** el sistema no permite el cambio, explica el estado de la orden y muestra su historial

**Reglas:** el motivo es obligatorio; no se puede elegir una ventana sin cupos; la orden conserva su código y su vínculo a la medición de origen.

## HU-F10 Anular una orden con su motivo *(mejora)*
**Como** planificador, **quiero** anular una orden programada indicando el motivo, **para** liberar el cupo del taller sin perder el registro de lo que ocurrió.

**Escenario principal**
- **Dado** que una orden está «programada»
- **Cuando** elijo un motivo, pulso «Anular orden» y confirmo
- **Entonces** la orden pasa a «anulada», se libera su cupo, el contador de anuladas sube en uno y la orden permanece en la lista con su motivo

**Escenario alternativo**
- **Dado** que abrí la confirmación de anulación
- **Cuando** elijo «No»
- **Entonces** la orden queda sin cambios y vuelvo al formulario

**Reglas:** la anulación pide confirmación explícita; la orden nunca se borra, porque es evidencia para la reunión semanal y para el proveedor; una orden anulada no se puede reactivar (se emite una nueva).

---

## Mejoras observadas en las capturas

| Observación | Propuesta | Historia |
|---|---|---|
| Las zonas se basan solo en horas remanentes | Mostrar también el nivel de daño de la foto y priorizar el daño crítico | HU-F06 |
| Las posiciones del camión muestran solo horas | Agregar el nivel de daño y un nivel por camión | HU-F06 |
| La ficha registra mediciones, pero no muestra la imagen | Foto con daños marcados, confianza y corrección | HU-F05 |
| El campo de búsqueda del tablero corta el texto de ayuda | Ensancharlo o acortar el texto | HU-F02 |
| Las notas largas alargan mucho las filas de órdenes | Mostrar un resumen y expandir al hacer clic | HU-F07 |
| La orden guarda la medición, no la evidencia visual | Vincular la foto del momento de la orden | HU-F08 |
| Las capturas no muestran cómo modificar o cancelar una orden | Acciones «Modificar» y «Anular» con motivo e historial | HU-F09, HU-F10 |
| La columna «última medición» muestra «(obs.)» sin explicar | Definir su significado y agregar una leyenda | HU-F01 |

## Revisión INVEST
Las historias de mejora (HU-F05, HU-F06, HU-F08) dependen de que el modelo de visión entregue daños y fotos. Mientras no exista, trabajarlas con fotos y daños de ejemplo, y dividirlas si no caben en un sprint (por ejemplo, separar la alerta crítica de la corrección).
