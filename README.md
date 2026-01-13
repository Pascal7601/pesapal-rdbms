# MiniRDBMS & Notepad App

A lightweight, file-based Relational Database Management System (RDBMS) implemented from scratch in pure Python.

This project was built to satisfy the Pesapal Engineering Challenge. It demonstrates the implementation of a core database engine with support for schemas, typing, constraints, and joins, decoupled from its interfaces (REPL and Web).

## 🏗 Architecture

The system follows a modular architecture separating the **Storage Engine** from the **User Interface**.



* **`db.py` (The Engine):** The core library. It parses custom SQL commands, handles data validation (Schema on Write), enforces constraints (Primary/Unique Keys), and manages persistence to `data.json`.
* **`interface.py` (Interface 1):** An interactive Read-Eval-Print-Loop for administrative database access.
* **`app.py` (Interface 2):** A Flask web application ("Notepad") that utilizes `db.py` to demonstrate practical CRUD usage.

## 🚀 Features

* **Custom SQL Parser:** Understands `CREATE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`.
* **Data Persistence:** Automatically saves and loads state using JSON.
* **Schema & Typing:** Enforces `INT` and `TEXT` types upon insertion.
* **Constraints:** Supports `PRIMARY_KEY` (integrity) and `UNIQUE` constraints.
* **Relational Joins:** Implements Nested Loop Joins to combine data from multiple tables.
* **Indexing:** Uses Python dictionary hashmaps for O(1) primary key lookups.

## 📦 Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/Pascal7601/pesapal-rdbms.git](https://github.com/Pascal7601/pesapal-rdbms.git)
    cd pesapal-rdbms
    ```

2.  **Install Dependencies**
    The Core Engine has **zero dependencies**. You only need Flask for the demo web app.
    ```bash
    pip install flask
    ```

3.  **Run the Web App (Demo)**
    ```bash
    python app.py
    ```
    Open `http://127.0.0.1:8000` in your browser. The database will automatically initialize `data.json` and the `notes` table on the first run.

4.  **Run the REPL (Admin Tool)**
    ```bash
    python interface.py
    ```

## 📂 Project Structure

```text
/pesapal-rdbms
  ├── db.py            # The Database Engine (Core Logic)
  ├── repl.py          # Interactive Terminal (Admin Tool)
  ├── app.py           # Notepad Web Application (Demo)
  ├── data.json        # Persistent Storage (Auto-generated)
  ├── README.md        # Documentation
  └── templates/
       └── index.html  # Frontend for the Notepad App
## 📖 Supported SQL Syntax
```

The engine supports a subset of SQL.

### Create Table
```sql
CREATE TABLE notes (id INT PRIMARY_KEY, title TEXT, content TEXT)
```

### Insert Data Note: Values must be comma-separated.
```sql
INSERT INTO notes VALUES (1, My_First_Note, This_is_content)
```

### Select Data
```sql
SELECT * FROM notes
```
### Update Data
```sql
UPDATE notes SET content=Updated_Content WHERE id=1
```

### Delete Data
```sql
DELETE FROM notes WHERE id=1
```

## ⚠️ Known Limitations
- In the spirit of the "trivial" implementation challenge, the following simplifications were made:

1. Tokenizer Constraints: The parser relies on basic string splitting. Strings with spaces are not supported.

- Incorrect: Buy Milk

- Correct: Buy_Milk

2. Concurrency: The system is single-threaded. Concurrent writes to the JSON store are not locked, which is acceptable for a prototype but not production.

3. Operator Support: WHERE clauses currently support simple equality (col=val) only.