import base64

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_uri = 'sqlite:///camp.db'
UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# MySQLに接続するための情報
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO']=True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# データベース作成
class Post(db.Model):
  __tablename__ = 'records'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Text)
  date = db.Column(db.Text)
  score = db.Column(db.Integer)
  review = db.Column(db.Text)
  image = db.Column(db.BLOB)
  

#アップロードされた画像の拡張子判定
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           


@app.before_first_request
def init():
    db.create_all()
  

  
@app.route('/')
def top():
  
  posts = Post.query.all()
  
  return render_template('top.html', posts = posts)

@app.route('/post')
def post_list():
    posts = Post.query.all()
    de_imgs = []
    for post in posts :
        de_imgs.append(base64.b64decode(post.image))
        
    return render_template('post_list.html', posts = posts, de_imgs = de_imgs)

@app.route('/new')
def new_post():

    message = 'New post'
    return render_template('new.html', message = message)
  
@app.route('/create', methods=['POST', 'GET'])
def create_post():

    message = 'create your memo'

    new_post = Post()
    new_post.name = request.form['title']
    new_post.date = request.form['date']
    new_post.score = request.form['score']
    new_post.review = request.form['content']
    file = request.files['image']
    img_base64 = base64.b64encode(file.read())
    # def upload_file():
    #     if request.method == 'POST':
    #         # check if the post request has the file part
    #         if 'file' not in request.files:
    #             flash('ファイルがありません')
    #             return redirect(request.url)
    #         file = request.files['image']
    #         # If the user does not select a file, the browser submits an
    #         # empty file without a filename.
    #         if file.filename == '':
    #             flash('ファイル名がありません')
    #             return redirect(request.url)
    #         if file and allowed_file(file.filename):
    #             img_base64 = base64.b64encode(file.read())
    #             print(img_base64)
    #             return img_base64
    new_post.image = img_base64
    db.session.add(new_post)
    db.session.commit()

    posts = Post.query.all()
    
    de_imgs = []
    for post in posts :
        de_imgs.append(base64.b64decode(post.image))
        


    return render_template('post_list.html', message = message, posts = posts, de_imgs = de_imgs)

@app.route('/map')
def map():
    return render_template('map.html')
