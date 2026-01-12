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
            if not len(parts) >= 4:
                return "Error: invalid command"
            table_name = parts[2]
            if table_name in self.tables:
                return "Error: table already exists"
            
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
            print(self.tables)
            return f"Table {table_name} created"
        
        elif verb == "INSERT":
            if not len(parts) > 4:
                return "Error: invalid command"
            if parts[3].upper() != "VALUES":
                return "Error: Invalid command"
            
            table_name = parts[2]
            if table_name not in self.tables:
                return "Error: Table not found"
            table_structure = self.tables[table_name]
            
            raw_values = statement.split('VALUES')[1].strip().strip('()')
            values = [v.strip() for v in raw_values.split(',')]
            
            # construct the new row
            new_row = {}
            col_names = list(table_structure['schema'].keys())
            for i, col in enumerate(col_names):
                new_row[col] = values[i]
            
            # check for constraints
            error = self._check_constraints(table_structure, new_row)
            if error:
                return error

            # commit
            table_structure['rows'].append(new_row)
            print(self.tables)
            return "Succes: data inserted in row"
        
        elif verb == "DELETE":
            if not len(parts) > 4:
                return "Error: invalid command"
            table_name = parts[2]
            if table_name not in self.tables:
                return "Error: table not found"
            
            try:
                where_part = statement.split('WHERE')[1].strip()
                target_col, target_val = where_part.split('=')
                target_col = target_col.strip()
                target_val = target_val.strip()
            except IndexError:
                return "Error: WHERE clause missing"
            
            rows = self.tables[table_name]['rows']
            initial_count = len(rows)
            
            # keep the rows that do not match the value
            self.tables[table_name]['rows'] = [
                row for row in rows
                if str(row.get(target_col)) != str(target_val)
            ]
            print(self.tables)
            deleted_count = initial_count - len(self.tables[table_name]['rows'])
            return f"Deleted {deleted_count} rows"
    
    def _check_constraints(self, table_structure, new_row):
        """
        Scans existing rows to ensure PK and Unique constraints are met.
        Returns None if safe, or an error string if violated.
        """
        pk_col = table_structure['primary_key']
        unique_cols = table_structure['unique_keys']
        existing_rows = table_structure['rows']

        # check against every existing row
        for row in existing_rows:
            # check for primary key
            if pk_col and str(row[pk_col]) == str(new_row[pk_col]):
                return f"Error: Duplicate primary key {new_row['pk_col']}"

        return None
