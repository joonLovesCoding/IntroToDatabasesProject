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

# assuming the user is already logged in
@app.route("/")
def index():
    # INCOMPLETE: add a login function
    session['username'] = 'AlreadyLoggedIn'
    return render_template('index.html')


@app.route('/post')
def post():
    return render_template('post.html')

# assuming the user is already logged in
@app.route('/post_action', methods=['GET', 'POST'])
def post_action():
    photo_poster = session['username']
    file_path = request.form['file_path']
    all_followers = int(request.form['all_followers'])
    caption = request.form['caption']
    cursor = conn.cursor()

    if all_followers == 1:
        posting_date = datetime.now()
        cursor.execute('INSERT INTO photo (postingDate, filepath, allFollowers, caption, photoPoster) VALUES (%s, %s, %s, %s, %s)',
                       (posting_date, file_path, all_followers, caption, photo_poster))
        conn.commit()
        cursor.close()
        return render_template('post.html')
    else:
        cursor.execute('SELECT groupName FROM friendgroup WHERE groupOwner = %s', (photo_poster))
        result = cursor.fetchall()
        cursor.close()
        return render_template('post_action_group.html', file_path=file_path, caption=caption, friend_groups=result)


@app.route('/post_action_group', methods=['POST'])
def post_action_group():
    posting_date = datetime.now()
    file_path = request.form['file_path']
    all_followers = 0
    caption = request.form['caption']
    photo_poster = session['username']
    friend_group = request.form['friend_group']
    cursor = conn.cursor()

    # upload the photo
    cursor.execute('INSERT INTO photo (postingDate, filepath, allFollowers, caption, photoPoster) VALUES (%s, %s, %s, %s, %s)',
                   (posting_date, file_path, all_followers, caption, photo_poster))
    # determine the AUTO_INCREMENT value
    cursor.execute('SELECT photoID FROM photo AS p WHERE photoID > ALL(SELECT photoID FROM photo WHERE photoID != p.photoID)')
    result = cursor.fetchone()
    # print(result, file=sys.stderr)
    # print(result['photoID'], file=sys.stderr)
    # share the photo
    cursor.execute('INSERT INTO sharedwith VALUES (%s, %s, %s)', (photo_poster, friend_group, result['photoID']))
    conn.commit()
    cursor.close()
    return render_template('index.html')


app.secret_key = "Databases project part 3"
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
