# Respaldo bibliográfico de los métodos y parámetros
## Control Predictivo de Neumáticos CAEX · Equipo 3

> **Autor de la revisión bibliográfica:** Nicolás Echeverría (Kanban del equipo, tareas «Matriz de respaldo bibliográfico» y «Citas en APA para respaldo»).
> **Criterio experto de taller:** Héctor Medina, reparación de neumáticos CAEX.
> Incorporado al repositorio con la propuesta PROP-05 (25-10-2026).

Este documento indica **qué tan respaldado está** cada método y cada parámetro que usa el prototipo. Sirve para distinguir lo que tiene fundamento de lo que es un **supuesto** o un **requisito propuesto** por el equipo.

**Niveles de respaldo**

| Nivel | Significado |
|---|---|
| **Respaldado** | La fuente apoya directamente el uso que le damos |
| **Parcial** | La fuente apoya el enfoque, pero no el valor exacto ni su aplicación a nuestra flota |
| **Criterio experto** | Valor aportado por experiencia de taller; pendiente de validar con datos de la faena |
| **Sin respaldo** | No se encontró fuente; se presenta como requisito propuesto o supuesto |

---

## 1. Métodos del modelo predictivo

| Método | Nivel | Evidencia y alcance | Fuente |
|---|---|---|---|
| Proyección lineal del desgaste | Parcial | Lindeque usa tasas de desgaste en mm/1.000 h, lo que permite una proyección inicial, pero no demuestra que el desgaste sea lineal durante toda la vida del neumático. | Lindeque (2016) |
| Regresión multivariable | Parcial | Vieira aplica regresión lineal múltiple y telemetría para predecir la vida estructural de neumáticos mineros. No valida directamente nuestra regresión de la tasa de desgaste. | Vieira (2017) |
| Gradient Boosting como modelo candidato | Respaldado | Grinsztajn y colaboradores respaldan evaluar modelos de árboles en datos tabulares. Su estudio no demuestra que sea el mejor modelo para CAEX. | Grinsztajn et al. (2022) |
| SHAP para explicar predicciones | Respaldado | Lundberg y Lee fundamentan la atribución de contribuciones a las variables. Kumar y colaboradores explican sus límites: las contribuciones **no deben interpretarse como causas**. | Lundberg y Lee (2017); Kumar et al. (2020) |
| Supervivencia y riesgos proporcionales | Parcial | Rahimdel estima la vida residual de neumáticos mineros con riesgos proporcionales. Respalda el enfoque, no los coeficientes ni la definición de falla del prototipo. | Rahimdel (2023) |
| Separar desgaste y falla prematura | Respaldado | Lindeque distingue reducir la tasa de desgaste de reducir las fallas prematuras: son fenómenos diferentes. | Lindeque (2016) |
| Redes neuronales para predecir vida útil | Parcial | Kunkyin-Saadaari y colaboradores estudian una red GRNN con optimización. Es un antecedente minero, pero no valida una LSTM ni obliga a avanzar hacia ella. | Kunkyin-Saadaari et al. (2025) |
| Validación por grupos y por tiempo | Respaldado | Roberts y colaboradores respaldan adaptar la validación a la dependencia entre observaciones. Separar por camión y evaluar períodos futuros aplica ese principio. | Roberts et al. (2017) |

## 2. Variables

| Variable | Nivel | Evidencia y alcance | Fuente |
|---|---|---|---|
| Carga, velocidad y temperatura de operación | Parcial | Goryunov y colaboradores estudian temperaturas de operación en neumáticos de camiones mineros. Respalda considerar estas variables; sus relaciones requieren calibración para nuestra flota. | Goryunov et al. (2019) |
| Profundidad del dibujo y temperatura | Parcial | Goryunov presenta una relación entre altura del dibujo y temperatura. No permite trasladar directamente una curva o coeficiente al prototipo. | Goryunov et al. (2019) |
| Efecto de la presión sobre desgaste y temperatura | Parcial | Michelin respalda los efectos de la presión insuficiente y excesiva. No valida los porcentajes del generador de datos sintéticos. | Michelin (s. f.-b) |

## 3. Parámetros y umbrales del prototipo

| Parámetro | Valor en el prototipo | Nivel | Evidencia y alcance | Fuente |
|---|---|---|---|---|
| Umbral de retiro | 20 mm | **Criterio experto** · Parcial en la literatura | Héctor Medina lo aporta desde su experiencia en reparación de neumáticos CAEX. Michelin respalda inspeccionar el desgaste y aplicar criterios técnicos de retiro, pero no hay respaldo para 20 mm como límite universal: debe definirse según el neumático y la faena. | Criterio experto; Michelin (s. f.-a) |
| Alerta crítica de temperatura | 95 °C | Parcial | La literatura respalda la importancia de controlar la temperatura, pero no valida el umbral exacto de 95 °C para nuestro equipo y método de medición. | Goryunov et al. (2019) |
| Advertencia de temperatura | 85 °C | Sin respaldo | Supuesto del prototipo para tener un nivel intermedio. | — |
| Presión nominal y bandas de alerta | 102 psi · ±5 % · ±10 % | Sin respaldo | Supuesto del prototipo; ajustar con el fabricante del neumático. | — |
| Ruido de medición del pórtico | σ = 0,25 mm | Parcial | TreadReader declara una precisión inferior a 0,2 mm en su equipo comercial. No valida una desviación de 0,25 mm en CAEX. | TreadReader (s. f.) |
| Proporción de fallas prematuras | ~30 % | Parcial | Lindeque aporta resultados de **una operación específica**. No es un criterio universal de desempeño. | Lindeque (2016) |
| Zonas de 200 h y 500 h; meta de 200 h de anticipación | 200 / 500 h | Sin respaldo | No hay respaldo directo en las fuentes revisadas. Son **requisitos propuestos de planificación**. Además, **un error de ±200 h no equivale a anticipar una falla con 200 h**. | — |

---

## 4. Cómo se corrigieron las afirmaciones del proyecto (PROP-05)

| Afirmación anterior | Corrección |
|---|---|
| «Umbral de retiro **seguro** de 20 mm», como un hecho | «Umbral de retiro de 20 mm», con su origen: criterio experto de taller, configurable por neumático y faena |
| 95 °C y 85 °C como umbrales establecidos | Umbrales de alerta del prototipo, no validados |
| Zonas de 200/500 h y meta de 200 h como estándar | Requisitos propuestos de planificación |
| «95 % de estimaciones dentro de ±200 h» junto a la meta de 200 h | Se aclara que el error de estimación no demuestra la anticipación de 200 h |
| «~30 % de los neumáticos muere prematuramente» como dato de la industria | Dato de una operación estudiada (Lindeque, 2016) |

---

## 5. Referencias (APA 7)

- Goryunov, S., Khoreshok, A., Grigoryeva, N., Preis, E., & Alitkina, O. (2019). The research of operational temperatures of dump trucks tires. *E3S Web of Conferences, 134*, Article 01014. https://doi.org/10.1051/e3sconf/201913401014
- Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? *Advances in Neural Information Processing Systems, 35*, 507–520. https://doi.org/10.52202/068431-0037
- Kumar, I. E., Venkatasubramanian, S., Scheidegger, C., & Friedler, S. (2020). Problems with Shapley-value-based explanations as feature importance measures. En *Proceedings of the 37th International Conference on Machine Learning* (Vol. 119, pp. 5491–5500). PMLR. https://proceedings.mlr.press/v119/kumar20e.html
- Kunkyin-Saadaari, F., Kesseh, A., & Agadzie, V. K. (2025). GRNN-FA hybrid model for predicting the useful life of dump truck tyres. *Journal of Sustainable Mining, 24*(2), Article 4. https://doi.org/10.46873/2300-3960.1451
- Lindeque, G. C. (2016). A critical investigation into tyre life on an iron ore haulage system. *Journal of the Southern African Institute of Mining and Metallurgy, 116*(4), 317–322. https://doi.org/10.17159/2411-9717/2016/v116n4a3
- Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems, 30*, 4765–4774. https://papers.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html
- Michelin. (s. f.-a). *Earthmover tyres inspection: Tyre checking and maintenance*. https://business.michelin.com.au/help-advice/earthmover-vehicles/tyre-maintenance-earthmover-tyre-inspection
- Michelin. (s. f.-b). *The right pressure for Earthmover tyres*. https://professional.michelin.dk/help-advice/managing-tyre-pressures
- Rahimdel, M. J. (2023). Residual lifetime estimation for the mining truck tires. *Proceedings of the Institution of Mechanical Engineers, Part D: Journal of Automobile Engineering, 237*(13), 3232–3244. https://doi.org/10.1177/09544070221121855
- Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881
- TreadReader. (s. f.). *TreadReader DriveOver*. https://treadreader.com/products/treadreader-driveover-laser-sensor-scanner/
- Vieira, C. S. (2017). *Factors that impact on tire structure useful life* (SAE Technical Paper No. 2017-36-0121). SAE International. https://doi.org/10.4271/2017-36-0121

> **Corrección respecto de la versión en Notion:** el DOI de Roberts et al. (2017) aparecía como `10.1111/ecog.0288`, que no existe; el correcto es `10.1111/ecog.02881`.
