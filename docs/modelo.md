# Modelo de desgaste y vida útil remanente (RUL)
## Pórtico Dimensional Predictivo de Neumáticos CAEX · Equipo 3 · PoC Semana 8 (META-01)

> **Estado:** prueba de concepto con **datos sintéticos**. Los resultados validan el **método**, no el desempeño en faena. La validación con datos reales es la tarjeta META-01 del Roadmap (horizonte *Después*).
> **Código:** [`modelo/generar_datos.py`](../modelo/generar_datos.py) y [`modelo/entrenar.py`](../modelo/entrenar.py) · **Resultados:** [`modelo/resultados/REPORTE.md`](../modelo/resultados/REPORTE.md)

---

## 1. Objetivo

1. Identificar qué variables operacionales tienen mayor influencia en la **tasa de desgaste** y en el **riesgo de falla prematura** de un neumático OTR.
2. Predecir las **horas de vida útil remanente** con un error menor que el del método actual (recta de profundidad vs horas, `backend/app/proyeccion.py`), con la meta de anticipar el retiro en **al menos 200 h**. Esa meta es un **requisito propuesto** de planificación (META-01), sin respaldo directo en la literatura revisada ([respaldo bibliográfico](respaldo-bibliografico.md)).
3. Entregar al planificador la **razón** de cada alerta (explicabilidad, Roadmap *Próximo*: «que el planificador vea por qué el modelo puso un neumático en rojo»).

## 2. Variables y fuentes de datos

El pórtico solo mide profundidad, daños y temperatura. El resto de las variables viene de otros sistemas de la faena y se agrega por **ciclo de operación entre dos pasadas** por el pórtico.

| # | Variable | Unidad | Fuente en faena | Rol esperado |
|---|---|---|---|---|
| 1 | Presión de inflado | % vs nominal | Monitoreo de presión de neumáticos (TPMS) | Causa |
| 2 | Temperatura del neumático | °C | Pórtico (termografía) o TPMS | **Consecuencia** de carga, presión y clima |
| 3 | Nivel de desgaste (profundidad) | mm | Pórtico (escáner 3D) | Estado |
| 4 | Carga transportada | t | Sistema de pesaje del CAEX | Causa (vía TKPH) |
| 5 | Velocidad de operación | km/h | Gestión de flota / despacho (GPS) | Causa (vía TKPH) |
| 6 | Distancia recorrida | km | Gestión de flota / despacho | Exposición |
| 7 | Horas de uso | h | Horómetro del CAEX | Exposición |
| 8 | Condiciones del terreno | categoría | Plan minero por fase (roca suelta, compactado, barro) | Causa |
| 9 | Pendiente de la ruta | % | GPS cruzado con topografía | Causa |
| 10 | Posición en el equipo | P1 a P6 | Registro de montaje | Causa (direccionales delanteros) |
| 11 | Frenadas y aceleraciones fuertes | eventos/h | Telemetría del CAEX | Causa |
| 12 | Temperatura ambiente | °C | Estación meteorológica | Causa menor |

### Indicador derivado: TKPH
Las variables 4, 5 y 6 están fuertemente correlacionadas. La industria las resume en el **TKPH** (toneladas-kilómetro por hora): carga media por neumático × velocidad media del turno. Es el indicador con que los fabricantes dimensionan neumáticos de minería. El modelo usa el TKPH junto con las variables originales.

## 3. Dos formas de terminar la vida de un neumático

| Fin de vida | Ejemplo | Modelo | Por qué separarlos |
|---|---|---|---|
| **Desgaste** | La banda llega al umbral de 20 mm | Regresión de la tasa (mm/100 h) | Es gradual y medible en cada pasada |
| **Daño** | Corte, impacto, separación (~30 % de las fallas en la operación estudiada por Lindeque, 2016) | Supervivencia (Cox) | Es un evento súbito; muchas vidas terminan por retiro o siguen montadas (**censura**) |

Mezclar ambos en una sola cifra de RUL distorsiona los dos.

## 4. Método

```
Datos por ciclo entre pasadas (pórtico + TPMS + pesaje + despacho + GPS)
        │  ventanas de ~200 h (4 pasadas) para que el ruido del pórtico (±0,25 mm) no domine
        ▼
Indicadores derivados (TKPH, presión bajo/sobre nominal, % de terreno, posición)
        │
        ├──► Desgaste (a): regresión multivariable sobre log(tasa) → efecto % de cada variable
        ├──► Desgaste (b): Gradient Boosting sobre las 12 variables → predicción + importancia SHAP
        └──► Daño: modelo de Cox con censura → razón de riesgo (HR) de cada factor
        │
        ▼
Horas remanentes = (profundidad actual − 20 mm) / tasa prevista × 100
        │
        ▼
Tablero (HU-01), motivo de la alerta (SHAP) y agendamiento (HU-06)
```

**Respecto de la propuesta inicial** (Deep Learning → coeficientes → regresión):
- Se parte con modelos **interpretables y con pocos datos**: regresión y Gradient Boosting. Una red profunda necesita miles de vidas de neumático; una flota de 67 CAEX genera unas 400 al año.
- La **importancia de cada variable** se obtiene con **SHAP** sobre el modelo, en lugar de pasar salidas de una red a una segunda regresión. Encadenar modelos de esa forma filtra información entre etapas y sobreestima el desempeño.
- Deep Learning (por ejemplo, una LSTM sobre la serie de pasadas) queda como **mejora futura** si el Gradient Boosting se queda corto con datos reales.

## 5. Validación con datos sintéticos

El simulador genera 1.610 vidas de neumático en 67 CAEX durante unas 12.000 h, con **efectos conocidos** sobre el desgaste y el daño. Así se puede comprobar si el método **recupera la verdad** antes de usar datos reales. Incluye a propósito tres trampas reales:
- efectos **no lineales**: la pendiente pesa el doble sobre 6 %, y la presión baja daña más con TKPH alto;
- la temperatura del neumático como **consecuencia**, no como causa;
- **cambios de fase** de cada camión cada ~1.500 h, que modifican las condiciones a mitad de la vida del neumático.

**Separación:** 14 camiones completos se reservan para prueba; el modelo nunca los ve al entrenar.

### Resultados (ejecución del 18-10-2026, semilla 2026)

**Tasa de desgaste** (error absoluto medio en camiones no vistos):

| Modelo | MAE (mm/100 h) |
|---|---|
| Promedio de flota | 0,401 |
| Regresión multivariable | 0,102 |
| **Gradient Boosting** | **0,080** |

**Horas remanentes frente al método actual** (167 neumáticos de prueba que terminaron por desgaste).

> **Cómo leer «dentro de ±200 h»:** mide el **error de la estimación** de horas remanentes. **No demuestra** que el modelo anticipe una falla con 200 h de antelación (meta META-01); eso requiere validarlo con fallas reales.

| Punto de evaluación | Método actual (recta) | Modelo | |
|---|---|---|---|
| A 45 mm | error 363 h · 32 % dentro de ±200 h | error **180 h** · **63 %** dentro de ±200 h | |
| A 30 mm | error 222 h · 49 % dentro de ±200 h | error **65 h** · **95 %** dentro de ±200 h | |
| Estimaciones **optimistas** a 30 mm (más de 200 h de vida extra) | 27,5 % | **3,0 %** | El error peligroso: retirar tarde |

**Efectos recuperados por la regresión** (selección; tabla completa en el reporte):

| Variable | Verdadero | Estimado | Lectura |
|---|---|---|---|
| Terreno roca suelta | +30,0 % | +29,6 % | ✅ |
| Posición delantera | +15,0 % | +14,9 % | ✅ |
| TKPH (+10 %) | +5,9 % | +5,7 % | ✅ |
| Frenadas fuertes (por evento/h) | +2,0 % | +2,2 % | ✅ |
| Presión bajo nominal (por 1 %) | +1,5 % | +2,5 % | ⚠️ Absorbe la interacción con TKPH (no lineal) |
| Pendiente (por punto) | +3,0 % | +4,6 % | ⚠️ Absorbe el efecto extra sobre 6 % (no lineal) |
| Temperatura del neumático | 0 % (es consecuencia) | +0,6 % | ⚠️ Correlación, no causa |

**Riesgo de daño (Cox):** índice de concordancia **0,71** en camiones no vistos. Recupera el efecto del terreno de roca suelta (HR verdadero 3,0; estimado 2,8), de la pendiente y de la sobrecarga. Atribuye un efecto falso pequeño a las frenadas (HR 1,09), que en el simulador no influyen en el daño ni están correlacionadas con el terreno. La causa más probable es que el modelo resume con un **promedio por vida** condiciones que cambian de fase durante la vida del neumático; con datos reales conviene un modelo de Cox con **covariables que varían en el tiempo**.

### Lecciones para el equipo
1. **El método funciona con datos sintéticos:** recupera los efectos principales y reduce a menos de un tercio el error de estimación de horas remanentes cerca del retiro. No demuestra todavía la anticipación de 200 h.
2. **La importancia no es causalidad:** SHAP pone la **temperatura del neumático** en tercer lugar, aunque en el simulador no causa desgaste; es un síntoma de carga y presión. Por eso las **recomendaciones operacionales** («corregir presión», «cambiar ruta») se presentan como **hipótesis a validar** y no como órdenes automáticas.
3. **Los efectos no lineales justifican el Gradient Boosting**, que tiene menor error que la regresión. La regresión sigue siendo útil para **explicar** el tamaño de cada efecto.
4. **Resumir con promedios puede crear efectos falsos** (frenadas en el modelo de daño). Cada efecto encontrado con datos reales se debe revisar con el equipo de operaciones antes de recomendar acciones.

## 6. Limitaciones
- Los datos son sintéticos: la magnitud de cada efecto es un **supuesto** basado en literatura y criterio del equipo, no una medición.
- El modelo supone que las condiciones de las últimas ~200 h se mantienen. Un cambio de fase futuro no se anticipa; se debe conectar con el plan minero.
- No hay variables de proveedor ni de compuesto del neumático, ni datos de reparaciones.

## 7. Próximos pasos
1. **Datos reales:** acordar con la faena el acceso a TPMS, pesaje y despacho, y crear en Supabase una tabla `ciclos_operacion` con las 12 variables (entrada nueva en [`docs/datos.md`](datos.md)).
2. **Integración con el prototipo:** reemplazar en el tablero la tasa constante por la tasa prevista, y mostrar en la ficha (HU-04) las tres variables SHAP que más explican cada alerta.
3. **Revisión con el planificador (Semana 7, Francisco Opazo):** validar que los motivos mostrados sean comprensibles y accionables.
4. **Deep Learning** (LSTM sobre la serie de pasadas) solo si con datos reales el Gradient Boosting no alcanza la meta de 200 h.

## 8. Cómo reproducir
```bash
python -m venv modelo/.venv
modelo/.venv/Scripts/python -m pip install -r modelo/requirements.txt   # en Linux/macOS: modelo/.venv/bin/python
modelo/.venv/Scripts/python modelo/generar_datos.py   # ~6 s, crea modelo/datos/ (no se versiona)
modelo/.venv/Scripts/python modelo/entrenar.py        # ~20 s, crea modelo/resultados/
```
La semilla fija (2026) hace que los resultados sean idénticos en cada ejecución.
