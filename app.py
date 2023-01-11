import base64, re, googlemaps, folium

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMBLOB, DATE
from sqlalchemy.sql import func


app = Flask(__name__)

UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# MySQLに接続するための情報
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
      'user': "Kta0000",
      'password': "----",
      'host': "Kta0000.mysql.pythonanywhere-services.com",
      'db_name': "Kta0000$test"
  })
# おまじない
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# dbの初期化
db = SQLAlchemy(app)


# データベース作成
class Post(db.Model):
    """
        Memoモデルの定義
    """
    __tablename__ = "memos"

    id = db.Column("id", INTEGER(11), primary_key=True)
    name = db.Column(db.Text)
    adress = db.Column(db.Text)
    lat = db.Column(db.Numeric(9,6))
    lng = db.Column(db.Numeric(9,6))
    date = db.Column(DATE)
    score = db.Column(db.Integer)
    review = db.Column(db.Text)
    image = db.Column(MEDIUMBLOB)
  

#アップロードされた画像の拡張子判定
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           


@app.before_first_request
def init():
    db.create_all()
  

#トップページ
@app.route('/')
def top():
  
  posts = Post.query.all()
  #キャンプ回数
  camp_count = Post.query.count()
  #最後に行った日
  latest_date = db.session.query(func.max(Post.date)).one()
  latest_date = str(latest_date)
  new_latest = re.sub('datetime.date|\(|\)|', '',latest_date)
  new_latest = re.sub(',', '.',new_latest)
  
  #画像データを表示できるように加工
  filebinary = []
  for post in posts :
        img_base64_string = re.sub('b\'|\'', '', str(post.image))
        filebinary.append(f'data:image/png;base64,{img_base64_string}')
  
  
  return render_template('top.html', posts = posts, camp_count = camp_count, new_latest = new_latest, filebinary =filebinary)

#投稿をリスト表示
@app.route('/post')
def post_list():
    posts = Post.query.all()
    filebinary = []
    for post in posts :
        img_base64_string = re.sub('b\'|\'', '', str(post.image))
        filebinary.append(f'data:image/png;base64,{img_base64_string}')

        
    return render_template('post_list.html', posts = posts, filebinary = filebinary)

#新規作成
@app.route('/new')
def new_post():

    message = 'New post'
    return render_template('new.html', message = message)
  
#作成完了
@app.route('/create', methods=['POST', 'GET'])
def create_post():

    message = 'create your memo'
    #作成したデータを追加
    new_post = Post()
    new_post.name = request.form['title']
    new_post.adress = request.form['adress']
    new_post.date = request.form['date']
    new_post.score = request.form['score']
    new_post.review = request.form['content']
    #画像データをエンコード
    file = request.files['image']
    img_base64 = base64.b64encode(file.stream.read())
    new_post.image = img_base64
    
    #住所から緯度経度を算出
    location = new_post.adress
    gm = googlemaps.Client(key='AIzaSyDDRUKKjqJDkDZrSePsD1Y_AbhpfGt8WQw')
    res = gm.geocode(location)
    try:
        new_post.lat = res[0]['geometry']['location']['lat']
        new_post.lng = res[0]['geometry']['location']['lng']
        print(res[0]['geometry']['location'])
    except IndexError:
        print("リストに関するエラー")
    finally:
        db.session.add(new_post)
        db.session.commit()

    posts = Post.query.all()
    
    
    filebinary = []
    for post in posts :
        img_base64_string = re.sub('b\'|\'', '', str(post.image))
        filebinary.append(f'data:image/png;base64,{img_base64_string}')

    return render_template('post_list.html', message = message, posts = posts, filebinary = filebinary)

#記録の詳細
@app.route('/post/detail/<int:id>')
def detail(id):
    post = Post.query.get(id)
    img_base64_string = re.sub('b\'|\'', '', str(post.image))
    image = f'data:image/png;base64,{img_base64_string}'
    return render_template('detail.html' , post = post, image = image)

#編集
@app.route('/edit/<int:id>')
def edit(id):
    post = Post.query.get(id)
    
    return render_template('edit.html', post = post)

#編集完了
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    
    update_post = Post.query.get(id)
    update_post.name = request.form['title']
    update_post.adress = request.form['adress']
    update_post.date = request.form['date']
    update_post.score = request.form['score']
    update_post.review = request.form['content']
    #画像データをエンコード
    file = request.files['image']
    img_base64 = base64.b64encode(file.stream.read())
    update_post.image = img_base64
    
    #住所から緯度経度を算出
    location = update_post.adress
    gm = googlemaps.Client(key='---')
    res = gm.geocode(location)
    try:
        update_post.lat = res[0]['geometry']['location']['lat']
        update_post.lng = res[0]['geometry']['location']['lng']
        print(res[0]['geometry']['location'])
    except IndexError:
        print("リストに関するエラー")
    finally:
        db.session.add(update_post)
        db.session.commit()

    posts = Post.query.all()
    
    
    filebinary = []
    for post in posts :
        img_base64_string = re.sub('b\'|\'', '', str(post.image))
        filebinary.append(f'data:image/png;base64,{img_base64_string}')

    return render_template('post_list.html',  posts = posts, filebinary = filebinary)

#削除
@app.route('/delete/<int:id>')
def delete(id):
    delete_post = Post.query.get(id)
    db.session.delete(delete_post)
    db.session.commit()
    
    posts = Post.query.all()
    
    
    filebinary = []
    for post in posts :
        img_base64_string = re.sub('b\'|\'', '', str(post.image))
        filebinary.append(f'data:image/png;base64,{img_base64_string}')

    return render_template('post_list.html',  posts = posts, filebinary = filebinary)
    
#地図表示
@app.route('/map')
def map():
    map = folium.Map(
        location=[35.138389322863596, 136.92635803665982],
        zoom_start=6
    )
    posts = Post.query.all()
    for post in posts:
        #緯度経度のデータが無いときは回避
        if not post.lat:
            continue
        if post.score == 1:
            pop = post.name+ "<br> " +str(post.date) + "<br> ★☆☆☆☆" 
        elif post.score == 2:
            pop = post.name+ "<br> " +str(post.date) + "<br> ★★☆☆☆" 
        elif post.score == 3:
            pop = post.name+ "<br> " +str(post.date) + "<br> ★★★☆☆" 
        elif post.score == 4:
            pop = post.name+ "<br> " +str(post.date) + "<br> ★★★★☆" 
        elif post.score == 5:
            pop = post.name+ "<br> " +str(post.date) + "<br> ★★★★★" 
        folium.Marker(
            location=[post.lat, post.lng],
            popup=folium.Popup(pop, max_width=500, min_width=0),
            icon=folium.Icon(icon="tree-conifer", icon_color='#F0F0F0', color="green")
        ).add_to(map)
    return map._repr_html_()
