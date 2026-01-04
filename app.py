import os
import time
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from MySQLdb import OperationalError

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'root')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'devops')

mysql = MySQL(app)


def init_db():
    retries = 5
    while retries > 0:
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message TEXT
                );
            """)
            mysql.connection.commit()
            cur.close()
            print("Database initialized")
            return
        except OperationalError:
            retries -= 1
            print("Waiting for MySQL...")
            time.sleep(5)

    raise Exception("MySQL not ready after retries")


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT message FROM messages")
    messages = cur.fetchall()
    cur.close()
    return render_template("index.html", messages=messages)


@app.route('/submit', methods=['POST'])
def submit():
    message = request.form.get("new_message")
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (message) VALUES (%s)", [message])
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": message})


# Required for Docker & Jenkins
@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)