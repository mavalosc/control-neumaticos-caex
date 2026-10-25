-- =============================================================================
-- ESQUEMA RELACIONAL SUPABASE (POSTGRESQL) - CONTROL DE NEUMÁTICOS CAEX
-- Proyecto: Pórtico Dimensional Predictivo de Neumáticos CAEX
-- Ecosistema DSD - Ingeniería Digital USACH · Equipo 3
-- Compatible y Re-ejecutable (Idempotente) para SQL Editor de Supabase
-- Orden de ejecución: 1) docs/schema.sql  2) docs/seed.sql (datos de demostración)
-- =============================================================================

-- 1. TIPOS ENUMERADOS (DOMINIO DEL NEGOCIO)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_intervencion_enum') THEN
        CREATE TYPE tipo_intervencion_enum AS ENUM ('retiro', 'rotacion', 'inspeccion');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_orden_enum') THEN
        CREATE TYPE estado_orden_enum AS ENUM ('programada', 'ejecutada', 'anulada');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'zona_criticidad_enum') THEN
        CREATE TYPE zona_criticidad_enum AS ENUM ('rojo', 'amarillo', 'verde', 'gris');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'severidad_dano_enum') THEN
        CREATE TYPE severidad_dano_enum AS ENUM ('0', '1', '2', '3'); -- 0: Sin daño, 1: Leve, 2: Moderado, 3: Crítico
    END IF;
END $$;

-- 2. TABLA: CAMIONES CAEX
CREATE TABLE IF NOT EXISTS camiones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL, -- ej. 'CAEX-101', 'CAEX-102'
    modelo VARCHAR(50) NOT NULL DEFAULT 'Cat 793F',
    horometro_h INTEGER NOT NULL DEFAULT 15000,
    estado_operacional VARCHAR(30) DEFAULT 'operativo',
    creado_en TIMESTAMPTZ DEFAULT now()
);

-- 3. TABLA: NEUMÁTICOS OTR (Identificados individualmente por Serial)
CREATE TABLE IF NOT EXISTS neumaticos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serial VARCHAR(50) UNIQUE NOT NULL, -- ej. '5980R63-2426-1348'
    caex_id UUID REFERENCES camiones(id) ON DELETE SET NULL,
    posicion INTEGER CHECK (posicion BETWEEN 1 AND 6), -- 1 a 6
    marca VARCHAR(30) NOT NULL DEFAULT 'Bridgestone', -- Michelin, Bridgestone, BKT
    medida VARCHAR(20) DEFAULT '59/80R63',
    umbral_retiro_mm NUMERIC(4,1) NOT NULL DEFAULT 20.0, -- UMBRAL CRÍTICO 20,0 mm
    creado_en TIMESTAMPTZ DEFAULT now()
);

-- 4. TABLA: MEDICIONES DIMENSIONALES (Generadas por pasada de pórtico)
CREATE TABLE IF NOT EXISTS mediciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_medicion VARCHAR(30) UNIQUE NOT NULL, -- ej. 'med-2494'
    neumatico_id UUID NOT NULL REFERENCES neumaticos(id) ON DELETE CASCADE,
    fecha_pasada TIMESTAMPTZ DEFAULT now(),
    horas_operacion INTEGER NOT NULL,
    profundidad_mm NUMERIC(4,1) NOT NULL, -- profundidad banda de rodado
    tasa_desgaste_por_100h NUMERIC(4,2) NOT NULL DEFAULT 1.10,
    tipo_tasa VARCHAR(20) DEFAULT 'observada', -- 'observada' o 'nominal'
    temperatura_flanco_c NUMERIC(4,1) DEFAULT 76.0,
    horas_remanentes_calculadas INTEGER NOT NULL,
    zona_calculada zona_criticidad_enum NOT NULL,
    modelo_version VARCHAR(20) DEFAULT 'v1.3',
    imagen_escaneo_url TEXT
);

-- 5. TABLA: REGISTRO DE DAÑOS DETECTADOS POR VISIÓN / AUDITORÍA
CREATE TABLE IF NOT EXISTS danos_neumaticos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medicion_id UUID REFERENCES mediciones(id) ON DELETE CASCADE,
    neumatico_id UUID NOT NULL REFERENCES neumaticos(id) ON DELETE CASCADE,
    severidad severidad_dano_enum NOT NULL DEFAULT '0',
    descripcion TEXT, -- ej. 'corte profundo en flanco', 'roca incrustada'
    confianza_ia NUMERIC(3,2) DEFAULT 0.95,
    validado_por_humano BOOLEAN DEFAULT FALSE,
    usuario_validador VARCHAR(50),
    fecha_registro TIMESTAMPTZ DEFAULT now()
);

-- 6. TABLA: VENTANAS DISPONIBLES DE TALLER DE NEUMÁTICOS
CREATE TABLE IF NOT EXISTS ventanas_taller (
    id SERIAL PRIMARY KEY,
    dia DATE NOT NULL,
    turno VARCHAR(30) NOT NULL, -- ej. 'turno A, 08:00 a 12:00', 'turno B, 20:00 a 00:00'
    cupos_totales INTEGER NOT NULL DEFAULT 3,
    cupos_libres INTEGER NOT NULL DEFAULT 3,
    horas_hasta_ventana INTEGER NOT NULL,
    creado_en TIMESTAMPTZ DEFAULT now()
);

-- 7. TABLA: ÓRDENES DE TRABAJO (OTs ERP / SAP PM)
CREATE TABLE IF NOT EXISTS ordenes_trabajo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL, -- ej. 'ot-0068'
    fecha_emision TIMESTAMPTZ DEFAULT now(),
    neumatico_id UUID NOT NULL REFERENCES neumaticos(id),
    ventana_id INTEGER NOT NULL REFERENCES ventanas_taller(id),
    medicion_origen_id UUID REFERENCES mediciones(id),
    tipo_intervencion tipo_intervencion_enum NOT NULL DEFAULT 'retiro',
    justificacion_nota TEXT NOT NULL,
    horas_remanentes_emision INTEGER NOT NULL,
    serial_reemplazo_bodega VARCHAR(50) DEFAULT '5980R63-B-544',
    estado estado_orden_enum NOT NULL DEFAULT 'programada',
    actualizado_en TIMESTAMPTZ DEFAULT now()
);

-- 8. TABLA: HISTORIAL DE CAMBIOS Y TRAZABILIDAD AUDITABLE
CREATE TABLE IF NOT EXISTS historial_ordenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    orden_id UUID NOT NULL REFERENCES ordenes_trabajo(id) ON DELETE CASCADE,
    fecha_evento TIMESTAMPTZ DEFAULT now(),
    autor VARCHAR(50) NOT NULL DEFAULT 'planificador',
    accion VARCHAR(50) NOT NULL, -- 'creacion', 'modificacion_ventana', 'anulacion'
    motivo TEXT NOT NULL, -- Obligatorio según rúbrica
    detalles JSONB
);

-- Columnas agregadas para la conexión del prototipo (ALTER idempotente: sirve
-- también en una base donde las tablas ya existían).
ALTER TABLE ventanas_taller ADD COLUMN IF NOT EXISTS reservable BOOLEAN NOT NULL DEFAULT TRUE; -- se ofrece al agendar
ALTER TABLE ordenes_trabajo ADD COLUMN IF NOT EXISTS medicion_codigo VARCHAR(30); -- ej. 'med-2494'
ALTER TABLE ordenes_trabajo ADD COLUMN IF NOT EXISTS origen_detalle TEXT;         -- ej. '22,9 mm, tasa observada'

-- Auditoría temporal uniforme (Tidy Data, regla 3): toda tabla registra cuándo se creó la fila.
ALTER TABLE mediciones        ADD COLUMN IF NOT EXISTS creado_en TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE danos_neumaticos  ADD COLUMN IF NOT EXISTS creado_en TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE historial_ordenes ADD COLUMN IF NOT EXISTS creado_en TIMESTAMPTZ NOT NULL DEFAULT now();

-- =============================================================================
-- FUNCIONES Y TRIGGERS PARA CONTROL DE CAPACIDAD DE TALLER (CUPOS)
-- SECURITY DEFINER: el trigger ajusta cupos aunque el usuario anon no tenga
-- permiso directo de UPDATE sobre ventanas_taller.
-- =============================================================================

-- Disminuye cupo al programar una orden
CREATE OR REPLACE FUNCTION decrementar_cupo_taller()
RETURNS TRIGGER
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
    UPDATE ventanas_taller
    SET cupos_libres = cupos_libres - 1
    WHERE id = NEW.ventana_id AND cupos_libres > 0;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'La ventana de taller seleccionada no cuenta con cupos libres.';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_decrementar_cupo ON ordenes_trabajo;
CREATE TRIGGER trg_decrementar_cupo
AFTER INSERT ON ordenes_trabajo
FOR EACH ROW
WHEN (NEW.estado = 'programada')
EXECUTE FUNCTION decrementar_cupo_taller();

-- Libera cupo al anular una orden
CREATE OR REPLACE FUNCTION liberar_cupo_taller_anulacion()
RETURNS TRIGGER
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
    IF OLD.estado = 'programada' AND NEW.estado = 'anulada' THEN
        UPDATE ventanas_taller
        SET cupos_libres = LEAST(cupos_totales, cupos_libres + 1)
        WHERE id = NEW.ventana_id;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_liberar_cupo_anulacion ON ordenes_trabajo;
CREATE TRIGGER trg_liberar_cupo_anulacion
AFTER UPDATE ON ordenes_trabajo
FOR EACH ROW
EXECUTE FUNCTION liberar_cupo_taller_anulacion();

-- Mueve el cupo al cambiar la ventana de una orden programada (HU-08)
CREATE OR REPLACE FUNCTION mover_cupo_cambio_ventana()
RETURNS TRIGGER
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
    IF NEW.estado = 'programada' AND NEW.ventana_id IS DISTINCT FROM OLD.ventana_id THEN
        UPDATE ventanas_taller
        SET cupos_libres = cupos_libres - 1
        WHERE id = NEW.ventana_id AND cupos_libres > 0;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'La nueva ventana de taller no cuenta con cupos libres.';
        END IF;
        UPDATE ventanas_taller
        SET cupos_libres = LEAST(cupos_totales, cupos_libres + 1)
        WHERE id = OLD.ventana_id;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_mover_cupo_cambio_ventana ON ordenes_trabajo;
CREATE TRIGGER trg_mover_cupo_cambio_ventana
AFTER UPDATE OF ventana_id ON ordenes_trabajo
FOR EACH ROW
EXECUTE FUNCTION mover_cupo_cambio_ventana();

-- =============================================================================
-- VISTA: ÚLTIMA MEDICIÓN Y ÚLTIMO DAÑO DE CADA NEUMÁTICO MONTADO
-- security_invoker: la vista respeta las políticas RLS de las tablas base.
-- =============================================================================
DROP VIEW IF EXISTS vista_tablero_turno;
CREATE VIEW vista_tablero_turno WITH (security_invoker = on) AS
SELECT
    c.codigo AS caex_codigo,
    c.modelo AS caex_modelo,
    c.horometro_h,
    n.id AS neumatico_id,
    n.posicion,
    n.serial AS neumatico_serial,
    n.marca,
    m.codigo_medicion,
    m.profundidad_mm,
    m.tasa_desgaste_por_100h,
    m.tipo_tasa,
    m.horas_remanentes_calculadas,
    m.zona_calculada,
    m.temperatura_flanco_c,
    COALESCE(d.severidad, '0') AS nivel_dano,
    COALESCE(d.descripcion, 'Sin daño') AS detalle_dano,
    d.confianza_ia,
    d.validado_por_humano,
    m.fecha_pasada
FROM neumaticos n
JOIN camiones c ON n.caex_id = c.id
LEFT JOIN LATERAL (
    SELECT * FROM mediciones
    WHERE neumatico_id = n.id
    ORDER BY fecha_pasada DESC
    LIMIT 1
) m ON TRUE
LEFT JOIN LATERAL (
    SELECT * FROM danos_neumaticos
    WHERE neumatico_id = n.id
    ORDER BY fecha_registro DESC
    LIMIT 1
) d ON TRUE;

-- =============================================================================
-- SEGURIDAD: ROW LEVEL SECURITY (RLS)
-- Supabase activa RLS en tablas nuevas; sin políticas, la clave anon no ve filas.
-- Políticas de PROTOTIPO: el frontend (clave anon, pública) puede leer todo,
-- registrar mediciones/daños/órdenes/historial y actualizar órdenes.
-- No hay políticas DELETE: las órdenes se anulan, nunca se borran (trazabilidad).
-- En producción estas políticas se restringirían a usuarios autenticados por rol.
-- =============================================================================
DO $$
DECLARE t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY['camiones','neumaticos','mediciones','danos_neumaticos',
                             'ventanas_taller','ordenes_trabajo','historial_ordenes'] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('DROP POLICY IF EXISTS prototipo_lectura ON %I', t);
        EXECUTE format('CREATE POLICY prototipo_lectura ON %I FOR SELECT TO anon, authenticated USING (true)', t);
    END LOOP;

    FOREACH t IN ARRAY ARRAY['mediciones','danos_neumaticos','ordenes_trabajo','historial_ordenes'] LOOP
        EXECUTE format('DROP POLICY IF EXISTS prototipo_insercion ON %I', t);
        EXECUTE format('CREATE POLICY prototipo_insercion ON %I FOR INSERT TO anon, authenticated WITH CHECK (true)', t);
    END LOOP;
END $$;

DROP POLICY IF EXISTS prototipo_actualizacion ON ordenes_trabajo;
CREATE POLICY prototipo_actualizacion ON ordenes_trabajo
    FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

-- Los datos de demostración (67 camiones, 402 neumáticos, órdenes) están en docs/seed.sql.

-- =============================================================================
-- PROP-06 · DATOS DE TERRENO SIMULADOS Y PREDICCIONES DEL MODELO
-- (misma definición que docs/migraciones/2026-10-25_PROP-06_terreno_simulado.sql)
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
