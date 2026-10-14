# Historias de Usuario y Criterios de Aceptación (BDD / Gherkin)
## Proyecto: Pórtico Dimensional Predictivo de Neumáticos CAEX
### Ingeniería Digital en Acción (Ecosistema DSD - USACH) · Equipo 3

> **Estándar:** historias en formato **"Como… quiero… para…"**, revisadas con **INVEST**, y criterios de aceptación en **Gherkin en español** (`Característica`, `Escenario`, `Dado`, `Cuando`, `Entonces`, `Y`, `Pero`).
> **Trazabilidad unívoca:** los códigos `HU-01` a `HU-08` son idénticos en el Roadmap de Notion (tablero *20261011 Roadmap*), en este documento y en los wireframes anotados de [`docs/wireframes/`](wireframes/README.md). Los campos citados están definidos en [`docs/datos.md`](datos.md).

---

## Flujo principal

La historia que sostiene el flujo central de la solución es **HU-07 · Emisión de Orden de Trabajo y Trazabilidad ERP / SAP PM**. Es el resultado que el Roadmap pone en *Ahora*: *"Que el planificador agende la intervención de una goma crítica y que la orden quede escrita con su trazabilidad a la medición que la originó"*.

El planificador llega a ella recorriendo cuatro historias, que corresponden a los wireframes W1 a W4:

```
HU-01 Tablero (W1) ──► HU-04 Ficha (W2) ──► HU-06 Agendar (W3) ──► ★ HU-07 Orden emitida (W4)
                                                                         │
                                                       HU-08 Modificar o anular (W5)
```

HU-02 (alerta crítica), HU-03 (vista de camiones) y HU-05 (reclasificación) son caminos alternativos que desembocan en la misma ficha (W2).

---

## Matriz de Trazabilidad

| Código | Historia de Usuario | Rol | Wireframe | Horizonte Notion | Tablas Supabase | Estado |
|---|---|---|---|---|---|---|
| **HU-01** | Tablero del Turno y Priorización por Horas Remanentes | Planificador | W1 | Ahora | `vista_tablero_turno` | Implementado |
| **HU-02** | Alerta Inmediata de Daño Crítico y Desvío a Despacho | Despachador / Planificador | W1 (banner) | Próximo | `danos_neumaticos` | Implementado |
| **HU-03** | Visualización Matricial de Flota y Chasis 6x4 | Planificador | Camino alternativo a W2 | Ahora | `camiones`, `neumaticos` | Implementado |
| **HU-04** | Ficha Técnica, Escáner 3D y Curva de Desgaste | Planificador | W2 | Ahora | `mediciones`, `danos_neumaticos` | Implementado |
| **HU-05** | Validación y Reclasificación de Daños (Humano en el Bucle) | Planificador | W2 (panel) | Próximo | `danos_neumaticos` | Implementado |
| **HU-06** | Agendamiento en Ventana de Taller con Control de Cupos | Planificador | W3 | Ahora | `ventanas_taller` | Implementado |
| **HU-07** ★ | Emisión de Orden de Trabajo y Trazabilidad ERP / SAP PM | Planificador | W4 | Ahora | `ordenes_trabajo`, `historial_ordenes` | Implementado |
| **HU-08** | Modificación y Anulación de OT con Motivo Obligatorio | Planificador | W5 | Próximo | `ordenes_trabajo`, `historial_ordenes` | Implementado |

★ Flujo principal.

---

## Especificación de las Historias

### HU-01: Tablero del Turno y Priorización por Horas Remanentes
**Como** planificador de mantención de neumáticos,
**quiero** ver al inicio del turno todos los neumáticos montados ordenados de menor a mayor horas de vida útil remanente y clasificados por zona de criticidad,
**para** priorizar las intervenciones más urgentes sin revisar camión por camión.

```gherkin
# language: es
Característica: Tablero del turno (HU-01)

  Escenario: Ver la flota ordenada por horas remanentes (camino feliz)
    Dado que Supabase tiene mediciones para los 67 camiones CAEX-101 a CAEX-167
    Cuando el planificador abre el "Tablero de Control del Turno"
    Entonces ve cuatro tarjetas de resumen: "Zona Roja" (< 200 h), "Zona Amarilla" (< 500 h), "Zona Verde" (> 500 h) y "Sin Proyección"
    Y la tabla lista los neumáticos ordenados de menor a mayor horas remanentes
    Y cada fila muestra camión, posición, serial, profundidad (mm), tasa (mm/100 h), horas remanentes, zona y nivel de daño
    Y el pie de la tabla indica "Mostrando 1 a 25 de 402 neumáticos (67 CAEX · 402 neumáticos)"

  Escenario: Búsqueda sin coincidencias (excepción)
    Dado que el planificador está en el "Tablero de Control del Turno"
    Cuando escribe el serial inexistente "5980R63-9999-9999" en el buscador
    Entonces la tabla muestra el mensaje "No se encontraron neumáticos con los filtros seleccionados."
    Y el pie de la tabla indica "Mostrando 0 a 0 de 0 neumáticos"
```

---

### HU-02: Alerta Inmediata de Daño Crítico y Desvío a Despacho
**Como** despachador de mina o planificador,
**quiero** recibir una alerta visual prioritaria cuando un neumático tenga daño nivel 3 (crítico),
**para** sacar el camión del circuito de acarreo antes de un reventón en la rampa.

```gherkin
# language: es
Característica: Alerta de daño crítico (HU-02)

  Escenario: Alerta y aviso al despacho (camino feliz)
    Dado que el neumático "5980R63-2426-1348" del CAEX-102, posición P3, tiene daño nivel 3 "corte profundo en flanco"
    Cuando el planificador abre el "Tablero de Control del Turno"
    Entonces aparece sobre las tarjetas el banner rojo "Alerta de Seguridad Operacional Crítica" con el camión, la posición, el daño, su certeza y la temperatura
    Y al presionar "Avisar Despacho Mina" aparece el aviso "ALERTA RADIAL: Se ha notificado al despachador de turno para desviar el CAEX-102…"

  Escenario: Flota sin daños críticos (excepción)
    Dado que ningún neumático tiene daño nivel 3
    Cuando el planificador abre el "Tablero de Control del Turno"
    Entonces el banner "Alerta de Seguridad Operacional Crítica" no se muestra
    Y el tablero comienza directamente con las tarjetas de zona
```

---

### HU-03: Visualización Matricial de Flota y Chasis 6x4
**Como** planificador de mantención de neumáticos,
**quiero** ver cada camión con sus 6 posiciones (P1 a P6) coloreadas según su zona,
**para** detectar desgaste desigual por eje y decidir rotaciones.

```gherkin
# language: es
Característica: Vista de camiones (HU-03)

  Escenario: Revisar el chasis de un camión y abrir un neumático (camino feliz)
    Dado que el planificador abre la vista "Camiones"
    Cuando busca "CAEX-102"
    Entonces ve la tarjeta del CAEX-102 con modelo, horómetro y sus 6 posiciones: P1 y P2 en el eje delantero, P3 a P6 en el tándem trasero dual
    Y cada posición muestra sus horas remanentes con el color de su zona
    Y al hacer clic en la posición P3 se abre la ficha del neumático "5980R63-2426-1348"

  Escenario: Búsqueda de un camión inexistente (excepción)
    Dado que el planificador está en la vista "Camiones"
    Cuando busca "CAEX-999"
    Entonces se muestra el mensaje "No se encontraron camiones con ese criterio."
```

---

### HU-04: Ficha Técnica, Escáner 3D y Curva de Desgaste
**Como** planificador de mantención de neumáticos,
**quiero** abrir la ficha de un neumático con su foto con daños marcados, temperatura de flanco y curva de desgaste frente al umbral de retiro,
**para** respaldar con evidencia la orden de retiro y el reclamo al fabricante.

```gherkin
# language: es
Característica: Ficha del neumático (HU-04)

  Escenario: Consultar la ficha de un neumático en riesgo (camino feliz)
    Dado que el neumático "5980R63-2426-1348" está en zona roja
    Cuando el planificador abre su ficha
    Entonces ve las horas remanentes, la profundidad contra el umbral de 20,0 mm, la tasa de desgaste y la temperatura de flanco
    Y ve el gráfico de las últimas pasadas con la línea punteada del umbral de retiro
    Y ve el daño "corte profundo en flanco" con "Confianza IA: 94%"
    Y el botón "Agendar Intervención en Taller" está habilitado

  Escenario: Daño de baja confianza (excepción)
    Dado que el modelo detectó un daño con confianza menor a 70 %
    Cuando el planificador abre la ficha
    Entonces el daño muestra la etiqueta "por confirmar" junto a su porcentaje de confianza

  Escenario: Neumático sin necesidad de intervención (excepción)
    Dado que el neumático está en zona verde y su daño es nivel 0 o 1
    Cuando el planificador abre la ficha
    Entonces la acción recomendada dice "Neumático en condiciones óptimas para continuar operación"
    Y el botón "Agendar Intervención en Taller" está deshabilitado
```

---

### HU-05: Validación y Reclasificación de Daños (Humano en el Bucle)
**Como** planificador de mantención de neumáticos,
**quiero** corregir el nivel de daño que asignó el modelo de visión,
**para** que prevalezca el juicio experto y quede un registro auditable para reentrenar el modelo.

```gherkin
# language: es
Característica: Corrección de la clasificación de daño (HU-05)

  Escenario: Subir la severidad de un daño (camino feliz)
    Dado que la ficha del neumático "5980R63-2328-1590" muestra daño nivel 1 "Leve"
    Cuando el planificador elige "Moderado" en el panel "Validación del Planificador (Industria 5.0)"
    Entonces aparece el aviso "Clasificación actualizada de Leve a Moderado (registrado en auditoría)"
    Y Supabase guarda una fila en danos_neumaticos con severidad "2", validado_por_humano = true y usuario_validador = "planificador"

  Escenario: Descartar un falso positivo (excepción)
    Dado que el modelo marcó un daño que el planificador reconoce como barro
    Cuando el planificador elige "Sin daño"
    Entonces la ficha muestra "No se detectaron cortes, rocas incrustadas ni delaminaciones en la última pasada."
    Y Supabase guarda una fila en danos_neumaticos con severidad "0"
```

---

### HU-06: Agendamiento en Ventana de Taller con Control de Cupos
**Como** planificador de mantención de neumáticos,
**quiero** elegir una ventana de taller con cupos libres y saber si llega antes de que el neumático cruce el umbral,
**para** asegurar capacidad del taller y evitar que el neumático falle en faena.

```gherkin
# language: es
Característica: Agendar intervención (HU-06)

  Escenario: Elegir una ventana oportuna (camino feliz)
    Dado que el neumático tiene 150 h remanentes
    Y la ventana "29-09-2026 · turno B, 20:00 a 00:00" llega en 36 h y tiene "2 de 3 cupos libres"
    Cuando el planificador selecciona esa ventana
    Entonces la ventana queda resaltada
    Y aparece el mensaje "✓ Ventana oportuna: La intervención se ejecutará con 114 h de margen antes del cruce de umbral."
    Y el botón "Confirmar y Emitir Orden en SAP PM" queda habilitado

  Escenario: Ventana sin cupos (excepción)
    Dado que una ventana tiene "0 de 3 cupos libres"
    Cuando el planificador intenta seleccionarla
    Entonces la ventana se ve atenuada y no se selecciona
    Y el botón "Confirmar y Emitir Orden en SAP PM" sigue deshabilitado

  Escenario: Ventana que llega tarde (excepción)
    Dado que el neumático tiene 34 h remanentes
    Cuando el planificador selecciona una ventana que llega en 56 h
    Entonces aparece el mensaje "⚠️ Advertencia de riesgo: El neumático cruzará el umbral 22 h antes de esta ventana."
```

---

### HU-07 ★: Emisión de Orden de Trabajo y Trazabilidad ERP / SAP PM
**Como** planificador de mantención de neumáticos,
**quiero** que al confirmar la ventana se emita la orden de trabajo con su trazabilidad a la medición que la originó,
**para** enviar el trabajo al taller y tener respaldo para la reunión semanal y el reclamo de garantía.

```gherkin
# language: es
Característica: Emisión de la orden de trabajo (HU-07, flujo principal)

  Escenario: Emitir la orden (camino feliz)
    Dado que el planificador eligió una ventana con cupo para el neumático "5980R63-2531-1596"
    Cuando presiona "Confirmar y Emitir Orden en SAP PM"
    Entonces aparece el aviso "Orden ot-XXXX emitida con éxito en ERP. Taller notificado."
    Y la vista "Órdenes de Trabajo" muestra la orden en estado "programada" con su nota, la medición de origen y la ventana
    Y Supabase guarda la orden en ordenes_trabajo, con su medicion_codigo y una fila "creacion" en historial_ordenes
    Y el cupo de la ventana en ventanas_taller baja en 1

  Escenario: La ventana se llenó antes de confirmar (excepción)
    Dado que otro usuario ocupó el último cupo de la ventana elegida
    Cuando el planificador presiona "Confirmar y Emitir Orden en SAP PM"
    Entonces la base rechaza la orden con "La ventana de taller seleccionada no cuenta con cupos libres."
    Y aparece el aviso "No se pudo guardar en Supabase: …"
    Y la orden no queda registrada en ordenes_trabajo
```

---

### HU-08: Modificación y Anulación de OT con Motivo Obligatorio
**Como** planificador de mantención de neumáticos,
**quiero** cambiar la ventana o la nota de una orden programada, o anularla, indicando siempre un motivo,
**para** reasignar o liberar cupos del taller con un historial de cambios auditable.

```gherkin
# language: es
Característica: Modificar o anular una orden (HU-08)

  Escenario: Cambiar la ventana de una orden (camino feliz)
    Dado que la orden "ot-0068" está "programada"
    Cuando el planificador presiona "Modificar" en la orden, elige otra ventana con cupo y escribe el motivo "Postergación por prioridad de mantención de pala"
    Y presiona "Guardar Modificaciones"
    Entonces aparece el aviso "Orden ot-0068 actualizada correctamente"
    Y la ventana nueva tiene un cupo libre menos
    Y el historial de la orden agrega "planificador · modificación de orden · motivo: Postergación por prioridad de mantención de pala"

  Escenario: Anular una orden con motivo (camino feliz)
    Dado que la orden "ot-0067" está "programada"
    Cuando el planificador elige el motivo "El neumático ya se rotó" y confirma con "Sí, anular"
    Entonces la orden queda en estado "anulada" y sigue visible en la lista
    Y el cupo de su ventana se libera
    Y el historial registra "orden anulada · motivo: El neumático ya se rotó"

  Escenario: Guardar sin motivo (excepción)
    Dado que el planificador editó la nota de una orden programada
    Pero dejó vacío el campo "Motivo del Cambio"
    Cuando revisa el formulario
    Entonces ve el mensaje "El motivo del cambio es obligatorio."
    Y el botón "Guardar Modificaciones" está deshabilitado

  Escenario: Anular sin motivo (excepción)
    Dado que el planificador abrió el panel "Anular esta Orden"
    Pero no eligió un "Motivo de Anulación"
    Entonces el botón para anular está deshabilitado
```

---

## Revisión INVEST

| Criterio | Cómo se cumple |
|---|---|
| **Independiente** | Cada historia se puede construir y desplegar por separado. Por ejemplo, HU-01 funciona sin HU-08. |
| **Negociable** | Describe el resultado esperado, no la tecnología. Los umbrales de 200 h y 500 h son parámetros ajustables. |
| **Valiosa** | Cada historia mejora la disponibilidad de la flota, reduce fallas en faena o deja trazabilidad frente al proveedor. |
| **Estimable** | Cada historia toca una pantalla y un conjunto acotado de tablas (ver la matriz). |
| **Pequeña** | Cada historia cabe en un sprint de una a dos semanas. |
| **Testeable** | Cada historia tiene al menos un escenario feliz y uno de excepción con resultados observables en pantalla o en Supabase. |
