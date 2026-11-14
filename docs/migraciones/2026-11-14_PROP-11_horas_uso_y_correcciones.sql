-- =============================================================================
-- PROP-11 · Cambios de la app tras la sesión 1 con usuario
--   (a) Horas de uso del neumático: horómetro del camión al montarlo (dato sintético).
--   (b) La corrección de daño conserva la descripción que detectó la visión artificial.
--   (c) El email de quien corrige un daño queda en danos_neumaticos.usuario_validador;
--       la app pública solo lo ve abreviado (ma***@usach.cl), igual que en PROP-08.
-- Ejecutar en Supabase → SQL Editor → Run without RLS, en este orden:
--   PARTE 1: antes de fusionar el PR (no afecta a la app publicada).
--   PARTE 2: después de fusionar el PR y de que Vercel publique la nueva versión.
--   PARTE 3: el 31-12-2026 (fin del curso), junto con la parte 3 de PROP-08.
-- =============================================================================

-- ----------------------------- PARTE 1 ---------------------------------------
-- (a) Horómetro del camión cuando se montó el neumático.
ALTER TABLE neumaticos ADD COLUMN IF NOT EXISTS horometro_montaje_h INTEGER;
COMMENT ON COLUMN neumaticos.horometro_montaje_h IS
  'Horómetro del CAEX al montar el neumático. PROTOTIPO: dato sintético calculado desde el desgaste (banda nueva de 95 mm), no un registro real.';

-- Valor sintético coherente con el desgaste de cada neumático:
-- horas de uso ≈ (95 mm − profundidad actual) / tasa × 100; montaje = horómetro actual − horas de uso.
UPDATE neumaticos n
SET horometro_montaje_h = GREATEST(0, c.horometro_h - ROUND((95 - m.profundidad_mm) / NULLIF(m.tasa_desgaste_por_100h, 0) * 100))
FROM camiones c,
     (SELECT DISTINCT ON (neumatico_id) neumatico_id, profundidad_mm, tasa_desgaste_por_100h
      FROM mediciones ORDER BY neumatico_id, fecha_pasada DESC) m      -- última medición de cada neumático
WHERE c.id = n.caex_id AND m.neumatico_id = n.id AND n.horometro_montaje_h IS NULL;

-- Vista del tablero: va ANTES del cambio de tipo de usuario_validador, porque la vista anterior
-- leía los daños con SELECT * y Postgres no deja cambiar una columna que usa una vista.
-- Mismas columnas, en el mismo orden, y cinco nuevas al final.
-- Los daños se leen con columnas explícitas (sin usuario_validador) para que la vista
-- siga funcionando cuando la parte 2 quite el acceso a esa columna.
CREATE OR REPLACE VIEW vista_tablero_turno WITH (security_invoker = on) AS
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
    m.fecha_pasada,
    n.horometro_montaje_h,
    GREATEST(0, c.horometro_h - n.horometro_montaje_h) AS horas_uso_h,
    det.severidad AS nivel_detectado,
    det.descripcion AS detalle_detectado,
    det.confianza_ia AS confianza_detectada
FROM neumaticos n
JOIN camiones c ON n.caex_id = c.id
LEFT JOIN LATERAL (
    SELECT * FROM mediciones
    WHERE neumatico_id = n.id
    ORDER BY fecha_pasada DESC
    LIMIT 1
) m ON TRUE
LEFT JOIN LATERAL (
    SELECT severidad, descripcion, confianza_ia, validado_por_humano FROM danos_neumaticos
    WHERE neumatico_id = n.id
    ORDER BY fecha_registro DESC
    LIMIT 1
) d ON TRUE
LEFT JOIN LATERAL (   -- última detección de la visión artificial (no corregida por una persona)
    SELECT severidad, descripcion, confianza_ia FROM danos_neumaticos
    WHERE neumatico_id = n.id AND validado_por_humano IS NOT TRUE
    ORDER BY fecha_registro DESC
    LIMIT 1
) det ON TRUE;

-- (c) Un email puede tener hasta 254 caracteres
ALTER TABLE danos_neumaticos ALTER COLUMN usuario_validador TYPE VARCHAR(254);

-- Vista de daños con el validador abreviado. Se ejecuta con los permisos de su dueño
-- (no security_invoker), así la app lee los daños sin acceso a la columna completa.
DROP VIEW IF EXISTS vista_danos_neumaticos;
CREATE VIEW vista_danos_neumaticos AS
SELECT d.id,
       n.serial,
       m.codigo_medicion,
       d.severidad,
       d.descripcion,
       d.confianza_ia,
       d.validado_por_humano,
       CASE WHEN position('@' IN d.usuario_validador) > 1
            THEN left(d.usuario_validador, 2) || '***@' || split_part(d.usuario_validador, '@', 2)
            ELSE d.usuario_validador
       END AS usuario_validador,
       d.fecha_registro,
       d.neumatico_id,
       d.medicion_id
FROM danos_neumaticos d
JOIN neumaticos n ON n.id = d.neumatico_id
LEFT JOIN mediciones m ON m.id = d.medicion_id;

GRANT SELECT ON vista_danos_neumaticos TO anon, authenticated;

-- Verificación de la parte 1: 402 neumáticos con horas de uso y la vista de daños abreviada
SELECT count(*) AS con_horas_uso FROM vista_tablero_turno WHERE horas_uso_h IS NOT NULL;
SELECT caex_codigo, posicion, horas_remanentes_calculadas, horas_uso_h, nivel_dano, detalle_detectado
FROM vista_tablero_turno ORDER BY horas_remanentes_calculadas LIMIT 5;
SELECT serial, severidad, descripcion, usuario_validador, fecha_registro FROM vista_danos_neumaticos ORDER BY fecha_registro DESC LIMIT 5;


-- ----------------------------- PARTE 2 ---------------------------------------
-- La clave pública puede seguir INSERTANDO correcciones con el email, pero ya no puede LEER
-- la columna usuario_validador completa (la app la lee abreviada desde vista_danos_neumaticos).
REVOKE SELECT ON danos_neumaticos FROM anon, authenticated;
GRANT SELECT (id, medicion_id, neumatico_id, severidad, descripcion, confianza_ia,
              validado_por_humano, fecha_registro, creado_en)
  ON danos_neumaticos TO anon, authenticated;

-- Verificación de la parte 2: debe devolver false
SELECT has_column_privilege('anon', 'danos_neumaticos', 'usuario_validador', 'SELECT') AS anon_lee_email;


-- ----------------------------- PARTE 3 (31-12-2026) --------------------------
-- UPDATE danos_neumaticos SET usuario_validador = 'planificador (email eliminado)'
-- WHERE usuario_validador LIKE '%@%';
