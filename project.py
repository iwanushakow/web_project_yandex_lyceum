from flask import Flask, render_template, request
import sqlalchemy as sa

import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import sqlalchemy
import datetime

# -------------------------------------------------------------------------------------------
SqlAlchemyBase = dec.declarative_base()

__factory = None


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
global_init("main_base.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.form.get('button'):
        password = get_user_password(request.form.get('mail'))
        if request.form.get('password') == password:
            print('nice')
        else:
            print('not nice')
    return render_template('sign_in/sign_in.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.form.get('button'):
        code_word = request.form.get('code_word')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')
        name = request.form.get('name')
        mail = request.form.get('mail')
        password = str(hash(pass1))
        add_user(mail, name, password, code_word, 'nick')
        print(name, mail, password, code_word, 'nick')
    return render_template('registration/registration.html')


@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.form.get('button'):
        user_id = get_user_id(request.form.get('mail'))
        post_text = request.form.get('post_text')
        post_headline = request.form.get('post_head')
        add_post(user_id, post_text, post_headline)
    return render_template('post/post.html')


@app.route('/')
def main():
    lst = get_all_posts()
    print(lst)
    # не показывает посты, почему-то
    return render_template('main.html', lst=lst)


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/profile')
def profile():
    return render_template('profile/profile.html')


@app.route('/composition')
def composition():
    return render_template('composition/composition.html')


@app.route('/my_works')
def my_works():
    return render_template('my_works/works.php')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
