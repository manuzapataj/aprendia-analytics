# Aprendia | E-learning analytics

[Leer en español](README.md)

Aprendia is a team capstone on a simulated e-learning platform. Our team of three analyzed 52,404 records across 12 tables to understand enrollment, course completion, subscriptions and revenue.

## My contribution

I wrote MySQL queries for business questions, used Python and Pandas to clean and validate data, and built Power BI views for enrollment, completion, subscriptions and revenue. This repository illustrates one of my queries with a small synthetic dataset.

## How do subscription volume and collected revenue compare across plans?

A subscription can have several payment attempts. Joining plans, subscriptions and payments creates one row per attempt, which can inflate subscription counts. The [query](sql/plan_metrics.sql) aggregates subscriptions and payments separately at plan level before combining the results. It counts all recorded attempts, including pending ones, and adds amounts only for completed payments. Plans with zero attempts have an undefined completion percentage.

| Plan | Subscriptions | Payment attempts | Completed payments | Collected amount¹ | Completed share |
| --- | ---: | ---: | ---: | ---: | ---: |
| Annual | 1 | 1 | 1 | 90.00 | 100% |
| Monthly | 2 | 4 | 2 | 24.00 | 50% |
| Starter | 1 | 0 | 0 | 0.00 | — |
| Preview | 0 | 0 | 0 | 0.00 | — |

¹ Synthetic currency units. These figures illustrate the calculation.

In the example, Monthly has more subscriptions than Annual, while Annual collects more revenue. The completion percentage uses payment attempts as its denominator. A renewal can produce more than one completed payment for the same subscription, so this percentage describes payment activity rather than subscriber conversion.

## Run the example

Run this command from the repository root with Python 3. The script uses SQLite from the Python standard library and checks the results before printing the table. The query also uses syntax compatible with MySQL 8.

```sh
python run_demo.py
```

The included [schema and data](sql/demo_data.sql) are synthetic. Amounts are stored as integer cents. The original project was built with MySQL, Python and Power BI.
