import json

class DB:
    def __init__(self):
        self.tables = {}
    
    def execute(self, statement: str):
        # executes the SQL statement
        parts = statement.split()
        verb = parts[0].upper()

        if verb == "CREATE":
            """
            eg: CREATE TABLE users (id INT PRIMARY_KEY, name VARCHAR)
            creates a new table in db with format 
            table_name = {
                "schema": {"col_name": "col_type"},
                "primary_key": key,
                "unique_keys": [],
                "rows": []
            }
            """
            table_name = parts[2]
            columns = statement.split('(')[1].strip(')')
            col_list = columns.split(',')
            
            schema = {}
            primary_key = None
            unique_keys = []

            for col in col_list:
                tokens = col.strip().split()
                col_name = tokens[0]
                col_type = tokens[1]

                schema[col_name] = col_type
                constraints = [t.upper() for t in tokens[2:]]
                print("constrinats", constraints)
                if "PRIMARY_KEY" in constraints:
                    if primary_key:
                        raise IndexError("Error: Multiple primary keys defined")
                    primary_key = col_name
                
                if "UNIQUE" in constraints:
                    unique_keys.append(col_name)
                self.tables[table_name] = {
                    "schema": schema,
                    "primary_key": primary_key,
                    "unique_keys": unique_keys,
                    "rows": []
                }
            return f"Table {table_name} created"
        
        # elif verb == "INSERT":
        #     table_name = parts[2]
        #     if table_name not in self.tables:
        #         return "Error: Table not found"
        #     table_structure = self.tables[table_name]
            
        #     raw_values = statement.split('VALUES')[1].strip().strip('()')
        #     values = [v.strip() for v in raw_values.split(',')]
        #     print(values)

        #     new_row = []

db = DB()
print(db.execute("CREATE TABLE users (id INT PRIMARY_KEY, name VARCHAR)"))
print(db.execute("INSERT INTO users VALUES (1, Pascal)"))