-- =============================================================================
-- PROP-07 · Datos reales de TPMS y velocidad (anonimizados)
-- Crea 4 tablas. Toda fila lleva origen = 'real'. Los equipos van anonimizados
-- ("Camión A", "Cargador B"…): no se guardan nombres de faena, empresa ni códigos originales.
-- La app (clave anon) solo puede LEER; escribe únicamente el script de carga con service_role.
-- Re-ejecutable. Ejecutar en Supabase → SQL Editor → Run without RLS.
-- =============================================================================

-- 1. Alertas del sistema TPMS (presión y temperatura) de una faena real, 2024–2026
CREATE TABLE IF NOT EXISTS alertas_tpms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clave VARCHAR(40) UNIQUE NOT NULL,            -- huella de la fila (evita duplicar al recargar)
    equipo VARCHAR(20) NOT NULL,                  -- anonimizado: 'Camión A', 'Cargador B'…
    tipo_equipo VARCHAR(10) NOT NULL CHECK (tipo_equipo IN ('camion', 'cargador')),
    posicion INTEGER NOT NULL CHECK (posicion BETWEEN 1 AND 6),
    sensor VARCHAR(10) NOT NULL,                  -- anonimizado: 'S-001'…
    tipo_alerta VARCHAR(30) NOT NULL,             -- 'Baja presión', 'Alta presión', 'Alta temperatura'…
    nivel INTEGER NOT NULL CHECK (nivel BETWEEN 1 AND 3),
    valor NUMERIC(6,1),
    limite NUMERIC(6,1),                          -- umbral que gatilló la alerta (del mensaje del TPMS)
    unidad VARCHAR(4) NOT NULL CHECK (unidad IN ('psi', '°C')),
    fecha_hora TIMESTAMP NOT NULL,                -- hora local de la faena
    origen VARCHAR(10) NOT NULL DEFAULT 'real' CHECK (origen IN ('simulado', 'real')),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_alertas_equipo ON alertas_tpms (equipo, posicion, fecha_hora);

-- 2. Excesos de velocidad registrados por el sistema de flota, jul–oct 2026
CREATE TABLE IF NOT EXISTS eventos_velocidad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clave VARCHAR(40) UNIQUE NOT NULL,
    equipo VARCHAR(20) NOT NULL,
    tipo_equipo VARCHAR(10) NOT NULL CHECK (tipo_equipo IN ('camion', 'cargador')),
    fecha_hora TIMESTAMP NOT NULL,
    velocidad_kmh INTEGER NOT NULL,
    limite_kmh INTEGER NOT NULL,
    area VARCHAR(40),                             -- tramo con límite propio (ej. 'Curva 11 C'); vacío = ruta general
    origen VARCHAR(10) NOT NULL DEFAULT 'real' CHECK (origen IN ('simulado', 'real')),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_velocidad_equipo ON eventos_velocidad (equipo, fecha_hora);

-- 3. Cada versión entrenada del modelo de riesgo, con sus métricas
CREATE TABLE IF NOT EXISTS riesgo_versiones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR(40) UNIQUE NOT NULL,          -- ej. 'gb-riesgo-20261029'
    fecha_entrenamiento TIMESTAMPTZ NOT NULL DEFAULT now(),
    algoritmo VARCHAR(80) NOT NULL DEFAULT 'Gradient Boosting (HistGradientBoostingClassifier) + SHAP',
    objetivo VARCHAR(120) NOT NULL,               -- qué predice
    datos_desde DATE NOT NULL,
    datos_hasta DATE NOT NULL,
    fecha_corte DATE NOT NULL,                    -- se entrena antes de esta fecha y se evalúa después
    n_ejemplos INTEGER NOT NULL,
    tasa_base NUMERIC(6,4) NOT NULL,              -- % de días-posición seguidos de una alerta crítica (prueba)
    auc_modelo NUMERIC(6,4) NOT NULL,
    auc_referencia NUMERIC(6,4) NOT NULL,         -- regla simple: alertas de los últimos 14 días
    metricas JSONB,
    importancia JSONB,
    origen VARCHAR(10) NOT NULL DEFAULT 'real' CHECK (origen IN ('simulado', 'real')),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Riesgo actual por equipo y posición, con sus 3 causas SHAP principales
CREATE TABLE IF NOT EXISTS riesgo_posiciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    modelo_version VARCHAR(40) NOT NULL REFERENCES riesgo_versiones(version),
    equipo VARCHAR(20) NOT NULL,
    tipo_equipo VARCHAR(10) NOT NULL CHECK (tipo_equipo IN ('camion', 'cargador')),
    posicion INTEGER NOT NULL CHECK (posicion BETWEEN 1 AND 6),
    fecha_referencia DATE NOT NULL,               -- último día con datos
    probabilidad NUMERIC(5,4) NOT NULL,           -- de una alerta crítica (nivel 3) en los 7 días siguientes
    nivel_riesgo VARCHAR(10) NOT NULL CHECK (nivel_riesgo IN ('alto', 'medio', 'bajo')),
    alertas_14d INTEGER NOT NULL,
    causas JSONB NOT NULL,                        -- [{"variable", "etiqueta", "efecto": "aumenta"|"reduce", "peso_pct"}]
    origen VARCHAR(10) NOT NULL DEFAULT 'real' CHECK (origen IN ('simulado', 'real')),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (modelo_version, equipo, posicion)
);

-- Seguridad: la app (anon) solo lee; service_role (script de carga) omite RLS y escribe
DO $$
DECLARE t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY['alertas_tpms', 'eventos_velocidad', 'riesgo_versiones', 'riesgo_posiciones'] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('DROP POLICY IF EXISTS prototipo_lectura ON %I', t);
        EXECUTE format('CREATE POLICY prototipo_lectura ON %I FOR SELECT TO anon, authenticated USING (true)', t);
    END LOOP;
END $$;

-- Verificación: debe mostrar 4 tablas con RLS activado
SELECT relname AS tabla, relrowsecurity AS rls_activado
FROM pg_class
WHERE relname IN ('alertas_tpms', 'eventos_velocidad', 'riesgo_versiones', 'riesgo_posiciones')
ORDER BY relname;
