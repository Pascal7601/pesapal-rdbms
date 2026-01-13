import json
import os

class DB:
    def __init__(self, filename='notes.json'):
        self.tables = {}
        self.filename = filename
        self.load()
    
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
            self.save()
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
            self.save()
            return "Succes: data inserted in row"
        
        elif verb == "DELETE":
            # Command: DELETE FROM users WHERE id=1
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
            self.save()
            return f"Deleted {deleted_count} rows"
        
        elif verb == "UPDATE":
            # Command: UPDATE users SET email=new@test.com WHERE id=1
            if not len(parts) > 4:
                return "Error: invalid command"
            table_name = parts[1]
            if table_name not in self.tables:
                return "Error: table not found"
            try:
                val_change_part = statement.split('SET')[1] # email=new@test.com WHERE id=1
                set_clause, where_clause = val_change_part.split('WHERE') # ['email=new@test.com', 'id=1']

                # parse SET: What to change
                set_col, set_val = set_clause.split('=') # ['email', 'new@test.com']
                set_col = set_col.strip()
                set_val = set_val.strip()
                print("set col ", set_col)
                print("set_val ", set_val)
                #parse WHERE: who to change
                where_col, where_val = where_clause.split('=') # ['id', '1']
                where_col = where_col.strip()
                where_val = where_val.strip()
                print("where_col ", where_col)
                print("where_val ", where_val)
            except ValueError:
                return "Error: Command syntax error. Use UPDATE table SET col=val WHERE col=val"
            
            rows = self.tables[table_name]['rows']
            updated_count = 0

            for row in rows:
                if str(row.get(where_col)) == str(where_val):

                    row[set_col] = set_val
                    updated_count += 1
            print(self.tables)
            self.save()
            return f"Updated {updated_count} rows"
        
        elif verb == "SELECT":
            # Command: SELECT * FROM users JOIN posts ON users.id=posts.user_id
            if "JOIN " in statement:
                try:
                    # Get everything after FROM
                    from_part = statement.split('FROM')[1].strip()
                    left_table_name, rest = from_part.split(' JOIN ') # ['users', 'posts ON users.id=posts.user_id']
                    right_table_name, on_clause = rest.split(' ON ') # ['posts', 'users.id=posts.user_id']

                    left_operand, right_operand = on_clause.strip().split('=') # ['users.id', 'posts.user_id']

                    # helper to extract table and its coresponding column from the right and left operands
                    def extract(operand):
                        table, col = operand.strip().split('.')
                        return table, col
                    
                    left_tbl_ref, left_col_ref = extract(left_operand)
                    right_tbl_ref, right_col_ref = extract(right_operand)

                except ValueError:
                    return "Error: Syntax error. Use SELECT * FROM table1 JOIN table2 ON t1.c1=t2.c2"
                
                if left_table_name not in self.tables or right_table_name not in self.tables:
                    return "Error: One of the tables do not exist"
                
                left_rows = self.tables[left_table_name]['rows']
                right_rows = self.tables[right_table_name]['rows']
                results = []

                for l_row in left_rows:
                    for r_row in right_rows:
                        # check which side of the '=' applies to which row
                        l_val = None
                        r_val = None
                        
                        # Resolve left operand value
                        if left_tbl_ref == left_table_name:
                            l_val = l_row.get(left_col_ref)
                        else:
                            l_val = r_row.get(left_col_ref)
                            
                        # Resolve right operand value
                        if right_tbl_ref == right_table_name:
                            r_val = r_row.get(right_col_ref)
                        else:
                            r_val = l_row.get(right_col_ref)

                        # The Match Condition
                        # Convert to strings for safe comparison
                        if str(l_val) == str(r_val):
                            # MERGE THE ROWS
                            # create a new dict combining both.
                            # Note: If columns have same names (like 'id'), the second one overwrites.
                            joined_row = {**l_row, **r_row}
                            results.append(joined_row)
                return results
            else:
                # Command: SELECT * FROM users
                parts = statement.split()
                table_name = parts[3]
                return self.tables.get(table_name, {}).get('rows', [])
            
    
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
                return f"Error: Duplicate primary key {new_row[pk_col]}"
    
    def load(self):
        """loads data from disk"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.tables = json.load(f)
            except json.JSONDecodeError:
                self.tables = {}
        else:
            self.tables = {}
    
    def save(self):
        """Saves data to disk"""
        with open(self.filename, 'w') as f:
            json.dump(self.tables, f, indent=4)

        return None
