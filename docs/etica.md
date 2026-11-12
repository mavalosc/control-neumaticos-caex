# Análisis ético, de sostenibilidad e impacto
## Herramienta predictiva de desgaste de neumáticos CAEX · Equipo 3 · Semana 6 (PROP-08)

> Pregunta de la semana: **¿a quién deja fuera esta automatización?** Este documento deja por escrito qué decidió el equipo y qué decidió no hacer. Se revisa en cada entrega: al probar con usuarios ([`prueba-usuarios.md`](prueba-usuarios.md)), al implementar seguridad y permisos (Semana 10) y al discutir quién sostiene la solución después del curso (Semana 13).
>
> Versión 1 · 12-11-2026 · Responsable: Manuel Ávalos (técnico). Revisión: Héctor Medina (QA).

---

## 1. Mapa de impacto y exclusión

La herramienta automatiza **tareas**, no puestos: el cálculo de horas remanentes, el orden de prioridad del turno y el registro de la orden de trabajo. Lo difícil queda en manos de las personas: las excepciones, el juicio sobre un daño dudoso y la explicación de cada decisión (Bainbridge, 1983).

| Actor | ¿Qué deja de hacer? | ¿Cómo se redefine su rol? | ¿Qué riesgo aparece? | Qué hace el diseño hoy |
|---|---|---|---|---|
| **Planificador de neumáticos** (ejecuta) | Calcular a mano las horas remanentes, ordenar la flota en planillas y transcribir la orden | **Supervisa el modelo**, corrige daños mal clasificados (HU-05), justifica cada orden y responde por ella | **Sesgo de automatización** (Parasuraman y Riley, 1997): aceptar la columna «Modelo» solo porque la entrega el sistema, aunque se entrenó con datos simulados. Pérdida de práctica en la inspección visual | Horas de la fórmula y del modelo en **columnas separadas**, etiqueta *sim*; la orden exige una nota; el daño se corrige como fila nueva validada por humano; desde PROP-08, cada cambio queda con su autor |
| **Operador del pórtico** (ejecuta) | Medir con profundímetro en el taller | Verifica que la pasada se capturó completa | Confiar en una lectura incompleta | Vista Operador con alertas de captura y estado de cada sensor |
| **Jefatura de mantención** (decide) | Consolidar informes a mano | Revisa decisiones con trazabilidad | Ordenar retiros solo por el indicador del modelo, sin criterio de taller | Página Modelos explica límites; umbral de 20 mm declarado como criterio experto y configurable |
| **Despachador de mina** (recibe el aviso) | — | Saca de ciclo un CAEX con daño crítico | El aviso queda solo en el navegador del planificador (ESP-F-03 🟡) | Riesgo **R5** de la matriz |
| **Conductor del CAEX** (queda fuera) | Nada: nunca usa la herramienta | Ninguno, si nadie lo nombra | Los excesos de velocidad y las alertas de presión de **su** camión pueden cruzarse con el turno y usarse para evaluarlo o sancionarlo, sin que sepa que existen esos datos | Datos reales anonimizados por equipo, sin turno ni conductor; **compromiso: no se usan para evaluar personas** (R4) |
| **Técnico del taller** (queda fuera) | Nada: recibe la orden impresa o por ERP | Ejecuta el cambio en la ventana asignada | Concentración de trabajo si muchas órdenes caen en el mismo turno | El cupo lo controla la base (3 por ventana) |
| **Planificador con menos práctica digital, o con daltonismo** (queda fuera) | — | — | Colores rojo/amarillo/verde y pantallas densas pueden dejarlo fuera | Revisión WCAG de la sección 3.3; correcciones en la Semana 9 (R6) |

**Tareas nuevas que alguien debe asumir** (con tiempo y formación, no «se absorben solas»): supervisar lo que sugiere el modelo, cuidar la calidad del dato (corregir daños y mediciones dudosas) y explicar a la jefatura por qué se retiró o no un neumático. En el piloto las asume el planificador; en un despliegue real requieren capacitación y un responsable de la calidad de los datos.

---

## 2. Ficha de tratamiento de datos personales

La herramienta trata **muy pocos datos personales**: el modelo de datos guarda neumáticos, camiones y mediciones, no personas. La excepción nueva es el **email de identificación** (PROP-08).

| Dato | Dónde se guarda | Finalidad (historia) | Quién lo ve | Conservación | Base y derechos |
|---|---|---|---|---|---|
| **Email de quien opera** | `historial_ordenes.autor` (Supabase) | Saber quién emitió, modificó o anuló cada orden (HU-07, HU-08) | **Completo:** solo el equipo del proyecto, desde Supabase. **Abreviado** (`ma***@usach.cl`): cualquier usuario de la app, en el historial de la orden y en Datos | Hasta el **31-12-2026**; ese día se reemplaza por el rol (parte 3 de la migración PROP-08) | Aviso en la pantalla de ingreso antes de entrar. Acceso, rectificación o eliminación: escribir a Manuel Ávalos |
| Email en el navegador | `localStorage` del propio equipo del usuario | No pedirlo en cada visita | Solo esa persona, en ese navegador | Hasta que pulse «cambiar usuario» o borre los datos del navegador | Lo controla el usuario |
| Rol del validador de daños | `danos_neumaticos.usuario_validador` | Distinguir la corrección humana de la clasificación de la IA (HU-05) | Todos los usuarios | Mientras exista el registro | No es dato personal: guarda el rol («planificador»), no la persona |
| **Grabación de la prueba con usuarios** (voz y pantalla) | Drive del curso, **fuera del repositorio**, con acceso restringido | Evidencia de la prueba de usabilidad (PROP-09) | Equipo del proyecto y profesor | Hasta el 31-12-2026 | **Consentimiento** leído y aceptado al inicio de la grabación ([`pauta-validacion.md`](pauta-validacion.md)). Las notas usan códigos (P1), no nombres |
| Alertas TPMS y excesos de velocidad reales | `alertas_tpms`, `eventos_velocidad` | Calibrar el simulador y el modelo de riesgo (PROP-07) | Todos los usuarios | Mientras dure el proyecto | No identifican personas: equipos anonimizados, sin turno ni conductor. **Riesgo de reidentificación** si se cruzaran con la nómina de turnos de la faena: no se hace (R4) |
| Datos técnicos (camiones, neumáticos, mediciones, órdenes) | Supabase | Historias HU-01 a HU-08 | Todos los usuarios | Mientras dure el proyecto | No son datos personales (datos sintéticos de 67 CAEX) |
| Registros técnicos de los proveedores (IP, navegador) | Supabase, Vercel, GitHub | Operación de los servicios | Los proveedores | Según sus políticas | El equipo no los consulta ni los cruza |

**Minimización (privacidad desde el diseño, Cavoukian, 2011):** se pide solo el email, no nombre, RUT ni cargo. Quien prefiera no usar su email personal puede ingresar un código (por ejemplo, `p1@prueba.cl`): el registro sigue siendo trazable dentro de la sesión. La app **no puede leer** el email completo con su clave pública: solo lo ve abreviado a través de `vista_historial_ordenes`.

**Ley 21.719 (vigente desde el 01-12-2026):** la herramienta **no toma decisiones automatizadas sobre personas**. Prioriza neumáticos y sugiere; la decisión de emitir, modificar o anular una orden la toma una persona y queda registrada con su autor.

---

## 3. Sesgo, transparencia y accesibilidad

### 3.1 Sesgos identificados

| Sesgo | Dónde | Efecto | Qué se hace |
|---|---|---|---|
| **Datos simulados** | Modelo de desgaste (PROP-06) | El modelo aprende los supuestos del equipo, no la realidad de la faena | Etiqueta «Modelo entrenado con datos de terreno simulados» en Tablero y Ficha; no reemplaza la fórmula |
| **La ausencia de dato se lee como «sin riesgo»** | Modelo de riesgo con alertas reales (PROP-07) | Un sensor que deja de transmitir no genera alertas y su posición aparece con riesgo bajo | Advertencia en la página Modelos; pendiente mostrar «sin datos recientes» como estado propio (R5) |
| **Más sensores, más presencia en el dato** | Modelo de riesgo | Los equipos con más alertas pesan más; los cargadores tienen pocos datos y otros umbrales | Variable «equipo cargador» separada; resultados por tipo de equipo |
| **Neumáticos sin pasada reciente** | Tablero | Sin medición no hay horas remanentes: quedan en zona gris, al final del orden | Zona gris visible y filtrable; revisar la regla con el planificador en la prueba |
| **Una sola faena** | Calibración (110 psi, umbrales de temperatura) | Puede no representar otras medidas de neumático u otras faenas | Declarado en `respaldo-bibliografico.md` |
| **Importancia no es causalidad** | Causas SHAP | El planificador puede leer una causa como explicación física | Texto «no prueban causalidad» junto a las causas |

### 3.2 Transparencia sobre el uso de IA

- La pantalla de ingreso avisa que la herramienta muestra estimaciones de modelos de aprendizaje automático, algunos entrenados con datos simulados, y que la decisión es de la persona.
- Cada predicción del modelo lleva la marca *sim* o «datos reales»; la página **Modelos** explica cómo se calcula cada cifra y sus límites.
- La **decisión final queda registrada**: quién emitió o cambió la orden, cuándo y con qué motivo (`historial_ordenes`).

### 3.3 Revisión preliminar de accesibilidad (WCAG 2.2, nivel AA)

Revisión del código de las pantallas principales (Ingreso, Tablero, Ficha, Agendar, Órdenes) el 12-11-2026. Es preliminar: falta probar con lector de pantalla y con usuarios.

| Criterio | Estado | Evidencia | Acción |
|---|---|---|---|
| 1.1.1 Texto alternativo | ✅ | Las 5 imágenes de la app tienen `alt` | — |
| 1.4.1 Uso del color | 🟡 | Las zonas llevan texto («Rojo · menos de 200 h»), pero el chasis de Camiones distingue posiciones solo por color | Agregar la zona o las horas en cada posición |
| 1.4.3 Contraste mínimo (4,5:1) | 🟡 | **Tema oscuro ✅**: texto secundario 5,8:1, texto principal 14,8:1. **Tema claro ❌**: textos de estado amarillo 1,7:1, verde 1,9:1 y rojo 2,7:1 sobre blanco | Colores de estado más oscuros en el tema claro (Semana 9) |
| 2.1.1 Teclado | ❌ | 8 elementos clicables son filas o tarjetas (`tr`/`div` con `onclick`) que no reciben foco | Convertirlos en botones o enlaces (Semana 9) |
| 2.4.7 Foco visible | 🟡 | 8 controles quitan el contorno de foco y solo 5 lo reemplazan por un anillo | Anillo de foco en todos los controles |
| 3.1.1 Idioma de la página | ✅ | `lang="es"` | — |
| 3.3.1 y 3.3.2 Errores y etiquetas | ✅ | El ingreso tiene etiqueta, mensaje de error con `role="alert"` y `aria-invalid` | Aplicar el mismo patrón en Agendar y Modificar |
| **3.3.8 Autenticación accesible** (nuevo en 2.2) | ✅ | El ingreso solo pide un email: sin contraseña que memorizar ni captcha | Mantenerlo si en la Semana 10 se agrega autenticación (enlace por correo) |
| 4.1.2 Nombre, función y valor | 🟡 | Botones solo con ícono identificados por `title`; solo 3 tienen `aria-label` | `aria-label` en todos los botones de ícono |

---

## 4. Sostenibilidad

| Plano | Prácticas verificables | Estado |
|---|---|---|
| **Ambiental** | Modelos pequeños (Gradient Boosting en CPU, segundos de entrenamiento); **no se usan modelos de lenguaje** dentro de la app | ✅ |
| | El reentrenamiento corre **una vez al día** (GitHub Actions) y el modelo de riesgo solo cuando llega un Excel nuevo; la app lee las predicciones guardadas, no recalcula | ✅ |
| | La app consulta vistas resumidas (`vista_tablero_turno`, `vista_prediccion_actual`) y carga las tablas grandes solo si el usuario abre la pestaña en Datos | ✅ |
| | Al terminar el curso (31-12-2026) se **desactiva la ejecución diaria** y se borran las ramas y despliegues de prueba | ⏳ R7 |
| **Social** | Mapa de impacto (sección 1), datos reales no usados para evaluar personas, accesibilidad (sección 3.3) | 🟡 |
| **Continuidad** | Responsable técnico: Manuel Ávalos · funcional: Francisco Opazo · QA: Héctor Medina | ✅ |
| | Cuentas: GitHub (`mavalosc`), Supabase y Vercel en planes gratuitos: **costo cero**, pero en cuentas personales | ⚠️ R7 |
| | Proyecto reproducible: `docs/schema.sql`, `docs/seed.sql`, migraciones fechadas, `modelo/requirements.txt` y README | ✅ |

---

## 5. Matriz de riesgos

Probabilidad e impacto: A alto · M medio · B bajo. Todo riesgo tiene responsable y fecha de revisión; aceptar un riesgo también es una decisión.

| ID | Riesgo | P | I | Tratamiento | Responsable | Revisión |
|---|---|---|---|---|---|---|
| R1 | El email de quien opera queda visible para cualquiera con el enlace | A | M | **Mitigar:** la app lo muestra abreviado y la clave pública no puede leer la columna completa (migración PROP-08, parte 2) | Manuel | 21-11-2026 |
| R2 | Cualquiera puede escribir el email de otra persona (no hay verificación) | M | M | **Aceptar** en el prototipo, declarado en la pantalla de ingreso; autenticación con enlace por correo en la Semana 10 | Manuel | Semana 10 |
| R3 | Sesgo de automatización: decidir con la columna «Modelo», entrenada con datos simulados | M | A | **Mitigar:** etiquetas *sim*, nota obligatoria en la orden; se mide en la prueba con usuarios (hipótesis H4) | Nicolás | 21-11-2026 |
| R4 | Uso de los datos de velocidad o presión para evaluar a conductores | B | A | **Evitar:** datos sin turno ni conductor; compromiso escrito de no cruzarlos con nóminas | Héctor | Semana 13 |
| R5 | Una posición sin datos (sensor caído) o un aviso a despacho no guardado se leen como «sin problema» | M | A | **Mitigar:** advertencias en Modelos; pendiente estado «sin datos recientes» y guardar el aviso (ESP-F-03) | Manuel | Semana 9 |
| R6 | Personas que usan teclado, lector de pantalla o tema claro no pueden completar el flujo | M | M | **Mitigar:** correcciones de la sección 3.3 | Manuel | Semana 9 |
| R7 | El proyecto depende de cuentas personales gratuitas y de una ejecución diaria que nadie apaga | M | M | **Aceptar** durante el curso; desactivar la ejecución diaria y decidir el traspaso al cierre | Manuel | 31-12-2026 |
| R8 | La grabación de la prueba expone la voz o datos del voluntario | M | M | **Mitigar:** consentimiento, cámara apagada, Drive restringido, códigos en vez de nombres y eliminación el 31-12-2026 | Nicolás | 21-11-2026 |
| R9 | Los datos reales permiten identificar a la faena | B | A | **Mitigar:** anonimización (PROP-07); confirmar con la faena el uso de los datos | Héctor | Semana 13 |
| R10 | Cualquier persona con el enlace puede emitir o anular órdenes | A | B | **Aceptar** en el prototipo (datos sintéticos); permisos por rol en la Semana 10 (ESP-NF-11) | Manuel | Semana 10 |

---

## Referencias

- Bainbridge, L. (1983). Ironies of automation. *Automatica, 19*(6), 775-779.
- Biblioteca del Congreso Nacional de Chile. (2024). *Ley 21.719 sobre protección y tratamiento de los datos personales*. bcn.cl
- Cavoukian, A. (2011). *Privacidad por diseño: los 7 principios fundamentales*. IPC Ontario.
- Parasuraman, R. y Riley, V. (1997). Humans and automation: Use, misuse, disuse, abuse. *Human Factors, 39*(2), 230-253.
- UNESCO. (2021). *Recomendación sobre la ética de la inteligencia artificial*. unesco.org
- W3C. (2023). *Pautas de accesibilidad para el contenido web (WCAG) 2.2*. w3.org/WAI
