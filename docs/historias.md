# Historias de Usuario y Criterios de Aceptación (BDD / Gherkin)
## Proyecto: Pórtico Dimensional Predictivo de Neumáticos CAEX
### Ingeniería Digital en Acción (Ecosistema DSD - USACH) · Unidad 1 · Equipo 3

> **Estándar Metodológico:** Formulado bajo principios **INVEST** (Independiente, Negociable, Valiosa, Estimable, Pequeña, Testeable) con criterios de aceptación en sintaxis **BDD / Gherkin** (`Dado`, `Cuando`, `Entonces`). Vinculado con el Roadmap de Notion mediante códigos `HU-XX` y wireframes anotados en Figma (Pantallas P1 a P5).

---

## Matriz de Trazabilidad de Historias de Usuario

| Código | Historia de Usuario | Rol Primario | Pantalla Figma | Horizonte Notion | Estado Código |
|---|---|---|---|---|---|
| **HU-01** | Tablero de Turno y Priorización por Horas Remanentes | Planificador | P1 (Tablero) | Ahora | Implementado |
| **HU-02** | Alerta Inmediata de Daño Crítico y Desvío a Despacho | Despachador / Planificador | P1 (Alerta) | Ahora / Próximo | Implementado |
| **HU-03** | Visualización Matricial de Flota y Chasis 6x4 | Planificador | P2 (Camiones) | Ahora | Implementado |
| **HU-04** | Ficha Técnica, Escáner 3D y Curva de Desgaste | Planificador | P3 (Ficha) | Ahora | Implementado |
| **HU-05** | Validación y Reclasificación de Daños (Humano en el Bucle) | Planificador | P3 (Ficha) | Próximo | Implementado |
| **HU-06** | Agendamiento en Ventana de Taller con Control de Cupos | Planificador | P4 (Agendar) | Ahora | Implementado |
| **HU-07** | Emisión de Orden de Trabajo y Trazabilidad ERP / SAP PM | Planificador | P5 (Órdenes) | Ahora | Implementado |
| **HU-08** | Modificación y Anulación de OT con Motivo Obligatorio | Planificador | P5 (Modal OT) | Próximo | Implementado |

---

## Especificación Detallada de Historias de Usuario

### HU-01: Tablero de Turno y Priorización por Horas Remanentes
**Como** Planificador de Mantención de Neumáticos,  
**quiero** visualizar al inicio de cada turno la lista completa de neumáticos montados en la flota ordenada de menor a mayor horas de vida útil remanente y clasificada por semáforo de criticidad,  
**para** priorizar inmediatamente las intervenciones más urgentes sin tener que inspeccionar camión por camión manualmente.

#### Criterios de Aceptación (BDD / Gherkin):

```gherkin
Escenario: Visualización y ordenamiento descendente de criticidad en el tablero (Camino Feliz)
  Dado que existen mediciones procesadas para los 67 camiones CAEX-101 a CAEX-167
  Cuando el planificador ingresa a la vista del "Tablero del turno"
  Entonces el sistema muestra las tarjetas KPI de resumen:
    | Zona      | Condición           |
    | Rojo      | < 200 h remanentes  |
    | Amarillo  | < 500 h remanentes  |
    | Verde     | > 500 h remanentes  |
    | Sin datos | 0 lecturas previas  |
  Y la tabla lista todos los neumáticos ordenados ascendentemente por horas remanentes
  Y cada fila muestra: Camión, Posición, Serial, Profundidad (mm), Tasa (mm/100h), Horas remanentes, Zona y Nivel de daño.

Escenario: Filtrado combinado por zona y búsqueda de texto
  Dado que el planificador se encuentra en el "Tablero del turno"
  Cuando selecciona el filtro de zona "rojo" y escribe "CAEX-102" en el buscador
  Entonces la tabla se actualiza mostrando únicamente los neumáticos del CAEX-102 con horas remanentes inferiores a 200 h
  Y se ocultan las filas pertenecientes a zonas amarilla o verde.

Escenario Alternativo: Búsqueda sin coincidencias en el turno
  Dado que el planificador ingresa un serial inexistente "5980R63-9999-9999" en el buscador
  Cuando el sistema ejecuta el filtro en tiempo real
  Entonces la tabla muestra el mensaje "Sin resultados. Limpia los filtros."
  Y el contador de registros visibles indica 0.
```

---

### HU-02: Alerta Inmediata de Daño Crítico y Desvío a Despacho
**Como** Despachador de Mina / Planificador de Mantención,  
**quiero** recibir una alerta visual prioritaria en el sistema cuando un neumático sea detectado con Daño Nivel 3 (corte profundo, sobrecalentamiento >95°C o riesgo de delaminación),  
**para** desviar inmediatamente el camión del circuito de acarreo hacia el taller antes de que ocurra un reventón catastrófico en la rampa.

#### Criterios de Aceptación (BDD / Gherkin):

```gherkin
Escenario: Detección de daño crítico y despliegue de banner prioritario (Camino Feliz)
  Dado que el neumático serial "5980R63-2426-1348" en CAEX-102 posición P3 registra daño Nivel 3
  Cuando el planificador o despachador abre el tablero principal
  Entonces el sistema despliega un banner superior de alta prioridad con borde rojo y animación destacada
  Y el mensaje indica: "Alerta de daño crítico · CAEX-102, posición 3: corte profundo en flanco. Sacar el CAEX del ciclo."
  Y el botón "Avisar Despacho Mina" queda habilitado para registrar la derivación radial.

Escenario: Confirmación de derivación a Despacho Mina
  Dado que el banner de alerta crítica está visible en pantalla
  Cuando el usuario presiona el botón "Avisar Despacho Mina"
  Entonces se genera un registro en el log de auditoría con fecha, hora, ID del camión y serial
  Y se muestra una notificación toast confirmando el aviso de desvío
  Y el estado del camión en el sistema pasa a "En derivación a taller".

Escenario Alternativo: Ausencia de daños críticos en la flota
  Dado que todos los neumáticos monitoreados poseen Nivel de Daño 0, 1 o 2
  Cuando se carga el tablero del turno
  Entonces el banner de alerta crítica permanece oculto y la interfaz muestra el estado "Operación Normal".
```

---

### HU-03: Visualización Matricial de Flota y Chasis 6x4
**Como** Planificador de Mantención de Neumáticos,  
**quiero** consultar una vista esquemática de la flota que represente el chasis de cada camión con sus 6 posiciones de neumáticos (P1 a P6),  
**para** analizar visualmente el desgaste cruzado por eje y definir rotaciones oportunas entre ruedas delanteras y traseras duales.

#### Criterios de Aceptación (BDD / Gherkin):

```gherkin
Escenario: Inspección de chasis 6x4 por camión CAEX (Camino Feliz)
  Dado que el planificador navega a la vista "Camiones"
  Cuando se renderizan las tarjetas de flota
  Entonces cada CAEX muestra:
    | Identificador | Modelo       | Horómetro   | Neumáticos en Rojo |
    | CAEX-101      | Cat 793F     | 16.791 h    | Cantidad en rojo   |
  Y una matriz esquemática del camión con 6 tarjetas:
    - Eje delantero: P1 (Delantero Izq), P2 (Delantero Der)
    - Tándem trasero dual: P3 (Ext Izq), P4 (Int Izq), P5 (Int Der), P6 (Ext Der)
  Y cada posición muestra sus horas remanentes coloreadas según su zona (verde, amarillo, rojo).

Escenario: Navegación directa desde una posición del camión a la ficha técnica
  Dado que el camión CAEX-102 muestra la posición P3 en color rojo con 34 h
  Cuando el planificador hace clic sobre la tarjeta de la posición P3
  Entonces el sistema navega a la URL "#/n/5980R63-2426-1348" abriendo la ficha técnica del neumático.

Escenario Alternativo: Camión con neumáticos sin lecturas previas
  Dado que el camión CAEX-104 tiene una posición sin historial dimensional
  Cuando se dibuja el camión en la vista matricial
  Entonces esa posición se muestra con estilo neutro "sin datos"
  Y al hacer clic en ella permite registrar o simular la primera pasada de pórtico.
```

---

### HU-04: Ficha Técnica, Escáner 3D y Curva de Desgaste
**Como** Planificador de Mantención de Neumáticos,  
**quiero** acceder a la ficha técnica individual del neumático para ver la nube de puntos/foto con daños delimitados, la termografía de flanco y la curva histórica de degradación frente al umbral de retiro,  
**para** sustentar con evidencia objetiva la orden de retiro y contar con respaldo técnico ante el fabricante (Michelin, Bridgestone o BKT).

#### Criterios de Aceptación (BDD / Gherkin):

```gherkin
Escenario: Consulta de ficha técnica con curva de desgaste (Camino Feliz)
  Dado que el planificador abre la ficha del neumático "5980R63-2426-1348"
  Cuando se renderiza la vista técnica
  Entonces se muestran las tarjetas métricas:
    - Horas remanentes calculadas
    - Profundidad de banda actual en mm contra el umbral crítico de 20,0 mm
    - Tasa de desgaste observada (mm / 100 h)
    - Temperatura de flanco en °C
  Y un gráfico SVG temporal con las últimas 8 pasadas y la línea horizontal punteada de umbral de retiro en 20,0 mm
  Y el panel de escáner 3D muestra el bounding box del daño con porcentaje de certeza (ej. "corte profundo en flanco 94%").

Escenario Alternativo: Daño detectado con baja confianza algorítmica
  Dado que el escáner detecta una irregularidad con confianza inferior al 70% (0.70)
  Cuando se presenta la información en la tarjeta de daños
  Entonces el daño se rotula explícitamente como "por confirmar"
  Y el botón "Agendar intervención" solicita confirmación visual antes de proceder.
```

---

### HU-05: Validación y Reclasificación de Daños (Humano en el Bucle)
**Como** Planificador de Mantención de Neumáticos (Ecosistema Industria 5.0),  
**quiero** corregir manualmente el nivel de severidad o el tipo de daño asignado por el modelo de visión artificial,  
**para** que el juicio experto humano prevalezca sobre la inferencia de la máquina y se genere un registro auditable para reentrenamiento del modelo.

#### Criterios de Aceptación (BDD / Gherkin):

```gherkin
Escenario: Reclasificación exitosa de daño por el planificador (Camino Feliz)
  Dado que la ficha de un neumático indica Nivel 1 (Leve) por inferencia automática
  Cuando el planificador selecciona la píldora "2 · Moderado" en el panel "Corregir clasificación"
  Entonces el nivel de daño del neumático se actualiza inmediatamente a Nivel 2
  Y el badge en la ficha cambia a color naranja
  Y el sistema registra en la base de datos la fecha, hora y rol del usuario que efectuó el ajuste
  Y el camión asociado actualiza su nivel máximo de severidad.

Escenario Alternativo: Reclasificación a Nivel 0 (Falso Positivo)
  Dado que una mancha de lodo fue catalogada erróneamente por la IA como roca incrustada (Nivel 2)
  Cuando el planificador presiona "0 · Sin daño"
  Entonces se eliminan los bounding boxes de daño activo
  Y la condición pasa a estado normal, liberando la sugerencia de intervención obligatoria.
```

---

### HU-06: Agendamiento en Ventana de Taller con Control de Cupos
**Como** Planificador de Mantención de Neumáticos,  
**quiero** seleccionar una ventana de taller disponible (turnos A o B) que cuente con cupos libres y verificar si la intervención se ejecutará antes de que el neumático cruce el umbral de falla,  
**para** asegurar la capacidad del taller y evitar que el neumático falle en faena antes de ingresar al servicio.

#### Criterios de Aceptación (BDD / Gherkin):

```gherkin
Escenario: Reserva de ventana con cupo disponible y margen de horas favorable (Camino Feliz)
  Dado que el neumático tiene 150 h remanentes de vida útil
  Y la ventana "29-09-2026, turno B" está proyectada para dentro de 36 h con 2 de 3 cupos libres
  Cuando el planificador selecciona dicha ventana en la pantalla "Agendar intervención"
  Entonces el sistema resalta la opción seleccionada con borde distintivo
  Y muestra el mensaje de validación: "La ventana elegida cae dentro del margen (quedan 114 h de margen de seguridad)"
  Y el botón "Confirmar y emitir orden" queda habilitado.

Escenario Alternativo: Ventana con capacidad de cupos agotada
  Dado que una ventana de taller tiene 0 de 3 cupos libres
  Cuando se renderiza la lista de ventanas en la vista de agendamiento
  Entonces la tarjeta de esa ventana se muestra deshabilitada (opacidad reducida)
  Y no permite ser seleccionada para emisión de orden.

Escenario de Advertencia: Ventana posterior al punto probable de falla
  Dado que un neumático tiene 34 h remanentes
  Cuando el planificador selecciona una ventana programada para dentro de 56 h
  Entonces el sistema muestra una advertencia en color rojo: "La ventana llega tarde: el neumático cruza el umbral antes"
  Y recomienda seleccionar la ventana más inmediata.
```

---

### HU-07: Emisión de Orden de Trabajo y Trazabilidad ERP / SAP PM
**Como** Planificador de Mantención de Neumáticos,  
**quiero** que al confirmar la reserva se genere automáticamente la Orden de Trabajo (OT) con trazabilidad a la medición dimensional, versión del modelo y serial de reemplazo de bodega,  
**para** enviar el trabajo al taller y contar con respaldo inmutable para la reunión semanal y el reclamo de garantía ante el proveedor.

#### Criterios de Aceptación (BDD / Gherkin):

```gherkin
Escenario: Emisión de orden de trabajo con trazabilidad completa (Camino Feliz)
  Dado que el planificador presiona "Confirmar y emitir orden" para el serial "5980R63-2531-1596"
  Cuando el sistema procesa la solicitud
  Entonces se crea una nueva OT con correlativo único (ej. "ot-0069")
  Y el cupo libre de la ventana seleccionada se decrementa en 1 (ej. de 2 a 1)
  Y la orden almacena:
    - Serial montado y posición en el CAEX
    - Tipo de intervención ("retiro" o "rotación")
    - Medición de origen (ej. "med-2496, 22,9 mm, tasa observada")
    - Serial de bodega asignado para reemplazo ("5980R63-B-544")
    - Versión del modelo predictivo ("v1.3")
    - Estado inicial: "programada"
  Y el usuario es redirigido a la vista de Órdenes con una notificación de confirmación.

Escenario Alternativo: Visualización y filtro en el listado de órdenes
  Dado que existen órdenes en estados "programada", "ejecutada" y "anulada"
  Cuando el usuario filtra por estado "programada"
  Entonces el listado muestra únicamente las órdenes pendientes con el botón "Modificar o anular" habilitado.
```

---

### HU-08: Modificación y Anulación de OT con Motivo Obligatorio
**Como** Planificador de Mantención de Neumáticos,  
**quiero** tener la capacidad de cambiar la ventana, editar la nota o anular una Orden de Trabajo en estado programada exigiendo un motivo mandatorio,  
**para** reasignar o liberar cupos del taller garantizando una auditoría inalterable del historial de cambios.

#### Criterios de Aceptación (BDD / Gherkin):

```gherkin
Escenario: Modificación de ventana de taller y justificación obligatoria (Camino Feliz)
  Dado que la orden "ot-0068" está en estado "programada"
  Cuando el planificador presiona "Modificar o anular"
  Y selecciona una nueva ventana con cupo disponible
  Y escribe el motivo: "Postergación por prioridad de mantención de pala"
  Y presiona "Guardar cambios"
  Entonces la orden actualiza su fecha y turno
  Y el cupo de la ventana anterior se incrementa en +1
  Y el cupo de la nueva ventana se decrementa en -1
  Y el historial de la orden anexa: "[Fecha Hora] · planificador · ventana modificada · motivo: Postergación por prioridad..."

Escenario: Anulación de orden con motivo y liberación de cupo
  Dado que el planificador selecciona la orden programada "ot-0067"
  Cuando hace clic en "Anular orden", elige el motivo "El neumático ya se rotó" y confirma la anulación
  Entonces la orden cambia su estado a "anulada" (sin borrarse de la base de datos)
  Y el cupo del taller asociado se libera automáticamente (+1)
  Y el motivo queda registrado de forma permanente en el historial de trazabilidad.

Escenario Excepción: Intento de guardar cambios sin motivo obligatorio
  Dado que el planificador cambia la nota de la orden
  Pero deja el campo "Motivo del cambio" en blanco
  Cuando evalúa la interfaz
  Entonces el botón "Guardar cambios" permanece deshabilitado (disabled)
  Y el sistema impide el envío hasta que se ingrese un texto válido.
```

---

## Criterios de Revisión INVEST Aplicados

1. **Independent (Independientes):** Las historias pueden desarrollarse y desplegarse de manera incremental (ej. HU-01 Tablero puede operar antes de HU-08 Modificación de OT).
2. **Negotiable (Negociables):** Las interfaces y umbrales (200h, 500h) están parametrizados y son ajustables según el feedback del cliente minero.
3. **Valuable (Valiosas):** Cada historia entrega valor directo en disponibilidad de flota, reducción de costos de neumáticos o trazabilidad frente a proveedores (US$40M en juego).
4. **Estimable (Estimables):** Cada historia tiene fronteras técnicas acotadas a las tablas de datos y componentes visuales correspondientes.
5. **Small (Pequeñas):** Cada historia corresponde a un flujo de interacción de una pantalla o modal específico dentro de un sprint de 1 a 2 semanas.
6. **Testable (Testeables):** Todas cuentan con escenarios en sintaxis Gherkin verificables mediante pruebas unitarias y de integración end-to-end.
