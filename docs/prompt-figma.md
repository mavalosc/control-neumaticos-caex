# Maqueta preliminar y wireframe anotado: idea de diseño y prompt para Figma

## Idea y diseño

**Concepto.** Mantener la interfaz que ya existe (tablero, camiones, órdenes), clara y sobria, y sumarle una segunda señal: el nivel de daño que detecta la foto, junto a las horas de vida útil. El planificador debe ver de un vistazo qué neumático está mal por desgaste y cuál por daño.

### Las 5 pantallas

| # | Pantalla | Qué resuelve | Historias |
|---|---|---|---|
| P1 | Tablero del turno | Flota ordenada por riesgo, con alerta crítica | HU-F01, F02, F06 |
| P2 | Camiones | Seis posiciones por CAEX con zona y nivel | HU-F03, F06 |
| P3 | Ficha del neumático | Foto con daños marcados, historia y corrección | HU-F04, F05 |
| P4 | Agendar intervención | Ventanas del taller | HU-04 (generales) |
| P5 | Órdenes de trabajo | Estado, tipo y trazabilidad hasta la evidencia | HU-F07, F08 |

Flujo: P1 o P2 → P3 → P4 → P5.

### Lenguaje visual
- Fondo gris muy claro, tarjetas blancas con borde fino y esquinas redondeadas.
- Zonas en colores apagados (rojo ladrillo, ámbar, verde salvia, gris para «sin datos»), siempre con el nombre de la zona al lado.
- Filtro activo como píldora durazno con borde naranja.
- Nivel de daño como insignia con número y nombre (0 · Sin daño, 1 · Leve, 2 · Moderado, 3 · Crítico), legible sin depender del color.
- Foto en una tarjeta propia, con cuadros de color sobre cada daño y su porcentaje de confianza.

### Decisiones
- La alerta crítica va arriba del tablero y lleva directo a la ficha.
- Un neumático en zona verde con daño nivel 3 sube al primer lugar.
- Las notas largas de las órdenes se muestran resumidas y se expanden al hacer clic.

> **Ojo:** la columna «Daño» y la foto son mejoras propuestas y no existen en las capturas actuales (`img/ui-*.jpg`). Si la maqueta debe mostrar solo lo ya construido, quítalas de P1, P2 y P3 y deja P1, P2 y P5 como en las capturas.

## Prompt para Figma Make

Adjuntar las tres capturas de `docs/img/` como referencia visual.

```
Crea la maqueta preliminar de una aplicación web de escritorio (1440 x 900 px) llamada "Control de neumáticos CAEX", para planificadores de mantención de neumáticos en minería a cielo abierto. El sistema fotografía los neumáticos de camiones mineros (CAEX), detecta daños (cortes, rajaduras, rocas incrustadas, desgaste irregular), proyecta las horas de vida útil remanente y permite agendar la intervención en el taller.

ESTILO VISUAL (basado en las capturas adjuntas)
- Fondo gris muy claro, tarjetas blancas con borde fino y esquinas redondeadas de 8 px, tipografía sans-serif limpia, mucho espacio en blanco.
- Zonas de vida útil: rojo ladrillo (menos de 200 h), ámbar (menos de 500 h), verde salvia (más de 500 h), gris (sin datos). Escribe siempre el nombre de la zona junto al color.
- Nivel de daño como insignia con número y nombre: 0 · Sin daño, 1 · Leve, 2 · Moderado, 3 · Crítico. El nivel 3 usa rojo intenso.
- Filtros como píldoras; la activa tiene relleno durazno y borde naranja.
- Barra superior con el nombre de la app y la navegación: Tablero, Camiones, Órdenes.

PANTALLAS (cinco frames, todos con el mismo encabezado)

P1 · Tablero del turno
- Título "Tablero del turno" y subtítulo "La flota ordenada por horas de vida útil remanente. Una fila es un neumático montado; se abre con un clic."
- Alerta destacada arriba, borde rojo: "Alerta de daño crítico · CAEX-102, posición 3: corte profundo en flanco. Sacar el CAEX del ciclo."
- Cuatro tarjetas de resumen: Rojo 6 (menos de 200 horas: programar el retiro ahora), Amarillo 3 (menos de 500 horas: entra a la próxima ventana), Verde 27 (más de 500 horas), Sin datos 0.
- Buscador "buscar por serial, camión, modelo o zona", filtros de zona (todas, rojo, amarillo, verde, sin datos) y de tasa (cualquier tasa, observada, nominal).
- Tabla con columnas: Camión, Pos., Serial, Profundidad, Tasa reciente, Tasa según, Horas remanentes, Zona, Daño, Última medición. Filas en rojo claro, de menor a mayor horas:
  CAEX-102 · 3 · 5980R63-2426-1348 · 20,4 mm · 1,17 mm/100 h · observada · 34 h · rojo · 3 Crítico · 24-09-2026
  CAEX-106 · 2 · 5980R63-2328-1590 · 21,7 mm · 1,79 mm/100 h · observada · 95 h · rojo · 1 Leve · 21-09-2026
  CAEX-105 · 5 · 5980R63-2345-1534 · 21,2 mm · 1,14 mm/100 h · observada · 106 h · rojo · 0 Sin daño · 20-09-2026
  CAEX-106 · 5 · 5980R63-2618-1611 · 22,3 mm · 1,61 mm/100 h · observada · 143 h · rojo · 0 Sin daño · 21-09-2026
  CAEX-106 · 4 · 5980R63-2531-1596 · 22,9 mm · 1,94 mm/100 h · observada · 150 h · rojo · 2 Moderado · 21-09-2026
  y dos filas ámbar.

P2 · Camiones
- Título "Camiones", subtítulo "Seis posiciones por CAEX. Cada posición abre la ficha del neumático que lleva montado."
- Buscador y una tarjeta por camión: CAEX-101 (Cat 793F, horómetro 16.791 h), CAEX-102 (Cat 793F, 13.622 h, "1 en rojo"), CAEX-103 (Komatsu 930E-4, 21.087 h).
- Cada tarjeta muestra seis recuadros P1 a P6 en dos filas de tres, coloreados por zona, con las horas remanentes y una insignia pequeña con el nivel de daño. La tarjeta lleva además el nivel del camión, que es el de su neumático más grave.
- Ejemplo: CAEX-102 con P3 en rojo (34 h, nivel 3) y P6 en ámbar (441 h).

P3 · Ficha del neumático
- Encabezado: serial 5980R63-2426-1348, CAEX-102 · posición 3 · pasada 24-09-2026 · modelo v1.3, con la insignia de nivel de daño.
- Fila de seis pestañas P1 a P6 para cambiar de posición.
- Tarjeta con una foto de ejemplo del neumático (imagen gris con marcador de posición) y cuadros de color sobre los daños, con el tipo y el porcentaje de confianza. Rótulo: "Imagen de ejemplo".
- Tarjeta "Daños detectados": tipo, nivel, confianza; un daño de baja confianza aparece como "por confirmar".
- Gráfico de línea "profundidad remanente por pasada" con línea punteada de umbral de retiro (20 mm) y recuadro "Proyección: 34 horas remanentes · tasa 1,17 mm por cada 100 h".
- Tarjeta "Corregir clasificación" con cuatro píldoras de nivel 0 a 3.
- Botón principal oscuro "Agendar intervención" y botón secundario "Registrar medición".

P4 · Agendar intervención
- Título "Agendar 5980R63-2426-1348".
- Tres tarjetas de ventana, una seleccionable con borde azul: Jueves 25 turno noche (2 de 3 cupos), Viernes 26 turno día (1 de 3), Sábado 27 turno noche (3 de 3).
- Tarjeta de aviso: "Daño crítico: conviene la ventana más próxima."
- Botón "Confirmar".

P5 · Órdenes de trabajo
- Título "Órdenes de trabajo", subtítulo "Cada orden conserva la medición y la proyección que la originaron: esa es la traza que sirve frente al taller y frente al proveedor."
- Tarjetas: Programada 5, Ejecutada 55, Anulada 8.
- Buscador, filtros de estado y de tipo (retiro, rotación, inspección).
- Tabla: Orden, Neumático, Intervención y nota (resumida, con "ver más"), Programada, Horas al emitir, Origen, Estado. Fila de ejemplo: ot-0068, 26-09-2026 10:59 · 5980R63-2531-1596, CAEX-106 P4 · retiro · 29-09-2026, turno A 08:00 a 12:00 · 150 h · med-2494, 22,9 mm, tasa observada · programada.
- Panel lateral al abrir una orden: medición de origen, proyección y la foto con los daños del momento.

NAVEGACIÓN
- Clic en una fila del tablero o en una posición del camión abre P3. "Agendar intervención" lleva a P4. "Confirmar" lleva a P5 con la nueva orden al inicio.

SEGUNDA PÁGINA: WIREFRAME ANOTADO
Duplica los cinco frames en una página llamada "Wireframe anotado" en escala de grises. Junto a cada pantalla agrega cuatro anotaciones numeradas: 1) historia de origen (por ejemplo HU-F01), 2) datos que muestra (nombres de campo como serial, nivel_dano, horas_remanentes), 3) criterio de aceptación que verifica, 4) a qué pantalla lleva cada acción, con flechas.

Usa datos realistas, no texto de relleno. Todo en español.
```
