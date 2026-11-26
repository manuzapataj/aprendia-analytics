# Aprendia | Analítica de una plataforma educativa

[Read in English](README.en.md)

Aprendia fue un proyecto de fin de bootcamp sobre una plataforma de aprendizaje simulada. Analizamos cómo las inscripciones se convertían en cursos finalizados y certificados, y qué planes generaban los ingresos cobrados.

## Explora el proyecto

| Material | Qué puedes revisar |
| --- | --- |
| [Cuaderno de análisis en Python](analisis_aprendia.ipynb) | Controles de claves, recorrido del estudiante, cálculo de ingresos y conciliación con el informe final. |
| [Cinco preguntas de negocio en MySQL](sql/preguntas_negocio_mysql.sql) | Consultas del bootcamp sobre planes, docentes, estructura de cursos, certificación y tiempo hasta el certificado. |
| [Tablero de Power BI y medidas DAX](docs/power_bi.md) | Capturas de la presentación final, relaciones del modelo y medidas de seguimiento. |
| [Script de preparación](preparar_agregados.py) | Código en Python y Pandas que transforma el Excel original en el [extracto agregado](datos/corte_agregado.json). |

## Resultados en el extracto de Power BI

- **12.833 inscripciones**, con **25,2 %** finalizadas y **1.617 certificados** en la plataforma simulada.
- **USD 142.671,64 cobrados** en pagos completados. Empresarial concentró **38,7 %** del importe cobrado con **5,5 %** de las suscripciones.
- La auditoría del extracto detectó **2.663 lecciones sin módulo correspondiente** y una certificación anterior a la inscripción. El cuaderno documenta cómo afectan estas diferencias al análisis de contenido y de duración.

El informe de entrega consigna **52.404 filas**. El [cuaderno](analisis_aprendia.ipynb) verifica **51.961** en las 12 tablas del Excel de Power BI y muestra la conciliación con el informe.

## Mi aporte

Escribí consultas en MySQL, limpié y validé datos con Python y Pandas y construí vistas en Power BI para hacer seguimiento de esos indicadores. El trabajo académico se realizó en equipo con Astrid Rodríguez y Valerie Avendaño.

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

Para revisar los resultados del proyecto, abre el [cuaderno](analisis_aprendia.ipynb) desde la raíz del repositorio en Jupyter con Python y Pandas. El cuaderno usa el agregado incluido. El script permite recalcularlo si tienes el Excel del proyecto.

```sh
python -m pip install -r requirements.txt
python preparar_agregados.py ruta/PowerBI_Aprendia_Paquete.xlsx
```
