-- =============================================================================
-- PROP-06 · Datos de terreno simulados, Gradient Boosting y SHAP
-- Crea 3 tablas y 2 vistas. Toda fila lleva origen = 'simulado' (o 'real' en el futuro).
-- La app (clave anon) solo puede LEER; escribe únicamente GitHub Actions con service_role.
-- Re-ejecutable. Ejecutar en Supabase → SQL Editor → Run without RLS.
-- =============================================================================

-- 1. Un ciclo de operación (≈ un día) de un neumático montado
CREATE TABLE IF NOT EXISTS ciclos_operacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    neumatico_id UUID NOT NULL REFERENCES neumaticos(id) ON DELETE CASCADE,
    serial VARCHAR(50) NOT NULL,
    caex_codigo VARCHAR(20) NOT NULL,
    posicion INTEGER NOT NULL CHECK (posicion BETWEEN 1 AND 6),
    vida INTEGER NOT NULL DEFAULT 1,              -- 2, 3… cuando el simulador modela un recambio
    ciclo INTEGER NOT NULL,                       -- correlativo dentro de la vida
    fecha DATE NOT NULL,
    horas_ciclo NUMERIC(5,1) NOT NULL,
    horas_vida NUMERIC(8,1) NOT NULL,             -- horas acumuladas de la vida al inicio del ciclo
    presion_desv_pct NUMERIC(5,2) NOT NULL,       -- % respecto de la presión nominal (TPMS)
    presion_psi NUMERIC(6,1) NOT NULL,
    temp_neumatico_c NUMERIC(5,1) NOT NULL,
    temp_ambiente_c NUMERIC(5,1) NOT NULL,
    carga_t NUMERIC(6,1) NOT NULL,                -- pesaje del CAEX
    velocidad_kmh NUMERIC(5,2) NOT NULL,          -- media del ciclo (despacho / GPS)
    distancia_km NUMERIC(7,1) NOT NULL,
    terreno VARCHAR(20) NOT NULL CHECK (terreno IN ('compactado', 'roca_suelta', 'barro')),
    pendiente_pct NUMERIC(5,2) NOT NULL,
    frenadas_por_h NUMERIC(5,2) NOT NULL,
    tkph NUMERIC(7,1) NOT NULL,
    profundidad_mm NUMERIC(5,2) NOT NULL,         -- medida al final del ciclo (con ruido del pórtico)
    profundidad_real_simulada NUMERIC(6,3) NOT NULL,   -- valor sin ruido: solo para continuar la simulación
    tasa_real_simulada NUMERIC(6,4) NOT NULL,     -- verdad del simulador: solo para evaluar, nunca es insumo del modelo
    origen VARCHAR(10) NOT NULL DEFAULT 'simulado' CHECK (origen IN ('simulado', 'real')),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (neumatico_id, vida, ciclo)
);
CREATE INDEX IF NOT EXISTS idx_ciclos_neumatico ON ciclos_operacion (neumatico_id, vida, ciclo);

-- 2. Cada versión entrenada del modelo, con sus métricas
CREATE TABLE IF NOT EXISTS modelo_versiones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR(40) UNIQUE NOT NULL,          -- ej. 'gb-terreno-20261025'
    fecha_entrenamiento TIMESTAMPTZ NOT NULL DEFAULT now(),
    algoritmo VARCHAR(60) NOT NULL DEFAULT 'Gradient Boosting (HistGradientBoostingRegressor) + SHAP',
    n_ciclos INTEGER NOT NULL,
    n_ventanas INTEGER NOT NULL,
    camiones_prueba INTEGER NOT NULL,
    mae_tasa_modelo NUMERIC(6,4) NOT NULL,        -- mm/100 h, en camiones no vistos
    mae_tasa_promedio NUMERIC(6,4) NOT NULL,      -- referencia: promedio de flota
    importancia JSONB,                            -- importancia SHAP global por variable
    origen VARCHAR(10) NOT NULL DEFAULT 'simulado' CHECK (origen IN ('simulado', 'real')),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Predicción diaria por neumático, con sus 3 causas SHAP principales
CREATE TABLE IF NOT EXISTS predicciones_modelo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    neumatico_id UUID NOT NULL REFERENCES neumaticos(id) ON DELETE CASCADE,
    serial VARCHAR(50) NOT NULL,
    modelo_version VARCHAR(40) NOT NULL REFERENCES modelo_versiones(version),
    fecha_prediccion TIMESTAMPTZ NOT NULL DEFAULT now(),
    profundidad_mm NUMERIC(5,2) NOT NULL,         -- profundidad actual (última medición del pórtico)
    tasa_prevista_mm_100h NUMERIC(6,3) NOT NULL,
    horas_remanentes_modelo INTEGER NOT NULL,
    causas JSONB NOT NULL,                        -- [{"variable", "etiqueta", "efecto": "aumenta"|"reduce", "peso_pct"}]
    origen VARCHAR(10) NOT NULL DEFAULT 'simulado' CHECK (origen IN ('simulado', 'real')),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_predicciones_neumatico ON predicciones_modelo (neumatico_id, fecha_prediccion DESC);

-- Vistas de apoyo (respetan RLS de las tablas base)
DROP VIEW IF EXISTS vista_ultimo_ciclo;
CREATE VIEW vista_ultimo_ciclo WITH (security_invoker = on) AS
SELECT DISTINCT ON (neumatico_id) *
FROM ciclos_operacion
ORDER BY neumatico_id, vida DESC, ciclo DESC;

DROP VIEW IF EXISTS vista_prediccion_actual;
CREATE VIEW vista_prediccion_actual WITH (security_invoker = on) AS
SELECT DISTINCT ON (neumatico_id) *
FROM predicciones_modelo
ORDER BY neumatico_id, fecha_prediccion DESC;

-- Seguridad: la app (anon) solo lee; service_role (GitHub Actions) omite RLS y escribe
DO $$
DECLARE t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY['ciclos_operacion', 'modelo_versiones', 'predicciones_modelo'] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('DROP POLICY IF EXISTS prototipo_lectura ON %I', t);
        EXECUTE format('CREATE POLICY prototipo_lectura ON %I FOR SELECT TO anon, authenticated USING (true)', t);
    END LOOP;
END $$;

-- Verificación: debe mostrar 3 tablas con RLS activado
SELECT relname AS tabla, relrowsecurity AS rls_activado
FROM pg_class
WHERE relname IN ('ciclos_operacion', 'modelo_versiones', 'predicciones_modelo')
ORDER BY relname;
