from flask import Flask, render_template, request, redirect, url_for
from db import DB

app = Flask(__name__)
db = DB()

def setup_db():
    """Ensure the notes tables exists on startup"""
    result = db.execute("SELECT * FROM notes")
    print("debug setup_db() ", result)
    if not result:
        print("Initializing database......")
        db.execute("CREATE TABLE notes (id INT PRIMARY_KEY,title TEXT,content TEXT)")

@app.route('/')
def index():
    """Get all notes to display"""
    notes = db.execute("SELECT * FROM notes")

    # If the DB returns a raw list, we pass it to HTML.
    # If it returns an error string (e.g., table empty), we pass an empty list.
    if isinstance(notes, str):
        notes = []
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['POST'])
def add_note():
    # CREATE: Insert a new note
    title = request.form['title']
    content = request.form['content']

    # Auto-increment logic
    # Get current notes to find the highest ID
    current_notes = db.execute("SELECT * FROM notes")
    if isinstance(current_notes, list) and len(current_notes) > 0:
        new_id = int(current_notes[-1]['id']) + 1
    else:
        new_id = 1
    
    # Construct the query string
    query = f"INSERT INTO notes VALUES ({new_id}, {title}, {content})"
    result = db.execute(query)
    print(result)
    return redirect(url_for('index'))

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_node(note_id):
    # DELETE; Remove a note by their id
    query = f"DELETE FROM notes WHERE id={note_id}"
    db.execute(query)
    return redirect(url_for('index'))

@app.route('/update/<int:note_id>', methods=['POST'])
def update_note(note_id):
    # UPDATE a note with new values
    content = request.form['content']
    query = f"UPDATE notes SET content={content} WHERE id={note_id}"
    db.execute(query)
    return redirect(url_for('index'))


if __name__ == '__main__':
    setup_db()
    app.run(debug=True, port=8000)