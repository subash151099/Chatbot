from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
import os
import pandas as pd

app = Flask(__name__)

#-----------------------------------------------------------------------------------------------------#
# SQLite3 database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
#-----------------------------------------------------------------------------------------------------#
# Create 'users' table if it doesn't exist
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Users table - 1
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    ''')
    # Updations table - 2
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS updations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            headline TEXT NOT NULL,
            message TEXT NOT NULL
        );
    ''')
    # Bot Keywords table - 3
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_key (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            message TEXT NOT NULL
        );
    ''')
    # Contact table - 4
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mail_id TEXT NOT NULL,
            skype TEXT NOT NULL,
            whatsapp TEXT NOT NULL,
            mobile TEXT NOT NULL
        );
    ''')
    # Leave table - 5
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            leave TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Call create_table() function
create_table()
#-----------------------------------------------------------------------------------------------------#
# Registration error
@app.route('/register_error')
def register_error():
    return "Invalid license number. Please try again."
#-----------------------------------------------------------------------------------------------------#
# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        license_number = request.form['license']
        LICENSE = "7867877418"
        # Check if the provided license matches the expected LICENSE
        if license_number == LICENSE:
            # Perform database operation to insert username and password
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()

            # Redirect to login page after successful registration
            return redirect(url_for('login'))
        
        else:
            # Redirect to register error page if license is incorrect
            return redirect(url_for('register_error'))
    
    # Render the registration form for GET requests
    return render_template('register.html')

#-----------------------------------------------------------------------------------------------------#
# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))

    return render_template('login.html')
#-----------------------------------------------------------------------------------------------------#

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))
#-----------------------------------------------------------------------------------------------------#
# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
#-----------------------------------------------------------------------------------------------------#
# chatbot code
# testing keywords


# Function to fetch response from SQLite database
def get_response_from_db(key):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT message FROM bot_key WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else "I'm sorry, I didn't understand that."

@app.route("/")
@app.route("/chat")
def index():
    messages = fetch_messages() # updations message connection
    return render_template('chat.html', messages=messages)

@app.route("/get", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        msg = request.form["msg"]
        response = get_response_from_db(msg.lower())
        return response
    return "Invalid Request"


#-----------------------------------------------------------------------------------------------------#
# sub options in admin dashboard

# Updations table SP
@app.route("/news_updation")
def news_updation():
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("select * from updations")
    data=cur.fetchall()
    return render_template('news_updation.html', username=session['username'],datas=data)

@app.route("/add_news_updation",methods=['POST','GET']) 
def add_news_updation():
    if request.method=='POST':
        date=request.form['date']
        time=request.form['time']
        headline=request.form['headline']
        message=request.form['message']
        con=sqlite3.connect("database.db")
        cur=con.cursor()
        cur.execute("insert into updations(date,time,headline,message) values (?,?,?,?)",(date,time,headline,message))
        con.commit()
        return redirect(url_for("news_updation"))
    return render_template("add_news_updation.html")


@app.route("/edit_news_updation/<string:id>",methods=['POST','GET'])
def edit_news_updation(id):
    if request.method=='POST':
        date=request.form['date']
        time=request.form['time']
        headline=request.form['headline']
        message=request.form['message']
        con=sqlite3.connect("database.db")
        cur=con.cursor()
        cur.execute("update updations set date=?,time=?,headline=?,message=? where ID=?",(date,time,headline,message,id))
        con.commit()
        return redirect(url_for("news_updation"))
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("select * from updations where ID=?",(id,))
    data=cur.fetchone()
    return render_template("edit_news_updation.html",datas=data)
    
@app.route("/delete_news_updation/<string:id>",methods=['GET'])
def delete_news_updation(id):
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("delete from updations where ID=?",(id,))
    con.commit()
    return redirect(url_for("news_updation"))

#-----------------------------------------------------------------------------------------------------#
# bot_key table SP
@app.route("/botkeyword_updation")
def botkeyword_updation():
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("select * from bot_key")
    data=cur.fetchall()
    return render_template('botkeyword_updation.html', username=session['username'],datas=data)

@app.route("/add_botkeyword_updation",methods=['POST','GET']) 
def add_botkeyword_updation():
    if request.method=='POST':
        key=request.form['key']
        message=request.form['message']
        con=sqlite3.connect("database.db")
        cur=con.cursor()
        cur.execute("insert into bot_key(key, message) values (?,?)",(key, message))
        con.commit()
        return redirect(url_for("botkeyword_updation"))
    return render_template("add_botkeyword_updation.html")


@app.route("/edit_botkeyword_updation/<string:id>",methods=['POST','GET'])
def edit_botkeyword_updation(id):
    if request.method=='POST':
        key=request.form['key']
        message=request.form['message']
        con=sqlite3.connect("database.db")
        cur=con.cursor()
        cur.execute("update bot_key set key=?,message=? where ID=?",(key,message,id))
        con.commit()
        return redirect(url_for("botkeyword_updation"))
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("select * from bot_key where ID=?",(id,))
    data=cur.fetchone()
    return render_template("edit_botkeyword_updation.html",datas=data)
    
@app.route("/delete_botkeyword_updation/<string:id>",methods=['GET'])
def delete_botkeyword_updation(id):
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("delete from bot_key where ID=?",(id,))
    con.commit()
    return redirect(url_for("botkeyword_updation"))

#-----------------------------------------------------------------------------------------------------#
@app.route("/contact_updation")
def contact_updation():
    return render_template('contact_updation.html', username=session['username'])
#-----------------------------------------------------------------------------------------------------#
@app.route("/leave_calendar")
def leave_calendar():
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("select * from leave")
    data=cur.fetchall()
    return render_template('leave_calendar.html', username=session['username'],datas=data)

@app.route("/add_leave_calendar",methods=['POST','GET']) 
def add_leave_calendar():
    if request.method=='POST':
        date=request.form['date']
        leave=request.form['leave']
        con=sqlite3.connect("database.db")
        cur=con.cursor()
        cur.execute("insert into leave(date,leave) values (?,?)",(date,leave))
        con.commit()
        return redirect(url_for("leave_calendar"))
    return render_template("add_leave_calendar.html")


@app.route("/edit_leave_calendar/<string:id>",methods=['POST','GET'])
def edit_leave_calendar(id):
    if request.method=='POST':
        date=request.form['date']
        leave=request.form['leave']
        con=sqlite3.connect("database.db")
        cur=con.cursor()
        cur.execute("update leave set date=?,leave=? where ID=?",(date,leave,id))
        con.commit()
        return redirect(url_for("leave_calendar"))
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("select * from leave where ID=?",(id,))
    data=cur.fetchone()
    return render_template("edit_leave_calendar.html",datas=data)
    
@app.route("/delete_leave_calendar/<string:id>",methods=['GET'])
def delete_leave_calendar(id):
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("delete from leave where ID=?",(id,))
    con.commit()
    return redirect(url_for("leave_calendar"))

#-----------------------------------------------------------------------------------------------------#
@app.route("/profile_updation")
def profile_updation():
    return render_template('profile_updation.html', username=session['username'])

#-----------------------------------------------------------------------------------------------------#

@app.route("/contactpage")
def contactpage():
    return render_template('contactpage.html')
#-----------------------------------------------------------------------------------------------------#
@app.route("/calendarpage")
def calendarpage():
    # Fetch data from SQLite database (example query)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT date, leave FROM leave")
    events = c.fetchall()
    conn.close()
    return render_template('calendarpage.html', events=events)
#-----------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------#
# Messages & Headline (Date, Time)

# Function to fetch messages from SQLite database
def fetch_messages():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT headline, date, time, message FROM updations')
    messages = cursor.fetchall()
    conn.close()
    return messages



#-----------------------------------------------------------------------------------------------------#
# bot key bulk upload (excel upload option)
DATABASE='database.db'
# Function to connect to SQLite database
def get_db():
    db = sqlite3.connect(DATABASE)
    return db

# Upload route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)
            conn = get_db()
            cursor = conn.cursor()

            # Assuming the Excel file has 'keyword' and 'data' columns
            for index, row in df.iterrows():
                key = row['key']
                message = row['message']

                # Check if keyword exists in the database
                cursor.execute("SELECT * FROM bot_key WHERE key=?", (key,))
                existing_data = cursor.fetchone()

                if existing_data:
                    # Keyword exists, replace the data
                    cursor.execute("UPDATE bot_key SET message=? WHERE key=?", (message, key))
                else:
                    # Keyword doesn't exist, insert new data
                    cursor.execute("INSERT INTO bot_key (key, message) VALUES (?, ?)", (key, message))
            
            conn.commit()
            conn.close()

            return 'File uploaded successfully'

    return render_template('upload.html', username=session['username'])

#-----------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------#


#-----------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    app.secret_key='admin123'
    app.run(debug=True)
