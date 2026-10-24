-- =============================================================================
-- PROP-02 · Terminología: "neumático" en lugar de "goma"
-- Corrige las notas de las 2 órdenes de demostración ya guardadas en Supabase.
-- (docs/seed.sql ya trae el texto corregido para futuras cargas.)
-- Ejecutar en Supabase → SQL Editor → Run without RLS.
-- =============================================================================

UPDATE ordenes_trabajo
SET justificacion_nota = replace(justificacion_nota,
        'dejar la goma retirada en la cancha', 'dejar el neumático retirado en la cancha'),
    actualizado_en = now()
WHERE codigo = 'ot-0068';

UPDATE ordenes_trabajo
SET justificacion_nota = replace(justificacion_nota,
        'goma entregada en cancha de garantía', 'neumático entregado en cancha de garantía'),
    actualizado_en = now()
WHERE codigo = 'ot-0052';

-- Verificación: debe devolver 0
SELECT count(*) AS notas_con_goma FROM ordenes_trabajo WHERE justificacion_nota ILIKE '%goma%';
