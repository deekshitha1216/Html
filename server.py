from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_database_connection():
    connection = sqlite3.connect("employee.db")
    connection.row_factory = sqlite3.Row
    return connection


# =========================================================
# CREATE TABLES
# =========================================================

def create_table():

    connection = get_database_connection()
    cursor = connection.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # EMPLOYEES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL,
            joining_date TEXT NOT NULL,
            address TEXT
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("navbar.html")


# =========================================================
# EMPLOYEE LIST
# =========================================================

@app.route("/employee")
def employee():

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        ORDER BY id DESC
    """)

    employee_list = cursor.fetchall()

    connection.close()

    return render_template(
        "employee.html",
        employees=employee_list
    )


# =========================================================
# ADD EMPLOYEE
# =========================================================

@app.route("/add-employee", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        department = request.form.get("department")
        salary = request.form.get("salary")
        joining_date = request.form.get("joining_date")
        address = request.form.get("address")

        # Check required fields
        if not name or not email or not phone or not department:
            return "Please fill all required fields!"

        connection = get_database_connection()
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO employees
                (
                    name,
                    email,
                    phone,
                    department,
                    salary,
                    joining_date,
                    address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                phone,
                department,
                salary,
                joining_date,
                address
            ))

            connection.commit()

        except Exception as e:

            connection.rollback()
            connection.close()

            return "Error adding employee: " + str(e)

        connection.close()

        return redirect(url_for("employee"))

    return render_template("add-employee.html")


# =========================================================
# EDIT EMPLOYEE
# =========================================================

@app.route("/edit-employee/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    connection = get_database_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        department = request.form.get("department")
        salary = request.form.get("salary")
        joining_date = request.form.get("joining_date")
        address = request.form.get("address")

        cursor.execute("""
            UPDATE employees
            SET
                name = ?,
                email = ?,
                phone = ?,
                department = ?,
                salary = ?,
                joining_date = ?,
                address = ?
            WHERE id = ?
        """, (
            name,
            email,
            phone,
            department,
            salary,
            joining_date,
            address,
            id
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("employee"))

    cursor.execute("""
        SELECT *
        FROM employees
        WHERE id = ?
    """, (id,))

    employee_data = cursor.fetchone()

    connection.close()

    if not employee_data:
        return "Employee not found!"

    return render_template(
        "edit-employee.html",
        employee=employee_data
    )


# =========================================================
# DELETE EMPLOYEE
# =========================================================

@app.route("/delete-employee/<int:id>", methods=["POST", "GET"])
def delete_employee(id):

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM employees
        WHERE id = ?
    """, (id,))

    connection.commit()
    connection.close()

    return redirect(url_for("employee"))


# =========================================================
# SEARCH
# =========================================================

@app.route("/search")
def search():
    return render_template("search.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form.get("fullname")
        username = request.form.get("username")
        password = request.form.get("password")

        if not fullname or not username or not password:
            return "Please fill all fields!"

        connection = get_database_connection()
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO users
                (
                    fullname,
                    username,
                    password
                )
                VALUES (?, ?, ?)
            """, (
                fullname,
                username,
                password
            ))

            connection.commit()

        except sqlite3.IntegrityError:

            connection.close()

            return "Username already exists!"

        connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username = ?
            AND password = ?
        """, (
            username,
            password
        ))

        user = cursor.fetchone()

        connection.close()

        if user:
            return "Login successful! Welcome " + user["fullname"]

        return "Invalid username or password!"

    return render_template("login.html")    


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    create_table()

    app.run(debug=True)