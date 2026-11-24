# Aprendia | Analítica de una plataforma educativa

[Read in English](README.en.md)

Aprendia fue un proyecto de fin de bootcamp sobre una plataforma de aprendizaje simulada. En un equipo de tres personas, analizamos **52.404 registros en 12 tablas** para entender las inscripciones, la finalización de cursos, las suscripciones y los ingresos.

## Mi aporte

Escribí consultas en MySQL, limpié y validé datos con Python y Pandas y construí vistas en Power BI para hacer seguimiento de esos indicadores. El repositorio reproduce una de mis consultas con un conjunto pequeño de datos sintéticos.

## ¿Cómo se comparan las suscripciones y los ingresos cobrados por plan?

Una suscripción puede tener varios intentos de pago. Al cruzar las tablas, cada intento genera una fila y la misma suscripción puede aparecer varias veces. La [consulta SQL](sql/plan_metrics.sql) agrupa suscripciones y pagos por separado antes de combinarlos por plan. Incluye los intentos pendientes en el total y suma el monto de los pagos completados.

| Plan | Suscripciones | Intentos de pago | Pagos completados | Ingresos cobrados¹ | % de intentos completados |
| --- | ---: | ---: | ---: | ---: | ---: |
| Annual | 1 | 1 | 1 | 90,00 | 100 % |
| Monthly | 2 | 4 | 2 | 24,00 | 50 % |
| Starter | 1 | 0 | 0 | 0,00 | — |
| Preview | 0 | 0 | 0 | 0,00 | — |

¹ Los montos están expresados en unidades monetarias ficticias. El guion indica que el porcentaje queda sin definir cuando el plan tiene cero intentos.

En el ejemplo, el plan mensual tiene más suscripciones y el anual recauda más. El porcentaje mide qué proporción de los **intentos de pago** terminó en un cobro. Una misma suscripción puede generar varios cobros debido a las renovaciones.

## Cómo reproducir el ejemplo

Desde la carpeta principal del repositorio, ejecuta el siguiente comando con Python 3. El programa usa SQLite, incluido en Python, verifica los resultados y luego imprime la tabla. La consulta también es compatible con MySQL 8.

```sh
python run_demo.py
```

El [esquema y los datos del ejemplo](sql/demo_data.sql) almacenan los montos en centavos enteros. El proyecto original se desarrolló con MySQL, Python y Power BI.
