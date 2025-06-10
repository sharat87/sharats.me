---
title: Gathering requirements for AI software products
status: draft
---

I was experimenting with building a small "AI Agent" with Python the other day. Made it a point to avoid using any
libraries or platforms to get a sense of what's happening.

So what's an AI Agent? To me, it's a piece of software that has LLM-driven autonomy. That's broad, and that's a
good thing. The agent communicates with an LLM, and the LLM decides what tool to call, what arguments to send to
the tool, what to do next, another tool call, or serve a report to the user, etc. The agent doesn't have autonomy
on its own, but it's driven by the LLM.

Great! So what tools? A friend suggested IT Asset management. Okay, but that's not an industry I was very close
with. No matter, I had AI generate a RDBMS schema for a hypothetical IT Asset Management system. With a bit of
back-and-forth, I got this:

```sql
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department TEXT,
    hire_date DATE NOT NULL
);

CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_type TEXT NOT NULL CHECK (asset_type IN ('Laptop', 'Mobile')),
    manufacturer TEXT,
    model TEXT,
    serial_number TEXT UNIQUE NOT NULL,
    purchase_date DATE,
    status TEXT DEFAULT 'Available' CHECK (status IN ('Assigned', 'Available', 'Repair', 'Retired'))
);

CREATE TABLE employee_assets (
    employee_asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    asset_id INTEGER,
    assignment_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE laptop_details (
    asset_id INTEGER PRIMARY KEY,
    processor TEXT,
    ram INTEGER,
    storage INTEGER,
    os TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE mobile_details (
    asset_id INTEGER PRIMARY KEY,
    os TEXT,
    storage INTEGER,
    imei TEXT UNIQUE,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);
```

And with a bit more persuading, I also got a lot of sample data for these tables. Close to ~100 rows spread over
all tables.

So I started off with Anthropic's HTTP API. I prepared two tools:

A tool function to run any "read" SQL query:

```python
async def run(query: str) -> list[dict[str, Any]]:
    """
    Runs any SQL query (SELECT, INSERT, UPDATE, DELETE) on the IT assets database

    Args:
        query: The SQL query to run on the IT assets database
    """

    conn = sqlite3.connect("it-assets.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(results, separators=(",", ":"))
```

And a tool function to run any "write" SQL query:

```python
async def run(query: str) -> str:
    """
    Run a write query on the IT assets database.

    Args:
        query: The SQL query to run on the IT assets database
    """

    conn = sqlite3.connect("it-assets.db")
    cursor = conn.cursor()
    cursor.executescript(query)
    conn.commit()
    conn.close()
    return "ok"
```

Wrapped them up in Anthropic's tool calling format, brought up a chat UI with Gradio, and I was ready to go.

> Who are the most recent five employees, and do they all have a phone?
