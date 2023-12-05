from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, render_template, request, Blueprint
from flask import Flask, session
import psycopg2
import datetime
rgz = Blueprint("rgz", __name__)

def dbConnect():
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="knowledge_base2",
        user="kramar_knowledge_base",
        password="000")

    return conn; 

def dbClose(cursor, connection):
    cursor.close()
    connection.close()

@rgz.route("/rgz")
def main():
    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users;")

    result = cur.fetchall()

    print(result)

    dbClose(cur, conn)
    
    return "go to console" 

@rgz.route("/rgz/glavn") 
def glavn (): 
    visibleUser = "Anon" 
 
    if 'username' in session: 
        visibleUser = session['username'] 
    
    return render_template('glavn.html', username=visibleUser)


@rgz.route("/rgz/users") 
def users (): 
    # Прописываем параметры подключения к БД 
    conn = dbConnect() 
    cur = conn.cursor() 
 
    cur.execute("SELECT * FROM users;") 
 
    result = cur.fetchall() 
 
    names = [row[1] for row in result] 
 
    dbClose(cur, conn) 
 
    return render_template('users.html', names = names)

@rgz.route("/rgz/register", methods=["GET", "POST"])
def registerPage():
    errors = {}

    visibleUser = "Anon"

    if 'username' in session:
        visibleUser = session['username']

    if request.method == "GET":
        return render_template("register.html", username=visibleUser)

    username = request.form.get("username")
    login = request.form.get("login")
    password = request.form.get("password")

    if username == '' or login == '' or password == '':
        errors = "Заполните поля"
        return render_template("register.html", errors=errors, username=visibleUser)

    hashPassword = generate_password_hash(password)
    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT username, login FROM users WHERE username = %s;", (username,
    ))

    if cur.fetchone() is not None:
        errors = "Пользователь уже существут"
        dbClose(cur, conn)
        return render_template("register.html", errors=errors, username=visibleUser)

    cur.execute(f"INSERT INTO users (username, login, password) VALUES (%s, %s, %s);", (username, login, hashPassword))

    conn.commit()
    dbClose(cur, conn)

    return redirect("/rgz/login")

@rgz.route("/rgz/login", methods=["GET", "POST"])
def loginPage():
    errors = []

    visibleUser = "Anon"

    if 'username' in session:
        visibleUser = session['username']

    if request.method == "GET":
        return render_template("login2.html", username=visibleUser)

    username = request.form.get("username")
    login = request.form.get("login")
    password = request.form.get("password")

    if username == '' or login == '' or password == '':
        errors = "Заполните поля"
        return render_template("login2.html", errors=errors, username=visibleUser)

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM users WHERE username = %s;", (username,))

    result = cur.fetchone()

    if result is None:
        errors = "Неправильный логин, имя пользователя или пароль"
        dbClose(cur, conn)
        return render_template("login2.html", errors=errors, username=visibleUser)
    
    userID, hashPassword = result

    if check_password_hash(hashPassword, password):
        session['id'] = userID
        session['username'] = username
        dbClose(cur,conn)
        return redirect("/rgz/glavn")
    else:
        errors = "Неправильный логин или пароль"
        return render_template("login2.html", errors=errors, username=visibleUser)