from contextlib import closing
from pathlib import Path
import sqlite3


def main():
    sql_dir = Path(__file__).resolve().parent / "sql"
    seed = (sql_dir / "demo_data.sql").read_text(encoding="utf-8")
    query = (sql_dir / "plan_metrics.sql").read_text(encoding="utf-8")

    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript(seed)
        rows = db.execute(query).fetchall()

    expected = [
        ("Annual", 1, 1, 1, 9000, 100.0),
        ("Monthly", 2, 4, 2, 2400, 50.0),
        ("Starter", 1, 0, 0, 0, None),
        ("Preview", 0, 0, 0, 0, None),
    ]
    if rows != expected:
        raise ValueError(f"Unexpected plan metrics: {rows!r}")

    print("Plan       Subs  Attempts  Completed  Collected  Completed share")
    for plan, subscriptions, attempts, completed, cents, share in rows:
        share_label = f"{share:.2f}%" if share is not None else "n/a"
        print(f"{plan:<10} {subscriptions:>4} {attempts:>9} {completed:>10} {cents / 100:>10.2f} {share_label:>16}")


if __name__ == "__main__":
    main()
