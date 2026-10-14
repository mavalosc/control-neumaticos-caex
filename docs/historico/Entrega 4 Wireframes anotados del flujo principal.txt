# Wireframes anotados del flujo principal

Cuatro pantallas del escenario principal de éxito. Imágenes en [`../img/`](../img/) (`pantalla-1.png` a `pantalla-4.png`) y prototipo navegable en [`../../frontend/index.html`](../../frontend/index.html). Cada pantalla declara su historia, sus datos, el criterio que verifica y su navegación.

## P1 · Tablero del turno (HU-01)
- **Datos que muestra:** `id_camion`, `nivel_dano_camion` (0 a 3), `cantidad_neumaticos_criticos`, `fecha_ultima_pasada`
- **Criterio que verifica:** HU-01, flota ordenada del más grave al menos grave, con nivel y color; «sin medición reciente» si falta la pasada
- **Navegación:** tocar un camión → **P2**

## P2 · Ficha del neumático (HU-02, HU-08)
- **Datos que muestra:** `serial`, `posicion`, `foto_url`, `tipo_dano`, `nivel_dano`, `confianza`, `fecha_pasada`, `modelo_version`, historial de pasadas
- **Criterio que verifica:** HU-02, foto con cada daño marcado y daños de baja confianza como «por confirmar»; HU-08, corrección con autor y fecha
- **Navegación:** «Agendar intervención» → **P3**; «Corregir clasificación» abre el formulario de corrección (camino alternativo, al margen)

## P3 · Agendar intervención (HU-04)
- **Datos que muestra:** `ventana_id`, `dia`, `turno`, `cupos_libres`
- **Criterio que verifica:** HU-04, solo se reserva una ventana con cupos; sin cupos se propone la siguiente
- **Navegación:** «Confirmar» → **P4**

## P4 · Orden emitida (HU-05)
- **Datos que muestra:** `codigo_orden`, `serial`, `posicion`, `ventana`, `fecha_pasada`, `modelo_version`
- **Criterio que verifica:** HU-05, código de orden, vínculo a la medición y a la versión del modelo; si el ERP rechaza, se muestra el motivo y la orden queda pendiente
- **Navegación:** «Volver al tablero» → **P1**

## Camino alternativo (alerta crítica, HU-03)
Cuando un neumático queda en nivel 3, la alerta llega al despachador y al planificador y lleva directo a la ficha de **P2**. Se anota al margen y no se dibuja como pantalla aparte.

## Pantallas actuales de la interfaz
Capturas de la interfaz construida, que alimentan las historias de [`../historias-frontend.md`](../historias-frontend.md).

| Pantalla | Historias | Navegación |
|---|---|---|
| Tablero del turno ([captura](../img/ui-tablero.jpg)) | HU-F01, HU-F02, HU-F06 | Clic en una fila → ficha del neumático |
| Camiones ([captura](../img/ui-camiones.jpg)) | HU-F03, HU-F06 | Clic en una posición → ficha del neumático |
| Órdenes de trabajo ([captura](../img/ui-ordenes.jpg)) | HU-F07, HU-F08 | Clic en el serial → ficha del neumático |

### Pantalla nueva: Modificar o anular una orden
Se abre desde el botón «Modificar o anular» de cada orden programada (HU-F09, HU-F10).
- **Datos que muestra:** `codigo_orden`, `serial`, `ventana_actual`, ventanas con `cupos_libres`, `nota`, `motivo`, `historial`
- **Criterio que verifica:** el motivo es obligatorio; la anulación pide confirmación; la orden anulada se conserva con su motivo
- **Navegación:** «Guardar cambios» o «Sí, anular» → Órdenes de trabajo con un aviso de confirmación; «Volver» → Órdenes sin cambios
