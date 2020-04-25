from flask import Flask, redirect, render_template, request, send_file
import sqlalchemy as sa

from flask import Blueprint, jsonify

import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import sqlalchemy
import datetime
from werkzeug.utils import secure_filename
import os

# -------------------------------------------------------------------------------------------
SqlAlchemyBase = dec.declarative_base()

__factory = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'works'

keys = ['Ivan', 'Anton']


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


# ----------------------------------------------------------------------------------------------------------------------


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    User_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    User_mail = sqlalchemy.Column(sqlalchemy.String, unique=True)
    User_name = sqlalchemy.Column(sqlalchemy.String)
    User_password = sqlalchemy.Column(sqlalchemy.String)
    User_code_word = sqlalchemy.Column(sqlalchemy.String)
    User_nick = sqlalchemy.Column(sqlalchemy.String)


#   posts = все посты полльзователя

def add_user(mail, name, password, code_word, nick):
    user = User()
    user.User_mail = mail
    user.User_name = name
    user.User_password = password
    user.User_code_word = code_word
    user.User_nick = nick
    session = create_session()
    session.add(user)
    session.commit()


def get_user_password(user_mail):
    session = create_session()
    for user in session.query(User).filter(User.User_mail == user_mail):
        return user.User_password


def get_user_id(user_mail):
    session = create_session()
    for user in session.query(User).filter(User.User_mail == user_mail):
        return user.User_id


def get_user_nick(user_id):
    session = create_session()
    for user in session.query(User).filter(User.User_id == user_id):
        return user.User_nick


# ----------------------------------------------------------------------------------------------------------------------


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    Post_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    User_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.User_id"))
    Post_date = sqlalchemy.Column(sqlalchemy.DateTime)
    Post_text = sqlalchemy.Column(sqlalchemy.String)
    Post_headline = sqlalchemy.Column(sqlalchemy.String)
    Work_link = sqlalchemy.Column(sqlalchemy.String)
    Post_level = sqlalchemy.Column(sqlalchemy.Integer)
    Another_id = sqlalchemy.Column(sqlalchemy.Integer)  # another post's id (if it is a comment)
    Post_type = sqlalchemy.Column(sqlalchemy.Boolean)


def add_post(user_id, post_text, post_headline, work_link):
    new_post = Post()
    new_post.User_id = user_id
    new_post.Post_date = datetime.datetime.today()
    new_post.Post_text = post_text
    new_post.Post_headline = post_headline
    new_post.Post_level = 1
    new_post.Work_link = work_link
    session = create_session()
    session.add(new_post)
    session.commit()


def get_all_posts():
    session = create_session()
    lst_final = list()
    for post in session.query(Post).filter(Post.Post_level == 1):
        lst = list()
        lst.append(get_user_nick(post.User_id))
        lst.append(post.Post_headline)
        lst.append(post.Post_text)
        lst.append(post.Post_date)
        lst.append(post.Post_id)
        lst_final.append(lst)
    return lst_final


def get_posts(id):
    session = create_session()
    lst_final = list()
    for post in session.query(Post).filter(Post.User_id == id, Post.Post_level == 1):
        lst = list()
        lst.append(get_user_nick(post.User_id))
        lst.append(post.Post_headline)
        lst.append(post.Post_text)
        lst.append(post.Post_date)
        lst.append(post.Post_id)
        lst_final.append(lst)
    return lst_final


def get_comments(id):
    session = create_session()
    lst_final = list()
    for post in session.query(Post).filter(Post.Another_id == id):
        lst = list()
        lst.append(get_user_nick(post.User_id))
        lst.append(post.Post_text)
        lst.append(post.Post_date)
        lst_final.append(lst)
    return lst_final


def add_comment(post_text, post_type, another_id):
    new_post = Post()
    new_post.User_id = current_user.id()
    new_post.Post_date = datetime.datetime.today()
    new_post.Post_text = post_text
    new_post.Post_level = 2
    new_post.Post_type = post_type
    new_post.Another_id = another_id
    session = create_session()
    session.add(new_post)
    session.commit()


# ----------------------------------------------------------------------------------------------------------------------


class Work(SqlAlchemyBase):
    __tablename__ = 'works'

    Work_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    User_id = sqlalchemy.Column(sqlalchemy.Integer)
    Work_type = sqlalchemy.Column(sqlalchemy.String)
    Work_date = sqlalchemy.Column(sqlalchemy.DateTime)
    Work_link = sqlalchemy.Column(sqlalchemy.String)
    Work_name = sqlalchemy.Column(sqlalchemy.String)


def add_work(user_id, work_type, work_link, work_name):
    new_work = Work()
    new_work.User_id = user_id
    new_work.Work_type = work_type
    new_work.Work_link = work_link
    new_work.Work_date = datetime.datetime.today()
    new_work.Work_name = work_name
    session = create_session()
    session.add(new_work)
    session.commit()


def get_works():
    session = create_session()
    lst = list()
    for work in session.query(Work).filter(Work.User_id == current_user.id()):
        small_lst = list()
        small_lst.append(work.Work_name)
        small_lst.append(work.Work_link)
        small_lst.append(work.Work_date)
        lst.append(small_lst)
    return lst


# ----------------------------------------------------------------------------------------------------------------------


def allowed_file(filename):
    return '.' in filename


# ----------------------------------------------------------------------------------------------------------------------
global_init("main_base.db")


class CurrentUser:
    def __init__(self):
        self.user_id = False
        self.user_nick = False

    def is_signed_in(self):
        return bool(self.user_id)

    def new_user(self, id, nick):
        self.user_id = id
        self.user_nick = nick

    def nick(self):
        return self.user_nick

    def id(self):
        return self.user_id


current_user = CurrentUser()


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    error_mail = ''
    error_password = ''
    if request.form.get('button'):
        s = create_session()
        user = s.query(User).filter(User.User_mail == request.form.get('mail')).first()
        if user:
            password = user.User_password
            if request.form.get('password') == password:
                prof = redirect('/profile')
                current_user.new_user(user.User_id, user.User_nick)
                return prof
            else:
                error_password = 'wrong password my dude'
        else:
            error_mail = 'we dont have users with this email'
    return render_template('sign_in/sign_in.html', error_mail=error_mail, error_password=error_password)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.form.get('button'):
        s = create_session()
        error_mail = ''
        error_code_word = ''
        error_name = ''
        error_pass1 = ''
        error_pass2 = ''
        code_word = request.form.get('code_word')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')
        name = request.form.get('name')
        mail = request.form.get('mail')
        password = pass1
        mails = [i[0] for i in list(s.query(User.User_mail).all())]
        if pass1 != pass2:
            error_pass2 = 'passwords do not match'
        if len(pass1) < 8:
            error_pass1 = 'password is too short'
        if code_word == '':
            error_code_word = 'you forgot the code word. dude...'
        if name == '':
            error_name = 'how are we supposed to give you copyrights if we do not have your name???'
        if '@' in mails:
            error_mail = 'this email is not cool'
        if mail in mails:
            error_mail = 'already in the system bro'
        if error_mail == error_name == error_code_word == error_pass1 == error_pass2:
            nick = 'nick'
            add_user(mail, name, password, code_word, nick)
            id = get_user_id(mail)
            current_user.new_user(id, nick)
            prof = redirect('/profile')
            return prof
        else:
            return render_template('registration/registration.html', error_pass2=error_pass2,
                                   error_pass1=error_pass1, error_code_word=error_code_word,
                                   error_name=error_name, error_mail=error_mail)
    return render_template('registration/registration.html')


@app.route('/post', methods=['GET', 'POST'])
def post():
    if current_user.is_signed_in():
        if request.form.get('button'):
            post_text = request.form.get('post_text')
            post_headline = request.form.get('post_head')
            post_work_link = request.form.get('work') if request.form.get('work') != 'none' else None
            print(post_work_link
                  )
            add_post(current_user.id(), post_text, post_headline, post_work_link)
            return redirect('/profile')
        lst = get_works()
        return render_template('post/post.html', lst=lst)
    else:
        return render_template('not_logged_in/main.html')


@app.route('/')
def start():
    return render_template('start/main.html')


@app.route('/main_page')
def main():
    if current_user.is_signed_in():
        if request.method == 'GET':
            dictionary = dict(request.args)
            if len(dictionary) > 0:
                post_id = dictionary['comment'].split()[-2]
                return redirect(f'/comment/{post_id}')
        lst = get_all_posts()
        return render_template('main/main.html', lst=lst)
    else:
        return render_template('not_logged_in/main.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if current_user.is_signed_in():
        nick = current_user.nick()
        lst = get_posts(current_user.id())
        if request.method == 'GET':
            dictionary = dict(request.args)
            if len(dictionary) > 0:
                if 'composition' in dictionary.keys():
                    return redirect('/composition')
                elif 'post' in dictionary.keys():
                    return redirect('/post')
                elif 'work' in dictionary.keys():
                    return redirect('/my_works')
                elif 'comment' in dictionary.keys():
                    post_id = dictionary['comment'].split('-')[0].split()[-1]
                    return redirect(f'/my_comments/{post_id}')
        return render_template('profile/profile.html', nick=nick, lst=lst)
    else:
        return render_template('not_logged_in/main.html')


@app.route('/composition', methods=['GET', 'POST'])
def composition():
    if current_user.is_signed_in():
        if request.form.get('button'):
            file = request.files['file']
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            add_work(current_user.id(), 'пока без этого', path, request.form.get('name'))
            return redirect('/profile')
        return render_template('composition/composition.html')
    else:
        return render_template('not_logged_in/main.html')


@app.route('/my_works')
def my_works():
    if current_user.is_signed_in():
        if request.method == 'GET':
            path = dict(request.args)
            if len(path) > 0:
                return send_file(path['composition'])
        return render_template('my_works/works.html', list=get_works())
    else:
        return render_template('not_logged_in/main.html')


@app.route('/comment/<post_id>', methods=['GET', 'POST'])
def comment(post_id):
    if current_user.is_signed_in():
        lst = get_comments(post_id)
        if request.form.get('Submit'):
            post_type = True if request.form.get('type') == 'like' else False
            post_text = request.form.get('text')
            add_comment(post_text, post_type, post_id)
            # ----------------------------------------
            return redirect('/main_page')
        return render_template('comment/comment.html', lst=lst)
    else:
        return render_template("not_logged_in/main.html")


@app.route('/my_comments/<post_id>', methods=['GET', 'POST'])
def comments(post_id):
    if current_user.is_signed_in():
        lst = get_comments(post_id)
        if request.form.get('Submit'):
            post_type = True if request.form.get('type') == 'like' else False
            post_text = request.form.get('text')
            add_comment(post_text, post_type, post_id)
            # ----------------------------------------
            return redirect('/main_page')
        return render_template('comment/my_comment.html', lst=lst)
    else:
        return render_template("not_logged_in/main.html")


# ////////////////////////////////////////////////////  API  ///////////////////////////////////////////////////////////

@app.route('/api/<key>/post/')
def get_jobs_api(key):  # //////////// Аналог ленты новостей, сортируется по дате //////////////////////////////////////
    if key in keys:
        lst = get_all_posts()
        print(lst, 5)
        dat = ['Post_id', 'User_id', 'Post_date', "Post_text", 'Post_headline', 'Work_link', "Post_level", 'Another_id']
        return jsonify(
            {
                x[2]: dict(zip(dat, x)) for x in lst
            }
        )
    else:
        return 'false key'


@app.route('/api/<key>/walls/')
def get_walls_api(key):  # ////////////// Посты каждого пользователя, сортируются по нику //////////////////////////////
    if key in keys:
        lst = get_all_posts()
        print(lst, 5)
        dat = ['Post_id', 'User_id', 'Post_date', "Post_text", 'Post_headline', 'Work_link', "Post_level", 'Another_id']
        return jsonify(
            {
                x[1]: dict(zip(dat, x)) for x in lst
            }
        )
    else:
        return 'false key'


@app.route('/api/<key>/registration/<pass1>/<pass2>/<code_word>/<name>/<mail>')
def registration_api(pass1, pass2, code_word, name,
                     mail, key):  # ////////////// Ругистрация с помощью API //////////////////
    if key in keys:
        s = create_session()
        error_mail = ''
        error_code_word = ''
        error_name = ''
        error_pass1 = ''
        error_pass2 = ''
        password = str(pass1)
        mails = [i[0] for i in list(s.query(User.User_mail).all())]
        if pass1 != pass2:
            error_pass2 = 'passwords do not match'
            return error_pass2
        if len(pass1) < 8:
            error_pass1 = 'password is too short'
            return error_pass1
        if code_word == '':
            error_code_word = 'you forgot the code word. dude...'
            return error_code_word
        if name == '':
            error_name = 'how are we supposed to give you copyrights if we do not have your name???'
            return error_name
        if '@' in mails:
            error_mail = 'this email is not cool'
            return error_mail
        if mail in mails:
            error_mail = 'already in the system bro'
            return error_mail
        if error_mail == error_name == error_code_word == error_pass1 == error_pass2:
            nick = 'nick'
            add_user(mail, name, password, code_word, nick)
            id = get_user_id(mail)
            current_user.new_user(id, nick)
            return 'ok'
    else:
        return 'false key'


@app.route('/api/<key>/sign_in/<password>/<mail>/')
def sign_in_api(password, mail, key):  # /////////////// Вход через API ////////////////////////////////////////////////
    if key in keys:
        s = create_session()
        user = s.query(User).filter(User.User_mail == mail).first()
        if user:
            password1 = user.User_password
            print(password, password1)
            if str(password) == password1:
                print(password, mail)
                return 'OK'
    else:
        return 'false key'


@app.route('/api/<key>/comment/<post_id>')
def comment_api(post_id, key):
    if key in keys:
        lst = get_comments(post_id)
        dat = ['nick', 'text', 'date']
        return jsonify(
            {
                x[0]: dict(zip(dat, x)) for x in lst
            }
        )
    else:
        return 'false key'


if __name__ == '__main__':
    app.run()
