from flask import Flask, request, redirect, render_template ,session ,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO']=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app) 
app.secret_key = "#someSecretString"

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body , user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog',backref = 'user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')   


def get_blog_list():
    blog_list = Blog.query.all()    
    return blog_list   
    
@app.route('/', methods=['POST', 'GET'])
def home():
    
    id =  request.args.get('id')

    if id:
        blog = Blog.query.get(id)
        return render_template('displayblog.html',blog=blog)
    # if no id paramter, then render home.html
    users = User.query.all()
    
    return render_template('home.html', title="blogz!", 
        users=users)  

@app.route('/allblog', methods=['POST', 'GET'])
def allblog():
    return render_template('blogbyposts.html', title="blogz!", 
        blog_list=get_blog_list())          
        
@app.route('/allblogbypost', methods=['POST', 'GET'])
def allblogbypost():
    
    username = session.get('username')
    user =User.query.filter_by(username=username).first()
    print("allblogbypost......",user)
    if user:
        blog = Blog.query.get(user)
        return render_template('displayblog.html',blog=blog)
    
    return render_template('blogbyposts.html')  


@app.route("/addblog", methods=['POST','GET'])
def addblog():
    title_error =''
    body_error =''
    print('WE MADE IT')
    id =  request.args.get('id')
    username = session.get('username')

    user =User.query.filter_by(username=username).first()

    if request.method == 'POST':
        print('in POST part')
        title = request.form['title']
        body = request.form['body']
        #userid = request.form['']
        

        if title == "" or body =="":
            title_error="please fill title of blog" 
            body_error ="Please Fill the body of the blog"   
            return render_template("newpost.html", title_error = title_error,body_error=body_error) 
        else:        
            add_blog = Blog(title,body,user)
            db.session.add(add_blog)
            db.session.commit()
            return redirect('/?id=' + str(add_blog.id))

   
    return render_template('newpost.html')  



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']

        
        user =User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            print(session)
            return redirect('/addblog')
        else:
            flash("User password incorrect or User don't exist",'error')

    return render_template('login.html')



@app.route("/displayblog", methods=['POST','GET'])
def displayblog():

    blog_id=request.args.get("id")
    username = session.get('username')
    user =User.query.filter_by(username=username).first()
    if blog_id:

        blog=Blog.query.get(blog_id)
        return render_template("displayblog.html",blog=blog,user=user)

@app.route("/blogbyuser", methods=['POST','GET'])
def blogbyuser(): 
    #username = session.get('username')
    #blog_user = request.args.get('user')
    user = User.query.filter_by(username=session['username']).first()
    #user =User.query.filter_by(username=username ).first()
    print("username.......:",user)
    blogs = Blog.query.filter_by(user=user).all()
    
    return render_template('blogbyuser.html', 
        blogs=blogs)
        

 

@app.route('/register',methods = ['POST','GET'])
def register():
    username_error=""
    password_error=""
    verify_error=""

    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username =="" or password =="":
            username_error="please enter username"
            password_error ="Plese enter password"   
            verify_error = "Password should match"
            return render_template("register.html", username_error = username_error,password_error=password_error,verify_error=verify_error) 
        else:
            existing_user =User.query.filter_by(username=username).first()
            if not existing_user :
                new_user = User(username , password)
                session['username'] = username
                db.session.add(new_user)
                db.session.commit()

                return redirect('/')
            else:
                return '<h1>Duplicate User</h1>'
        
    return render_template('register.html')    
        

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/allblog')    

if __name__ == '__main__':
    app.run()  