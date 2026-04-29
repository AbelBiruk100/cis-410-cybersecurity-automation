import os
import socket
import datetime
import sqlite3
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
DEPLOY_TIME = os.environ.get("DEPLOY_TIME", "unknown")
COMMIT_SHA = os.environ.get("COMMIT_SHA", "local")
BRANCH = os.environ.get("BRANCH", "main")
WORKFLOW = os.environ.get("WORKFLOW", "deploy-dev.yml")


@app.route("/")
def index():
    context = {
        "version": APP_VERSION,
        "env": ENVIRONMENT,
        "hostname": socket.gethostname(),
        "deploy_time": DEPLOY_TIME,
        "commit_sha": COMMIT_SHA[:7] if len(COMMIT_SHA) > 7 else COMMIT_SHA,
        "branch": BRANCH,
        "workflow": WORKFLOW,
        "port": "5000",
    }
    return render_template("index.html", **context)


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "version": APP_VERSION,
        "env": ENVIRONMENT,
        "host": socket.gethostname(),
        "time": datetime.datetime.utcnow().isoformat() + "Z",
    })


@app.route("/search")
def search():
    query = request.args.get("q", "")

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            role TEXT
        )
    """)

    cursor.executemany("""
        INSERT INTO users (name, role) VALUES (?, ?)
    """, [
        ("Alice", "Admin"),
        ("Bob", "Developer"),
        ("Charlie", "Security Analyst"),
        ("Diana", "QA Tester"),
        ("Ethan", "DevOps Engineer"),
        ("Fatima", "Project Manager"),
    ])

    sql = f"SELECT * FROM users WHERE name = '{query}'"
    results = cursor.execute(sql).fetchall()
    conn.close()

    rows = ""
    for row in results:
        rows += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"

    return f"""
    <h2 style="color:red;">SQL Injection Alert: Vulnerable query detected</h2>
    <p><strong>Query entered:</strong> {query}</p>
    <p><strong>SQL executed:</strong> {sql}</p>

    <table border="1" cellpadding="8">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Role</th>
        </tr>
        {rows}
    </table>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
