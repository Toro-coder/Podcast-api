from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'C:/Users/KIM/PycharmProjects/podcast-api/files/'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_ROOT'] = '3306'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Cindy1648'
app.config['MYSQL_DB'] = 'campaigns'

mysql = MySQL(app)


@app.route('/fetch_genre', methods=['POST', 'GET'])
def fetch_genre():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT name FROM interests')
    account = cursor.fetchall()
    genre = []
    # looping through the list
    for i in account:
        account = list(i.values())
        genre.append(account)
    return genre


@app.route('/age_group', methods=['POST', 'GET'])
def age_group():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT name FROM age_groups')
    account = cursor.fetchall()
    age_group = []
    # looping through the list
    for i in account:
        account = list(i.values())
        age_group.append(account)
    return age_group


@app.route('/add_blog', methods=['POST', 'GET'])
def add_blog():
    try:
        form = request.form
        genre = form['genre']
        age_group = form['age_group']
        heading = form['heading']
        phone = form['phone']
        # updated_on = form['updated_on']
        thumbnail = request.files['thumbnail_url']

        if thumbnail and allowed_file(thumbnail.filename):
            filename = secure_filename(thumbnail.filename)
            thumbnail_url = UPLOAD_FOLDER + filename
            thumbnail.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM blogs WHERE phone = % s and thumbnail_url = % s', (phone, thumbnail_url))
            account = cursor.fetchone()
            if account:
                return 'The au already exists'
            cursor.execute('INSERT INTO blogs (genre, age_group, heading, thumbnail_url, phone)'
                           ' VALUES (% s, % s, % s, % s, % s)',
                           (genre, age_group, heading, thumbnail_url, phone))
            mysql.connection.commit()
            return 'Blog created successfully'

        else:
            return 'Failed! Try again later'

    except Exception as e:
        print(e)


@app.route('/blog_display', methods=['POST', 'GET'])
def blog_display():
    form = request.form
    phone = form['phone']
    if phone:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT heading,genre, thumbnail_url, created_on FROM blogs WHERE phone = %s and flag = 1', (phone, ))
        account = cursor.fetchall()
        if account:
            return jsonify(account)
        else:
            return jsonify({'message': 'The file does not exist'})


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    form = request.form
    id = form['id']
    if id:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM blogs WHERE id = %s and flag = 1', (id, ))
        account = cursor.fetchall()
        if account:
            return jsonify(account)
        else:
            return jsonify({'message': 'The blog does not exist'})


@app.route('/update', methods=['POST', 'GET'])
def update():
    form = request.form
    genre = form['genre']
    age_group = form['age_group']
    heading = form['heading']
    id = form['id']
    thumbnail = request.files['thumbnail_url']
    if thumbnail and allowed_file(thumbnail.filename) and genre and age_group and heading:
        filename = secure_filename(thumbnail.filename)
        thumbnail_url = UPLOAD_FOLDER + filename
        thumbnail.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE blogs SET  genre = % s, age_group = % s, heading = % s, thumbnail_url '
                       '= % s, updated_on = NOW() WHERE id = % s', (genre, age_group, heading, thumbnail_url, id))
        mysql.connection.commit()
        return 'Congratulations, You have successfully updated your file'
    else:
        return 'Sorry, Something went wrong'


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    id = request.form["id"]
    if id:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE blogs SET  flag = 0 WHERE id = % s', (id,))
        mysql.connection.commit()
        return 'The file is deleted successful'


if __name__ == '__main__':
    app.run(debug=True)
