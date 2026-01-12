from db import DB

def interface():
    db = DB()
    db.execute("CREATE TABLE users (id INT PRIMARY_KEY, name VARCHAR)")
    db.execute("INSERT INTO users VALUES (1, Pascal)")
    print('Welcome to my custom db\ntype exit to break out of the interface')
    while True:
        user_input = input('db> ')
        if user_input == 'exit':
            break
        result = db.execute(user_input)
        print(result)

if __name__ == "__main__":
    interface()