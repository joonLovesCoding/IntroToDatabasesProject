# Part 3 benchmark assumptions:
# There is already a user registered under the name AlreadyLoggedIn
# AlreadyLoggedIn is the owner of a Friendgroup called SecretBudz

from flask import Flask, render_template, request, session
import pymysql.cursors
from datetime import datetime
import sys

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='root',
                       password='',
                       db='project',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@app.route("/")
def index():
    session['username'] = 'AlreadyLoggedIn'
    return render_template('index.html')


@app.route('/post')
def post():
    return render_template('post.html')


@app.route('/post_action', methods=['GET', 'POST'])
def post_action():
    filepath = request.form['filepath']
    allFollowers = int(request.form['allFollowers'])
    caption = request.form['caption']
    photoPoster = session['username']
    cursor = conn.cursor()

    if allFollowers == 1:
        postingdate = datetime.now()
        cursor.execute('INSERT INTO Photo (postingdate, filepath, allFollowers, caption, photoPoster) VALUES (%s, %s, %s, %s, %s)',
                       (postingdate, filepath, allFollowers, caption, photoPoster))
        conn.commit()
        cursor.close()
        return render_template('post.html')
    else:
        cursor.execute('SELECT groupName FROM Friendgroup WHERE groupOwner = %s', (photoPoster))
        result = cursor.fetchall()
        cursor.close()
        return render_template('post_action_group.html', filepath=filepath, caption=caption, Friendgroups=result)


@app.route('/post_action_group', methods=['POST'])
def post_action_group():
    postingdate = datetime.now()
    filepath = request.form['filepath']
    allFollowers = 0
    caption = request.form['caption']
    photoPoster = session['username']
    Friendgroup = request.form['Friendgroup']
    cursor = conn.cursor()

    # upload the photo
    cursor.execute('INSERT INTO Photo (postingdate, filepath, allFollowers, caption, photoPoster) VALUES (%s, %s, %s, %s, %s)',
                   (postingdate, filepath, allFollowers, caption, photoPoster))
    # determine the AUTO_INCREMENT value
    cursor.execute('SELECT photoID FROM Photo AS p WHERE photoID > ALL(SELECT photoID FROM Photo WHERE photoID != p.photoID)')
    result = cursor.fetchone()
    # share the photo
    cursor.execute('INSERT INTO SharedWith VALUES (%s, %s, %s)', (photoPoster, Friendgroup, result['photoID']))
    conn.commit()
    cursor.close()
    return render_template('post.html')


app.secret_key = "Databases project part 3"
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
