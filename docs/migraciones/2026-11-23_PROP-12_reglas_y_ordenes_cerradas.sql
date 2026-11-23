-- =============================================================================
-- PROP-12 · Avance funcional robustecido: reglas en la base y órdenes cerradas
--   (a) Respaldo de las órdenes y su historial antes de cambiar nada.
--   (b) Reglas de largo (los mismos números de src/reglas.js; tests/reglas.test.js lo verifica).
--   (c) Cada cambio de estado o de ventana entra por UNA sola escritura: una fila en
--       historial_ordenes. Un trigger aplica el cambio a la orden en la misma transacción:
--       si algo falla, no queda nada a medias (antes, anular eran dos escrituras).
--   (d) Una orden anulada o ejecutada ya no admite cambios.
--   (e) Parte 2: la clave pública deja de poder modificar órdenes directamente.
--   (f) El texto automático de creación deja de mencionar un ERP que no existe.
-- Sin backend propio, la «capa servidor» del curso son estos CHECK y triggers de Postgres.
-- Ejecutar en Supabase → SQL Editor, en este orden:
--   PARTE 1: ANTES de fusionar el PR. La app publicada hoy sigue funcionando igual.
--   PARTE 2: DESPUÉS de fusionar el PR y de que Vercel publique la nueva versión.
--   REVERSA: solo si hay que volver atrás (al final del archivo).
-- =============================================================================

-- ----------------------------- PARTE 1 ---------------------------------------
-- (a) Respaldo en un esquema que la API pública no expone.
CREATE SCHEMA IF NOT EXISTS respaldo;
REVOKE ALL ON SCHEMA respaldo FROM anon, authenticated;
CREATE TABLE IF NOT EXISTS respaldo.ordenes_trabajo_20261123 AS TABLE ordenes_trabajo;
CREATE TABLE IF NOT EXISTS respaldo.historial_ordenes_20261123 AS TABLE historial_ordenes;
CREATE TABLE IF NOT EXISTS respaldo.ventanas_taller_20261123 AS TABLE ventanas_taller;

-- (b) Reglas de largo. NOT VALID: se aplican a todo lo nuevo sin rechazar filas antiguas;
--     la consulta de verificación de abajo muestra cuántas antiguas no cumplen.
ALTER TABLE historial_ordenes DROP CONSTRAINT IF EXISTS chk_historial_motivo_largo;
ALTER TABLE historial_ordenes ADD CONSTRAINT chk_historial_motivo_largo
  CHECK (char_length(btrim(motivo)) BETWEEN 3 AND 500) NOT VALID;            -- REGLAS.motivo

ALTER TABLE ordenes_trabajo DROP CONSTRAINT IF EXISTS chk_orden_justificacion_largo;
ALTER TABLE ordenes_trabajo ADD CONSTRAINT chk_orden_justificacion_largo
  CHECK (char_length(btrim(justificacion_nota)) BETWEEN 10 AND 2000) NOT VALID; -- REGLAS.justificacion

-- (c) Un evento del historial aplica el cambio a la orden (una sola escritura).
--     accion = 'anulacion'    → estado 'anulada' (el trigger existente libera el cupo)
--     accion = 'ejecucion'    → estado 'ejecutada'
--     accion = 'modificacion' → si detalles trae ventana_id, mueve la orden (el trigger existente mueve el cupo
--                               y rechaza la ventana sin cupo: entonces tampoco queda el registro del historial)
CREATE OR REPLACE FUNCTION aplicar_evento_orden()
RETURNS TRIGGER
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
    o ordenes_trabajo%ROWTYPE;
    nueva_ventana INTEGER;
BEGIN
    IF NEW.accion = 'creacion' THEN
        RETURN NEW;
    END IF;
    SELECT * INTO o FROM ordenes_trabajo WHERE id = NEW.orden_id FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'La orden no existe.';
    END IF;

    -- Compatibilidad con la versión anterior de la app (anulaba la orden y después escribía el historial)
    IF NEW.accion = 'anulacion' AND o.estado = 'anulada' THEN
        RETURN NEW;
    END IF;

    IF o.estado <> 'programada' THEN
        RAISE EXCEPTION 'La orden % está % y no admite cambios.', o.codigo, o.estado
            USING ERRCODE = 'P0001', HINT = 'orden_cerrada';
    END IF;

    IF NEW.accion = 'anulacion' THEN
        UPDATE ordenes_trabajo SET estado = 'anulada', actualizado_en = now() WHERE id = o.id;
    ELSIF NEW.accion = 'ejecucion' THEN
        UPDATE ordenes_trabajo SET estado = 'ejecutada', actualizado_en = now() WHERE id = o.id;
    ELSIF NEW.accion = 'modificacion' THEN
        nueva_ventana := NULLIF(NEW.detalles ->> 'ventana_id', '')::INTEGER;
        IF nueva_ventana IS NOT NULL AND nueva_ventana IS DISTINCT FROM o.ventana_id THEN
            UPDATE ordenes_trabajo SET ventana_id = nueva_ventana, actualizado_en = now() WHERE id = o.id;
        ELSE
            UPDATE ordenes_trabajo SET actualizado_en = now() WHERE id = o.id;
        END IF;
    ELSE
        RAISE EXCEPTION 'Acción de historial desconocida: %.', NEW.accion;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_aplicar_evento_orden ON historial_ordenes;
CREATE TRIGGER trg_aplicar_evento_orden
BEFORE INSERT ON historial_ordenes
FOR EACH ROW
EXECUTE FUNCTION aplicar_evento_orden();

-- (d) Una orden anulada o ejecutada no se modifica ni se reactiva, venga de donde venga el cambio.
CREATE OR REPLACE FUNCTION proteger_orden_cerrada()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.estado <> 'programada' THEN
        RAISE EXCEPTION 'La orden % está % y no admite cambios.', OLD.codigo, OLD.estado
            USING ERRCODE = 'P0001', HINT = 'orden_cerrada';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_proteger_orden_cerrada ON ordenes_trabajo;
CREATE TRIGGER trg_proteger_orden_cerrada
BEFORE UPDATE ON ordenes_trabajo
FOR EACH ROW
EXECUTE FUNCTION proteger_orden_cerrada();

-- (f) El texto de creación lo escribía la app, no una persona, y afirmaba algo falso
--     («sincronizada con ERP», «en SAP PM»): no hay ERP conectado. Se corrige solo ese texto
--     automático; el original queda en respaldo.historial_ordenes_20261123.
UPDATE historial_ordenes
SET motivo = 'orden emitida',
    detalles = coalesce(detalles, '{}'::jsonb) || jsonb_build_object('texto_original', motivo, 'corregido_por', 'PROP-12')
WHERE accion = 'creacion' AND (motivo ILIKE '%ERP%' OR motivo ILIKE '%SAP PM%');

-- Verificación de la parte 1 (debe mostrar 3 respaldos con filas, 2 reglas y 2 triggers):
SELECT 'respaldo órdenes' AS item, count(*)::text AS valor FROM respaldo.ordenes_trabajo_20261123
UNION ALL SELECT 'respaldo historial', count(*)::text FROM respaldo.historial_ordenes_20261123
UNION ALL SELECT 'respaldo ventanas', count(*)::text FROM respaldo.ventanas_taller_20261123
UNION ALL SELECT 'reglas nuevas', count(*)::text FROM pg_constraint
  WHERE conname IN ('chk_historial_motivo_largo', 'chk_orden_justificacion_largo')
UNION ALL SELECT 'triggers nuevos', count(*)::text FROM pg_trigger
  WHERE tgname IN ('trg_aplicar_evento_orden', 'trg_proteger_orden_cerrada')
UNION ALL SELECT 'historial antiguo fuera de regla', count(*)::text FROM historial_ordenes
  WHERE char_length(btrim(motivo)) NOT BETWEEN 3 AND 500;

-- ----------------------------- PARTE 2 ---------------------------------------
-- Después de publicar la nueva app: la clave pública ya no modifica órdenes directamente.
-- Todo cambio entra como evento del historial (con motivo obligatorio) y lo aplica el trigger.
-- DROP POLICY IF EXISTS prototipo_actualizacion ON ordenes_trabajo;
-- REVOKE UPDATE ON ordenes_trabajo FROM anon, authenticated;
-- Verificación (debe devolver false):
-- SELECT has_table_privilege('anon', 'ordenes_trabajo', 'UPDATE') AS anon_modifica_ordenes;

-- ----------------------------- REVERSA ---------------------------------------
-- Solo si hay que volver a la versión anterior de la app:
-- CREATE POLICY prototipo_actualizacion ON ordenes_trabajo FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
-- GRANT UPDATE ON ordenes_trabajo TO anon, authenticated;
-- DROP TRIGGER IF EXISTS trg_aplicar_evento_orden ON historial_ordenes;
-- DROP TRIGGER IF EXISTS trg_proteger_orden_cerrada ON ordenes_trabajo;
-- ALTER TABLE historial_ordenes DROP CONSTRAINT IF EXISTS chk_historial_motivo_largo;
-- ALTER TABLE ordenes_trabajo DROP CONSTRAINT IF EXISTS chk_orden_justificacion_largo;
-- Los respaldos quedan en el esquema «respaldo»; se borran el 31-12-2026 con DROP SCHEMA respaldo CASCADE.
