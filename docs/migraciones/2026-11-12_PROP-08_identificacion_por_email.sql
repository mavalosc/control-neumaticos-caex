-- =============================================================================
-- PROP-08 · Identificación por email en la planificación del taller
-- El email de quien emite, modifica o anula una orden queda en historial_ordenes.autor.
-- La app pública NO puede leer ese email: solo ve una versión abreviada (ma***@usach.cl)
-- a través de la vista vista_historial_ordenes.
-- Ejecutar en Supabase → SQL Editor → Run without RLS, en este orden:
--   PARTE 1: antes de fusionar el PR (no afecta a la app publicada).
--   PARTE 2: después de fusionar el PR y de que Vercel publique la nueva versión.
--   PARTE 3: el 31-12-2026 (fin del curso), para no conservar emails más de lo necesario.
-- =============================================================================

-- ----------------------------- PARTE 1 ---------------------------------------
-- Un email puede tener hasta 254 caracteres
ALTER TABLE historial_ordenes ALTER COLUMN autor TYPE VARCHAR(254);

-- Vista con el autor abreviado. Se ejecuta con los permisos de su dueño (no security_invoker),
-- así la app puede leer el historial sin tener acceso a la columna autor completa.
DROP VIEW IF EXISTS vista_historial_ordenes;
CREATE VIEW vista_historial_ordenes AS
SELECT h.id,
       h.orden_id,
       o.codigo AS codigo_orden,
       h.fecha_evento,
       CASE WHEN position('@' IN h.autor) > 1
            THEN left(h.autor, 2) || '***@' || split_part(h.autor, '@', 2)
            ELSE h.autor
       END AS autor,
       h.accion,
       h.motivo
FROM historial_ordenes h
JOIN ordenes_trabajo o ON o.id = h.orden_id;

GRANT SELECT ON vista_historial_ordenes TO anon, authenticated;

-- Verificación de la parte 1: debe mostrar filas con el autor abreviado o 'planificador'
SELECT codigo_orden, fecha_evento, autor, accion FROM vista_historial_ordenes ORDER BY fecha_evento DESC LIMIT 5;


-- ----------------------------- PARTE 2 ---------------------------------------
-- La clave pública puede seguir INSERTANDO el autor, pero ya no puede LEER la columna completa.
-- REVOKE SELECT ON historial_ordenes FROM anon, authenticated;
-- GRANT SELECT (id, orden_id, fecha_evento, accion, motivo, detalles) ON historial_ordenes TO anon, authenticated;
--
-- Verificación de la parte 2: debe devolver false
-- SELECT has_column_privilege('anon', 'historial_ordenes', 'autor', 'SELECT') AS anon_lee_email;


-- ----------------------------- PARTE 3 (31-12-2026) --------------------------
-- Fin del período de conservación: se reemplazan los emails por el rol.
-- UPDATE historial_ordenes SET autor = 'planificador (email eliminado)' WHERE autor LIKE '%@%';
