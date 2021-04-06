# Imports
import json
import flask
import server_helper as helper
from flask import Flask, render_template, url_for, request, redirect, session, abort
from flask_mysqldb import MySQL

# Global Vars
app = Flask(__name__)

# Remove when fully finished
f = open("temp.csv")
lines = f.readlines()

app.secret_key = lines[0].strip('\n')

# Set up database
app.config['MYSQL_HOST'] = lines[1].strip('\n')
app.config['MYSQL_USER'] = lines[2].strip('\n')
app.config['MYSQL_PASSWORD'] = lines[3].strip('\n')
app.config['MYSQL_DB'] = lines[4].strip('\n')

mysql = MySQL(app)


# ToDo List
# 1. Need to create class to hold all data related to processes (different class same class?)
# 2. Need to create database connection. Can do local db file or have a new one set up. This is small scale
# enough local will probably suffice.
# 2.5. I guess account creation abilities would go with this. Honestly either works
# 3. Need to reload config file read in when a new server is added or destroyed. Don't forget this one
# X. Probably Some other stuff tbh. But rn, IDK
# 4. Rewrite the Login page. This is from an example. Make it my own work
# 5. Implement Registration Page
# 6. Implement Add Server Page
# 7. Pull server data associated with active server list


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        post_data = json.loads(bytes.decode(request.data))
        helper.handleMcStart(post_data)
        return 'OK'
    else:
        process_array = helper.get_process_array()  # todo Get the data made into a class and uhh, do stuff with it here.
        return render_template("index_revision.html", servers=process_array, server_number=0, active=True,
                               image_source="minecraft-vanilla.jpg", server_name="Minecraft",
                               server_text="A minecraft Server", logged_in=get_if_logged_in())


@app.route("/update")
def update():
    update_data = helper.getRamInfo()
    update_data["servers"] = helper.getServerStatus()
    return flask.jsonify(update_data)


@app.route("/login", methods=['POST', 'GET'])
def do_login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        db_data = execute_query("SELECT username, password FROM users WHERE username = '{0}' "
                                "AND password = '{1}'".format(request.form['username'], request.form['password']))
        db_data = db_data[0]
        if len(db_data) != 0:
            if request.form['username'] == db_data[0] and request.form['password'] == db_data[1]:
                session['logged_in'] = True
                return redirect(url_for("index"))
        else:
            session['logged_in'] = False
            return render_template("login.html", msg="Login Not Valid")


@app.route('/logout')
def do_logout():
    session.pop('logged_in', None)
    return index()


@app.route('/register')
def do_register():
    if get_if_logged_in():
        return redirect(url_for("index"))
    return render_template("register.html")


# Database Helper Functions
def execute_query(query):
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute(query)
        r = cur.fetchall()
        cur.close()
    return r


def execute_query_with_commit(query):
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        cur.close()


# Local Helpers
def get_if_logged_in():
    return session.get("logged_in") if session.get('logged_in') is not None else False


if __name__ == '__main__':
    # print(execute_query("SELECT * FROM server_instances"))
    # print(execute_query("SHOW columns FROM users"))
    # print(execute_query("SELECT password FROM users WHERE username = 'Skipper'"))
    # execute_query_with_commit("INSERT INTO users (email, password) VALUES ('tester@gmail.com', 'thisIsAPassword')")
    helper.readInConfig()
    app.run(host='192.168.0.55', port='80')
