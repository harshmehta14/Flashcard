from flask import Flask,render_template,request,redirect,url_for, session
import sqlite3
from datetime import datetime

app=Flask(__name__)
app.config['SECRET_KEY']='1234'    

@app.before_request
def require_login():
    allowed_routes=['login','register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/')

@app.route('/',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        conn=sqlite3.connect("project.db")
        cur=conn.cursor()
        query="""SELECT * FROM users WHERE username=? AND password=?"""
        cur.execute(query,(username,password))
        rows=cur.fetchall()
        
        if len(rows) ==1:
            session['username']=username
            return redirect(url_for('index'))
        else:
            return redirect(url_for('register'))
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=="POST":
        try:
            name=request.form['name']
            username=request.form['username']
            password=request.form['password']
            date_created = datetime.now()
            conn=sqlite3.connect("project.db")
            cur=conn.cursor()
            query="""INSERT INTO users (name,username,password,date_created) VALUES (?,?,?,?)"""
            cur.execute(query,(name,username,password,date_created))
            conn.commit()
            
            if cur.rowcount ==1:
                return "Registered successfully <a href='/'>Go to Login</a>"
            else:
                return "Username already exists <a href='/register'>Try Register again</a>"
        except:
            return "Something wrong"
        
    return render_template('register.html')


@app.route('/index')
def index():
    username = session['username']
    conn=sqlite3.connect("project.db")
    cur=conn.cursor()
    query="""SELECT deckname from cards WHERE front IS NULL and username=?"""
    cur.execute(query,(username,))
    rows=cur.fetchall()
    query1="""SELECT deckname, created_on from cards WHERE front IS NULL"""
    cur.execute(query1)
    created_on=cur.fetchall()
    
    query2 ="""Select score from users where username=?"""
    cur.execute(query2,(username,))
    score = cur.fetchone()[0]
    if rows != []:
        query2="""SELECT deckname, front from cards WHERE front IS NOT NULL """
        cur.execute(query2)
        card=cur.fetchall()
        
        return render_template('index.html',rows=rows , card=card,created_on=created_on,score=score,username=username )
    else:
        card=[[]]
        return render_template('index.html',rows=rows, card=card, created_on=created_on,score=score ,username=username )
   

@app.route('/createdeck',methods=['GET','POST'])
def createdeck():
    if request.method=="POST":
        deckname=request.form['deckname']
        created_on = datetime.now()
        username = session['username']
        if deckname == "":
            return redirect(url_for('createdeck'))
        conn=sqlite3.connect("project.db")
        cur=conn.cursor()
        query="""SELECT deckname from cards WHERE front IS NULL and username=?"""
        cur.execute(query,(username,))
        rows=cur.fetchall()
        flag=False
        for i in range(0,len(rows)):
            if deckname==rows[i][0]:
                flag=True
                break
        if (flag==False):
            query="""INSERT INTO cards (deckname,created_on,username) VALUES (?,?,?)"""
            cur.execute(query,(deckname,created_on,username))
            conn.commit()
            return redirect(url_for('index'))
        else:
            return render_template('createdeck.html')
    return render_template('createdeck.html')

@app.route('/deletedeck/<deckname>')
def deletedeck(deckname):
    conn=sqlite3.connect("project.db")
    cur=conn.cursor()
    query="""DELETE FROM cards WHERE deckname=?"""
    cur.execute(query,(deckname,))
    conn.commit()
    return redirect(url_for('index'))

@app.route('/updatedeck/<deckname>',methods=['GET','POST'])
def updatedeck(deckname):
    if request.method=="POST":
        old=deckname
        new=request.form['new']
        if new == "":
            return redirect(url_for('index'))
        conn=sqlite3.connect("project.db")
        cur=conn.cursor()
        query="""UPDATE cards SET deckname=? WHERE deckname=?"""
        cur.execute(query,(new,old))
        conn.commit()
        return redirect(url_for('index'))
    return render_template('updatedeck.html',deckname=deckname)


@app.route('/review/<deckname>',methods=["POST","GET"])
def review(deckname):
    if request.method == 'POST':
        option = request.form['option']
        if option == "easy":
            username = session['username']
            conn=sqlite3.connect("project.db")
            cur=conn.cursor()
            q1 = """Select score from users where username =?"""
            cur.execute(q1,(username,))
            score = cur.fetchone()
            scores = int(score[0])+3
            query="""Update users set score = ?  where username = ?"""
            cur.execute(query,(scores, username,))
            conn.commit()
        elif option == "medium":
            username = session['username']
            conn=sqlite3.connect("project.db")
            cur=conn.cursor()
            q1 = """Select score from users where username =?"""
            cur.execute(q1,(username,))
            score = cur.fetchone()
            scores = int(score[0])+2
            query="""Update users set score = ?  where username = ?"""
            cur.execute(query,(scores, username,))
            conn.commit()
        else:
            username = session['username']
            conn=sqlite3.connect("project.db")
            cur=conn.cursor()
            q1 = """Select score from users where username =?"""
            cur.execute(q1,(username,))
            score = cur.fetchone()
            scores = int(score[0])+1
            query="""Update users set score = ?  where username = ?"""
            cur.execute(query,(scores, username,))
            conn.commit()
        return redirect(url_for("review",deckname=deckname))
    else:    
        conn=sqlite3.connect("project.db")
        cur=conn.cursor()
        query="""SELECT * FROM cards WHERE deckname=? AND front IS NOT NULL ORDER BY RANDOM() LIMIT 1"""
        cur.execute(query,(deckname,))
        rows=cur.fetchone()
        if rows is not None:
            return render_template('review.html',deckname=deckname,rows=rows)
        else:
            return redirect(url_for('index'))   
       
 
@app.route('/addcard/<deckname>',methods=['GET','POST'])
def addcard(deckname):
    if request.method=="POST":
        front=request.form['front']
        back=request.form['back']
        last_rev = datetime.now()
        conn=sqlite3.connect("project.db")
        cur=conn.cursor()
        query="""INSERT INTO cards (deckname,front,back,last_rev) VALUES (?,?,?,?)"""
        cur.execute(query,(deckname,front,back,last_rev))
        conn.commit()
        return redirect(url_for('index'))
    return render_template('addcard.html',deckname=deckname)


@app.route('/deletecard/<front>')
def deletecard(front):
    conn=sqlite3.connect("project.db")
    cur=conn.cursor()
    query="""DELETE FROM cards WHERE front=?"""
    cur.execute(query,(front,))
    conn.commit()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    return redirect(url_for('login'))



if __name__=="__main__":
    app.run(debug=True)
