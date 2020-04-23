from flask import Flask, redirect, render_template, request
import sqlalchemy as sa

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


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

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
        print(user.User_password)
        return user.User_password


def get_user_id(user_mail):
    session = create_session()
    for user in session.query(User).filter(User.User_mail == user_mail):
        print(user.User_id)
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
    user = sqlalchemy.orm.relation('User', backref='posts')


def add_post(user_id, post_text, post_headline):
    new_post = Post()
    new_post.User_id = user_id
    new_post.Post_date = datetime.datetime.today()
    new_post.Post_text = post_text
    new_post.Post_headline = post_headline
    new_post.Post_level = 1
    session = create_session()
    session.add(new_post)
    session.commit()


def get_all_posts():
    session = create_session()
    lst_final = list()
    for post in session.query(Post).all():
        lst = list()
        lst.append(get_user_nick(post.User_id))
        lst.append(post.Post_headline)
        lst.append(post.Post_text)
        lst.append(post.Post_date)
        lst_final.append(lst)
    return lst_final


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
    if request.form.get('button'):
        s = create_session()
        user = s.query(User).filter(User.User_mail == request.form.get('mail')).first()
        if user.User_mail:
            password = user.User_password
            if request.form.get('password') == password:
                prof = redirect('/profile')
                current_user.new_user(user.User_id, user.User_nick)
                print(current_user.user_id)
                return prof
    if current_user.is_signed_in:
        return render_template('sign_in/sign_in.html', nick=current_user.nick())
    else:
        return render_template('sign_in/sign_in.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.form.get('button'):
        s = create_session()
        code_word = request.form.get('code_word')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')
        name = request.form.get('name')
        mail = request.form.get('mail')
        password = str(hash(pass1))
        mails = [i[0] for i in list(s.query(User.User_mail).all())]
        print(mails)
        if pass1 == pass2 and mail not in mails:
            add_user(mail, name, password, code_word, 'nick')
            prof = redirect('/profile')
            return prof
    return render_template('registration/registration.html')


@app.route('/post', methods=['GET', 'POST'])
def post():
    if current_user.is_signed_in():
        if request.form.get('button'):
            user_id = get_user_id(request.form.get('mail'))
            post_text = request.form.get('post_text')
            post_headline = request.form.get('post_head')
            add_post(user_id, post_text, post_headline)
        return render_template('post/post.html')
    else:
        return render_template('not_logged_in/main.html')


@app.route('/')
def main():
    if current_user.is_signed_in():
        lst = get_all_posts()
        print(lst)
        return render_template('main/main.html', lst=lst)
    else:
        return render_template('not_logged_in/main.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if current_user.is_signed_in():
        if request.form.get('post'):
            response = redirect('/post')
            return response
        elif request.form.get('composition'):
            response = redirect('/composition')
            return response
        elif request.form.get('work'):
            response = redirect('/my_works')
            return response
        if current_user:
            nick = current_user.nick()
            return render_template('profile/profile.html', nick=nick)
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


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/my_works')
def my_works():
    if current_user.is_signed_in():
        return render_template('my_works/works.html', list=get_works())
    else:
        return render_template('not_logged_in/main.html')


@app.route('/comment')
def comment():
    if current_user.is_signed_in():
        return render_template('comment/comment.html')
    else:
        return render_template("not_logged_in/main.html")


if __name__ == '__main__':
    app.run(port=808, host='127.0.0.1')
