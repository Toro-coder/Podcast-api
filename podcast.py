from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'C:/Users/KIM/PycharmProjects/podcast-api/files/'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif', 'mp3', 'mpeg'])


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


@app.route('/file_upload', methods=['POST', 'GET'])
def file_upload():
    try:
        form = request.form
        genre = form['genre']
        age_group = form['age_group']
        title = form['title']
        descriptions = form['descriptions']
        phone = form['phone']
        audio = request.files['audio_url']

        if audio and allowed_file(audio.filename):
            filename = secure_filename(audio.filename)
            audio_url = UPLOAD_FOLDER + filename
            audio.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM podcast WHERE phone = % s and audio_url = % s', (phone, audio_url))
            account = cursor.fetchone()
            if account:
                return 'The audio already exists'

            if genre != 'News' and genre != 'Weather & Environment' and genre != 'Trends' and genre != 'Travel & Leisure' and \
                    genre != 'Tech & Trends' and genre != 'Health & Neutrition' and genre != 'Food & Drinks' and genre != 'Fitness & Wellness' \
                    and genre != 'Entertainment' and genre != 'Beauty & Fashion' and genre != 'Agriculture' and genre != 'Business' \
                    and genre != 'Sports' and genre != 'Love & Relationship' and genre != 'Politics' and genre != 'Comedy':
                return 'Please Select a genre'
            elif age_group != 'under 18' and age_group != '18-24' and age_group != '25-30' and \
                    age_group != '30-35' and age_group != '35-40' and age_group != '40-50' and \
                    age_group != '50-60' and age_group != 'Above 60':
                return 'Kindly select your age group'
            elif not phone or not genre or not age_group or not title or not descriptions:
                return 'please enter the necessary credentials'
            cursor.execute('INSERT INTO podcast VALUES (NULL, % s, % s, % s, % s, % s, % s)',
                           (phone, genre, age_group, title, descriptions, audio_url))
            mysql.connection.commit()
            return 'Congratulations, You have successfully added a file'

        else:
            return 'Sorry, There was a problem in adding a file'

    except Exception as e:
        print(e)


@app.route('/file_display', methods=['POST', 'GET'])
def file_display():
    form = request.form
    phone_no = form['phone_no']
    if phone_no:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users_post WHERE phone_no = % s', (phone_no,))
        account = cursor.fetchall()
        if account:
            return jsonify(account)
        else:
            return jsonify({'message': 'The file does not exist'})


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    form = request.form
    id = form['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM podcast WHERE id = % s', (id,))
    data = cursor.fetchall()
    if data:
        return jsonify(data)


@app.route('/update', methods=['POST', 'GET'])
def update():
    form = request.form
    genre = form['genre']
    age_group = form['age_group']
    title = form['title']
    descriptions = form['descriptions']
    id = form['id']
    audio = request.files['audio_url']
    if audio and allowed_file(audio.filename) and genre and age_group and title and descriptions:
        filename = secure_filename(audio.filename)
        audio_url = UPLOAD_FOLDER + filename
        audio.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE podcast SET  genre = % s, age_group = % s, title = % s, descriptions = % s, audio_url '
                       '= % s WHERE id = % s', (genre, age_group, title, descriptions, audio_url, id))
        mysql.connection.commit()
        return 'Congratulations, You have successfully updated your file'
    else:
        return 'Sorry, Something went wrong'


if __name__ == '__main__':
    app.run(debug=True)
