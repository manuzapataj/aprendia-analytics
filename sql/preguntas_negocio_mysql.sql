-- AprendIA | Consultas de Manuela Zapata Jiménez, entrega de bootcamp.
-- Requiere la estructura original plataforma_cursos_aprendia en MySQL.
-- La pregunta 3 promedia tasas por curso. La tasa global pondera por inscripciones.
-- La pregunta 5 conserva el cálculo original, incluida cualquier duración negativa.
-- El cuaderno de Python documenta las validaciones del extracto para Power BI.

Use plataforma_cursos_aprendia;
-- 1. ¿Qué planes de suscripción generan más ingresos reales y cuál es su tasa de cobro exitoso?
SELECT
    pl.Id_plan,
    pl.Nombre AS plan,
    COUNT(DISTINCT s.Id_suscripcion) AS total_suscripciones,
    COUNT(p.Id_pago) AS total_pagos,
    SUM(CASE WHEN p.Estado = 'completado' THEN p.Monto ELSE 0 END) AS ingresos_reales,
    ROUND(
        100 * SUM(CASE WHEN p.Estado = 'completado' THEN 1 ELSE 0 END) / NULLIF(COUNT(p.Id_pago), 0),
        2
    ) AS tasa_pago_exitoso_pct
FROM Plan pl
LEFT JOIN Suscripcion s
    ON pl.Id_plan = s.Plan_id
LEFT JOIN Pago p
    ON s.Id_suscripcion = p.Suscripcion_id
GROUP BY pl.Id_plan, pl.Nombre
ORDER BY ingresos_reales DESC, tasa_pago_exitoso_pct DESC;

-- 2. ¿Qué docentes tienen mayor alcance internacional, medido por la diversidad de países de sus estudiantes?
SELECT
    pr.Id_usuario AS profesor_id,
    CONCAT(pr.Nombre, ' ', pr.Apellido) AS profesor,
    COUNT(DISTINCT c.Id_curso) AS cursos_publicados,
    COUNT(DISTINCT i.Usuario_id) AS estudiantes_unicos,
    COUNT(DISTINCT est.Pais) AS paises_alcanzados
FROM Usuario pr
INNER JOIN Curso c
    ON pr.Id_usuario = c.Profesor_id
INNER JOIN Inscripcion i
    ON c.Id_curso = i.Curso_id
INNER JOIN Usuario est
    ON i.Usuario_id = est.Id_usuario
WHERE pr.Rol = 'profesor'
  AND est.Rol = 'estudiante'
  AND c.Publicado = TRUE
GROUP BY pr.Id_usuario, profesor
ORDER BY paises_alcanzados DESC, estudiantes_unicos DESC, cursos_publicados DESC;

-- 3. ¿Las categorías con cursos más robustos en contenido logran mejores tasas de finalización?
WITH estructura_curso AS (
    SELECT
        c.Id_curso,
        c.Categoria,
        COUNT(DISTINCT m.Id_modulo) AS total_modulos,
        COUNT(DISTINCT l.Id_leccion) AS total_lecciones,
        COUNT(DISTINCT ml.Id_material) AS total_materiales
    FROM Curso c
    LEFT JOIN Modulo m
        ON c.Id_curso = m.Curso_id
    LEFT JOIN Leccion l
        ON m.Id_modulo = l.Modulo_id
    LEFT JOIN Material_leccion ml
        ON l.Id_leccion = ml.Leccion_id
    WHERE c.Publicado = TRUE
    GROUP BY c.Id_curso, c.Categoria
),
finalizacion_curso AS (
    SELECT
        i.Curso_id,
        COUNT(*) AS total_inscripciones,
        SUM(CASE WHEN i.Estado = 'completado' THEN 1 ELSE 0 END) AS total_completados,
        ROUND(
            100 * SUM(CASE WHEN i.Estado = 'completado' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
            2
        ) AS tasa_finalizacion_pct
    FROM Inscripcion i
    GROUP BY i.Curso_id
)
SELECT
    ec.Categoria,
    COUNT(DISTINCT ec.Id_curso) AS cursos_publicados,
    ROUND(AVG(ec.total_modulos), 2) AS promedio_modulos,
    ROUND(AVG(ec.total_lecciones), 2) AS promedio_lecciones,
    ROUND(AVG(ec.total_materiales), 2) AS promedio_materiales,
    ROUND(AVG(fc.tasa_finalizacion_pct), 2) AS promedio_tasa_finalizacion_pct
FROM estructura_curso ec
INNER JOIN finalizacion_curso fc
    ON ec.Id_curso = fc.Curso_id
GROUP BY ec.Categoria
ORDER BY promedio_tasa_finalizacion_pct DESC, promedio_materiales DESC;

-- 4. ¿Qué niveles educativos convierten mejor en certificados dentro de cada categoría de curso?
SELECT
    de.Nivel_educativo,
    c.Categoria,
    COUNT(DISTINCT i.Usuario_id, i.Curso_id) AS inscripciones,
    COUNT(DISTINCT ce.Usuario_id, ce.Curso_id) AS certificados_emitidos,
    ROUND(
        100 * COUNT(DISTINCT ce.Usuario_id, ce.Curso_id) / NULLIF(COUNT(DISTINCT i.Usuario_id, i.Curso_id), 0),
        2
    ) AS tasa_certificacion_pct
FROM Detalle_estudiante de
INNER JOIN Usuario u
    ON de.Usuario_id = u.Id_usuario
INNER JOIN Inscripcion i
    ON u.Id_usuario = i.Usuario_id
INNER JOIN Curso c
    ON i.Curso_id = c.Id_curso
LEFT JOIN Certificado ce
    ON i.Usuario_id = ce.Usuario_id
   AND i.Curso_id = ce.Curso_id
WHERE u.Rol = 'estudiante'
GROUP BY de.Nivel_educativo, c.Categoria
HAVING COUNT(DISTINCT i.Usuario_id, i.Curso_id) >= 5
ORDER BY tasa_certificacion_pct DESC, inscripciones DESC;

-- 5. ¿Qué categorías de cursos tardan más o menos tiempo en llevar a un estudiante desde la inscripción hasta la certificación?
SELECT
    c.Categoria,
    COUNT(*) AS total_certificaciones,
    ROUND(AVG(TIMESTAMPDIFF(DAY, i.Fecha_inscripcion, ce.Fecha_emision)), 2) AS promedio_dias_a_certificacion,
    MIN(TIMESTAMPDIFF(DAY, i.Fecha_inscripcion, ce.Fecha_emision)) AS minimo_dias,
    MAX(TIMESTAMPDIFF(DAY, i.Fecha_inscripcion, ce.Fecha_emision)) AS maximo_dias
FROM Certificado ce
INNER JOIN Inscripcion i
    ON ce.Usuario_id = i.Usuario_id
   AND ce.Curso_id = i.Curso_id
INNER JOIN Curso c
    ON ce.Curso_id = c.Id_curso
WHERE i.Fecha_inscripcion IS NOT NULL
  AND ce.Fecha_emision IS NOT NULL
GROUP BY c.Categoria
HAVING COUNT(*) >= 3
ORDER BY promedio_dias_a_certificacion ASC, total_certificaciones DESC;
