from flask import Flask, render_template
from flask import request, session, redirect
import pymysql 
from datetime import datetime

app=Flask(__name__,
        static_folder='static',
        template_folder='template')

app.config['ENV']='development'
app.config['DEBUG']=True
app.secret_key='who are you?'

db = pymysql.connect(
    user='root',
    passwd='avante',
    host='localhost',
    db='web',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
    )

def get_menu():
    cur=db.cursor()
    cur.execute(f"""
    select id, title from topic
    """)
    menu = cur.fetchall()
    menu_list = []
    for row in menu:
        menu_list.append(f"""<li><a href='{row['id']}'> {row['title']}</a></li>
                """)
    return '\n'.join(menu_list)

@app.route('/')
def index():
    if 'owner' in session:
        message='Welcome~~ '+session['user']['name']
    else:
        message='Welcome everybody!!'
    return render_template('template.html',
                        menu = get_menu(),
                        title='Python 문법을 조회해 보세요',
                        message = message)

@app.route('/<id>')
def menu(id):
    cur=db.cursor()
    cur.execute(f"""
        select id, title, description from topic where id='{id}'
    """)
    content=cur.fetchone()

    return render_template('template.html',
                        id = content['id'],
                        menu=get_menu(),
                        title= content['title'] ,
                        description= content['description'])

@app.route('/delete/<id>')
def delete(id):
    cursor = db.cursor()
    cursor.execute(f"delete from topic where id='{id}'")
    db.commit()
    return redirect("/")

@app.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'POST':
        cursor = db.cursor()
        sql = f"""
            insert into topic (title, description, created, author_id)
                values ('{request.form['title']}', '{request.form['desc']}',
                    '{datetime.now()}', "{session['user']['id']}")"""
        cursor.execute(sql)
        db.commit()
        return redirect('/')

    return render_template('create.html',
                        menu=get_menu())

@app.route('/login', methods=['GET','POST'])
def login():
    message='login 해 주세요'

    if request.method == 'POST':
        cur=db.cursor()
        cur.execute(f"""
                select name from author where name='{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            message="회원이 아닙니다."
        else:
            cur=db.cursor()
            cur.execute(f"""
                select id, name, profile from author 
                where name='{request.form['id']}' and password=SHA2('{request.form['pw']}',256)
            """)
            user=cur.fetchone()
            if user is None:
                message='암호를 확인해 주세요.'
            else:
                session['user']=user
                return redirect('/')

    return render_template('login.html',
                        menu = get_menu(),
                        message=message)

@app.route('/logout')
def logout():
    session.pop('user', None)

    return redirect('/')

@app.route('/join', methods=['GET','POST'])
def join():
    message='회원 가입을 부탁드립니다.'
    if request.method=='POST':
        cur=db.cursor()
        cur.execute(f"""
            select name from author where name='{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            cur=db.cursor()
            cur.execute(f"""
                insert into author (name, profile, password)
                values( '{request.form['id']}' , '{request.form['pf']}' ,
                 SHA2('{request.form['pw']}', 256))
            """)
            db.commit()
            return redirect('/')
        else:
            message='이미 가입하셨읍니다.'

    return render_template('join.html',
                        menu = get_menu(),
                        message=message)

@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    message='탈퇴를 원하는 user id 를 입력해 주세요'
    if request.method == 'POST':
        cur=db.cursor()
        cur.execute(f"""
            select name from author where name='{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            message="가입된 회원이 아닙니다."
        else:
            cur=db.cursor()
            cur.execute(f"""
                delete from author where name='{request.form['id']}'
            """)
            db.commit()
            return redirect('/')

    return render_template('withdraw.html',
                        menu = get_menu(),
                        message=message)

@app.route('/dbquery')
def dbquery():
    cur=db.cursor()
    cur.execute(f"""
        select * from author
    """)
    user=cur.fetchall()
    return str(user)


app.run(port=5000)