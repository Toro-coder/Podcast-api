from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import boto3
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['mp3'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_ROOT'] = '3306'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Cindy1648'
app.config['MYSQL_DB'] = 'campaigns'

app.config['S3_BUCKET'] = "teleeza-pilot"
app.config['S3_KEY'] = "AKIAWQ63TTT7NWIPJMMQ"
app.config['S3_SECRET'] = "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"
app.config['S3_LOCATION'] = 'https://s3.us-east-2.amazonaws.com/teleeza-pilot/'

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
        bucket = 'teleeza-pilot'
        content_type = request.mimetype
        audio = request.files['audio_url']
        if audio and allowed_file(audio.filename):
            client = boto3.client('s3',
                                  region_name='us-east-2',
                                  endpoint_url='https://s3.us-east-2.amazonaws.com',
                                  aws_access_key_id=app.config['S3_KEY'],
                                  aws_secret_access_key=app.config['S3_SECRET'])

            filename = secure_filename(audio.filename)
            client.put_object(Body=audio,
                              Bucket=bucket,
                              Key=filename,
                              ContentType=content_type,
                              ACL="public-read")

            filename = app.config['S3_LOCATION'] + filename
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM blogs WHERE phone = % s and thumbnail_url = % s', (phone, filename))
            account = cursor.fetchone()
            if account:
                return 'The file already exists'
            cursor.execute('INSERT INTO podcast (genre, age_group, title, descriptions, audio_url, phone)'
                           ' VALUES (% s, % s, % s, % s, % s, % s)',
                           (genre, age_group, title, descriptions, filename, phone))
            mysql.connection.commit()
            return 'podcast created successfully'
        else:
            return 'System accepts only mp3'
    except Exception as e:
        print(e)


@app.route('/file_display', methods=['POST', 'GET'])
def file_display():
    form = request.form
    phone = form['phone']
    if phone:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT title, descriptions ,genre, audio_url, created_on FROM podcast WHERE phone = %s and flag = 1',
                       (phone,))
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
        cursor.execute('SELECT * FROM podcast WHERE id = %s and flag = 1', (id,))
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
    title = form['title']
    descriptions = form['descriptions']
    id = form['id']
    bucket = 'teleeza-pilot'
    content_type = request.mimetype
    audio = request.files['audio_url']
    if audio and allowed_file(audio.filename):
        client = boto3.client('s3',
                              region_name='us-east-2',
                              endpoint_url='https://s3.us-east-2.amazonaws.com',
                              aws_access_key_id=app.config['S3_KEY'],
                              aws_secret_access_key=app.config['S3_SECRET'])

        filename = secure_filename(audio.filename)
        client.put_object(Body=audio,
                          Bucket=bucket,
                          Key=filename,
                          ContentType=content_type,
                          ACL="public-read")

        filename = app.config['S3_LOCATION'] + filename
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE podcast SET  genre = % s, age_group = % s, title = % s, descriptions = % s, audio_url '
                       '= % s, updated_on = NOW() WHERE id = % s', (genre, age_group, title, descriptions, filename, id))
        mysql.connection.commit()
        return 'Congratulations, You have successfully updated your file'
    else:
        return 'Sorry, Something went wrong'

@app.route('/delete', methods=['POST', 'GET'])
def delete():
    id = request.form["id"]
    if id:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE podcast SET  flag = 0 WHERE id = % s', (id,))
        mysql.connection.commit()
        return 'The file is deleted successful'


if __name__ == '__main__':
    app.run(debug=True)
