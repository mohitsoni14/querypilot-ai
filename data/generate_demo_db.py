from __future__ import annotations

import sqlite3
from pathlib import Path


SQL = """
PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS enrolment;
DROP TABLE IF EXISTS schools;
DROP TABLE IF EXISTS districts;
DROP TABLE IF EXISTS academic_years;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
CREATE TABLE districts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, region TEXT NOT NULL);
CREATE TABLE schools (id INTEGER PRIMARY KEY, name TEXT NOT NULL, district_id INTEGER NOT NULL REFERENCES districts(id), opened_year INTEGER);
CREATE TABLE academic_years (id INTEGER PRIMARY KEY, label TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, is_complete INTEGER NOT NULL DEFAULT 1);
CREATE TABLE enrolment (id INTEGER PRIMARY KEY, school_id INTEGER NOT NULL REFERENCES schools(id), academic_year_id INTEGER NOT NULL REFERENCES academic_years(id), enrolled_count INTEGER, new_admissions TEXT, as_of_date TEXT, source_note TEXT);
CREATE TABLE customers (id INTEGER PRIMARY KEY, full_name TEXT, email TEXT, region TEXT, created_at TEXT);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, unit_price REAL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id), order_date TEXT, status TEXT);
CREATE TABLE order_items (id INTEGER PRIMARY KEY, order_id INTEGER REFERENCES orders(id), product_id INTEGER REFERENCES products(id), quantity INTEGER, revenue REAL);
"""


def build_database(path: str | Path = "data/demo.db") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target)
    conn.executescript(SQL)
    conn.executemany("INSERT INTO districts VALUES (?, ?, ?)", [(1, "North Coast", "Coastal"), (2, "Central Plains", "Central"), (3, "Pine Valley", "Mountain"), (4, "River East", "Eastern")])
    conn.executemany("INSERT INTO schools VALUES (?, ?, ?, ?)", [(1, "Harbor View High", 1, 1998), (2, "Bayridge Academy", 1, 2004), (3, "Cedar Grove School", 2, 1987), (4, "Prairie Star School", 2, 2010), (5, "Pinecrest School", 3, 1975), (6, "Summit Ridge School", 3, 2001), (7, "Riverside Prep", 4, 1992), (8, "Eastbank School", 4, 2016)])
    conn.executemany("INSERT INTO academic_years VALUES (?, ?, ?, ?, ?)", [(1, "2021-22", "2021-09-01", "2022-06-30", 1), (2, "2022-23", "2022-09-01", "2023-06-30", 1), (3, "2023-24", "2023-09-01", "2024-06-30", 1), (4, "2024-25", "2024-09-01", "2025-06-30", 1), (5, "2025-26", "2025-09-01", "2026-06-30", 0)])
    rows=[]
    counts={1:[820,790,735,690],2:[610,605,580,560],3:[1040,1015,1008,1022],4:[480,500,520,550],5:[730,710,680,640],6:[420,430,410,395],7:[890,870,845,810],8:[360,370,390,420]}
    idx=1
    for school_id, values in counts.items():
        for year_id, count in zip((1,2,3,4), values):
            rows.append((idx, school_id, year_id, count, str(round(count*.28)), f"{2022+year_id-1}-06-30", "synthetic demo")); idx += 1
    rows.append((idx, 1, 4, 690, "N/A", "2025/06/30", "duplicate-like demo record"))
    conn.executemany("INSERT INTO enrolment VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", [(1,"Alex Morgan","alex@example.com","Coastal","2024-01-03"),(2,"Alex Morgan","alex@example.com","Coastal","2024-01-03"),(3,"Jamie Lee","jamie@example.com","Central","2024-02-15"),(4,"Riley Chen","N/A","Mountain","2024-03-20"),(5,"Sam Patel","sam@example.com","Eastern","bad-date")])
    conn.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", [(1,"Notebook","Stationery",8.5),(2,"Backpack","Accessories",42.0),(3,"Desk Lamp","Workspace",28.0),(4,"Planner","Stationery",14.0)])
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", [(1,1,"2024-01-12","complete"),(2,3,"2024-02-16","complete"),(3,4,"2024-03-21","complete"),(4,5,"2024-04-05","cancelled"),(5,2,"2025-01-10","complete")])
    conn.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", [(1,1,1,12,102.0),(2,1,2,2,84.0),(3,2,3,4,112.0),(4,3,4,8,112.0),(5,4,2,1,42.0),(6,5,1,7,59.5)])
    conn.commit(); conn.close(); return target


if __name__ == "__main__":
    print(build_database())
