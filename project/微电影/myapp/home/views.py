import json
import os,uuid,datetime
from functools import wraps
from operator import and_

from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from myapp.ext import db
from myapp.home.forms import RegisterForm, LoginForm, CommentForm
from myapp.models import User, Userlog, Preview, Tag, Movie, Comment, Moviecol

# 蓝图注册
from myapp.sttings import UPLOAD_LOGO_USER
blue = Blueprint('project', __name__)
def init_blue(app):
    app.register_blueprint(blueprint=blue)



# 判断登录装饰器
def user_login(func):
    @wraps(func)
    def decorate_function(*args,**kwargs):
        if 'user' not in session:                           # 登录成功时，将'user'存入了session中
            flash('你还没有登录！')
            return redirect(url_for('project.login'))
        return func(*args,**kwargs)
    return decorate_function

# 定义全局变量，列表每页显示数量
limits = 10
################################################################################################
# 首页
@blue.route('/index/',methods=['GET'])
@blue.route('/index/<int:page>/',methods=['GET'])
def home(page=None):
    tags = Tag.query.all()
    movie_data = Movie.query
    # 通过url获取参数
    tid = request.args.get("tid",0)                             # 标签
    if int(tid) != 0:
        movie_data = movie_data.filter_by(tag_id=int(tid))

    star = request.args.get("star",0)                           # 星级
    if int(star) != 0:
        movie_data = movie_data.filter_by(star=int(star))

    time = request.args.get("time",0)                          # 上映时间
    if int(time) != 0:
        if int(time) == 1:
            movie_data = movie_data.order_by(Movie.addtime.desc())
        else:
            movie_data = movie_data.order_by(Movie.addtime)

    pm = request.args.get("pm",0)                               # 播放数量
    if int(pm) == 1:
        movie_data = movie_data.order_by(Movie.playnum.desc())
    elif int(pm)==2:
        movie_data = movie_data.order_by(Movie.playnum)

    cm = request.args.get("cm",0)                                # 评论数量
    if int(cm) == 1:                                             # 从高到低排序
        movie_data = movie_data.order_by(Movie.commentnum.desc())
    elif int(cm) == 1:                                          # 从低到高排序
        movie_data = movie_data.order_by(Movie.commentnum)

    # 保存获取的参数
    td = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )
    page_data = movie_data.paginate(page, limits)                     # 分页
    return render_template('home/index.html',tags=tags,td=td,page_data=page_data)


# 注册
@blue.route('/register/',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():                                       # 是否是表单提交
        data = form.data                                                # 获取提交数据，返回结果字典
        if User.query.filter(User.name==data['name']).count()>0:          # 判断注册昵称是否存在                                          # 用户名已存在
            flash('此昵称已存在！请重新输入！','err')                 # 闪现提示信息
            return redirect(url_for('project.register'))
        elif User.query.filter_by(email=data['email']).count()>0:      # 判断邮箱是否存在                                              # 用户名已存在
            flash('此邮箱已存在！请重新输入！','err')
            return redirect(url_for('project.register'))
        else:                                                          # 判断完成后，进行注册，数据库储存
            user = User()
            user.name = data['name']
            user.password = int(data['pwd'])
            user.email = data['email']
            user.phone = data['phone']
            user.info = data.get('info','这家伙很懒，什么都没有写')
            user.uuid = uuid.uuid4().hex
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('project.login'))
    return render_template('home/register.html',form=form)


# 登录
@blue.route('/login/',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():                                     # 如果是表单提交
        data = form.data
        user = User.query.filter_by(name=data['name'])
        if  user.count()>0:                                           # 账号过滤，确认会员是否存在
            if user.first().password == int(data['pwd']):            # 会员存在，判断会员的密码是够正确
                session['user'] = user.first().name                  # 登录成功，对用户进行标识
                session['user_id'] = user.first().id
                userlog = Userlog(                                   # 登录日志的保存
                    user_id=user.first().id,
                    ip=request.remote_addr
                )
                db.session.add(userlog)
                db.session.commit()
                return redirect(url_for('project.user'))
            else:
                flash('密码错误，请重新输入！')
                return redirect(url_for('project.login'))
        else:
            flash('此账号不存在')
            return redirect(url_for('project.login'))
    return render_template('home/login.html',form=form)


# 退出
@blue.route('/loginout/',methods=['GET','POST'])
@user_login
def loginout():
    session.pop('user')
    session.pop('user_id')
    return redirect(url_for('project.login'))


################################################################################################
# 用户信息界面
@blue.route('/user/',methods=['GET','POST'])
@user_login
def user():
    user = User.query.get(int(session['user_id']))
    if request.method == 'GET':
        return render_template('home/user.html',user=user)
    if request.method == 'POST':
        name = request.form.get('name')                                 # 昵称
        email= request.form.get('email')                                # 邮箱
        info = request.form.get('info')                                 # 手机
        face = request.files.get('face')                                # 头像
        phone = request.form.get('phone')
        if user.name != name and User.query.filter_by(name=name).count()>0:      # 判断输入昵称是否存在
            flash('昵称已存在！','err')
            return redirect(url_for('project.user'))
        if user.email != email and User.query.filter_by(email=email).count()>0:   # 判断输入邮箱是否存在
            flash('邮箱已存在！','err')
            return redirect(url_for('project.user'))
        if not os.path.exists(UPLOAD_LOGO_USER):                        # 判断保存头像的文件夹是否存在
            os.makedirs(UPLOAD_LOGO_USER,'rw')
        if face.filename != '':                                         # 判断是够上传头像
            if user.face is not None:
                if  os.path.exists(UPLOAD_LOGO_USER+user.face):              # 首先删除原头像
                    os.remove(UPLOAD_LOGO_USER+user.face)
            face_name = face.filename                                    # 新头像文件名
            # 进行文件名唯一性编码
            face_name_bm = '%s_%s_%s' % (
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"),uuid.uuid4(),face_name)
            face_path = os.path.join(UPLOAD_LOGO_USER+face_name_bm)
            face.save(face_path)
            user.face = face_name_bm
        user.name = name
        user.email = email
        user.info = info
        user.phone = phone
        db.session.add(user)
        db.session.commit()
        flash('修改成功！','ok')
        return redirect(url_for('project.user'))



# 修改密码界面
@blue.route('/changepwd/',methods=['GET','POST'])
@user_login
def pwd():
    if request.method == 'GET':
        return render_template('home/changepwd.html')
    elif request.method == 'POST':
        user = User.query.get(session['user_id'])
        oldpwd = int(request.form.get('oldpwd'))
        newpwd = request.form.get('newpwd')
        if user.password == oldpwd:                              # 验证密码是否正确
            user.password = newpwd
            db.session.add(user)
            db.session.commit()
            flash('修改密码成功，请重新登录！', 'ok')
            return redirect(url_for('project.loginout'))
        else:
            flash('原密码不正确！','err')
            return redirect(url_for('project.pwd'))



# 登录日志
@blue.route('/loginlog/<int:page>/',methods=['GET'])
@user_login
def loginlog(page=None):
    if page == None:
        page = 1
    loginlog = Userlog.query.filter_by(user_id=session['user_id']).paginate(page,limits)
    return render_template('home/loginlog.html',loginlog=loginlog)


# 评论界面
@blue.route('/comments/<int:page>/')
@user_login
def comments(page=None):
    if page == None:
        page = 1
    comments = Comment.query.filter(and_(Comment.user_id==session['user_id'],Comment.movie_id==Movie.id)).order_by(Comment.addtime.desc()).paginate(page,limits)
    return render_template('home/comments.html',comments=comments)


# 添加取消收藏
@blue.route('/moviecol/edit/',methods=['GET'])
@user_login
def moviecol_edit():
    mid = int(request.args.get('mid'))
    uid = int(request.args.get('uid'))
    moviecol = Moviecol.query.filter(and_(Moviecol.movie_id==mid,Moviecol.user_id==uid)).first()
    if moviecol:                   # 说明已经收藏,此次点击是取消
        data = dict(ok=0)
        db.session.delete(moviecol)
        db.session.commit()
        flash('取消收藏成功')
    else:                                   # 说明未收藏,此次点击是添加
        data = dict(ok=1)
        moviecol = Moviecol(
            user_id=uid,
            movie_id=mid
        )
        db.session.add(moviecol)
        db.session.commit()
        flash('收藏成功')
    return json.dumps(data)

# 收藏电影
@blue.route('/moviecol/<int:page>/',methods=['GET'])
@user_login
def moviecol(page=None):
    if page == None:
        page = 1
    moviecols = Moviecol.query.filter(
                Moviecol.user_id==session['user_id'],
                Moviecol.movie_id==Movie.id).order_by(Moviecol.addtime).paginate(page,limits)
    return render_template('home/moviecol.html',moviecols=moviecols)


# 上映预告(动画)
@blue.route('/animation/')
def animation():
    previews = Preview.query.all()
    return render_template('home/animation.html',previews = previews)


# 电影搜索
@blue.route('/search/<int:page>/',methods=['GET'])
def search(page=None):
    if page == None:
        page = 1
    value = request.args.get('value','')
    movie_count = Movie.query.filter(Movie.title.like("%" + value + "%")).count()
    if value == '':
        return redirect(url_for('project.home'))
    movies = Movie.query.filter(Movie.title.like("%"+value+"%")).paginate(page,limits)
    return render_template('home/search.html',movies=movies,value=value,movie_count=movie_count)


#  电影播放界面
@blue.route('/play/<int:id>/<int:page>/',methods=['GET','POST'])
def play(id,page=None):
    movie = Movie.query.get(id)
    if page ==  None:
        page = 1
    comments = Comment.query.filter(and_(Comment.movie_id==movie.id,Comment.user_id==User.id)).order_by(Comment.addtime.desc()).paginate(page,limits)
    form = CommentForm()
    if form.validate_on_submit():
        data = form.data
        comment = Comment(
            content= data['content'],
            movie_id = movie.id,
            user_id = session['user_id']
        )
        movie.commentnum += 1                       # 评论数量 + 1
        db.session.add(movie)
        db.session.add(comment)
        db.session.commit()
        flash('提交评论成功！','ok')
        return redirect(url_for('project.play',id=movie.id,page=1))
    movie.playnum += 1                              # 播放数量 + 1
    db.session.add(movie)
    db.session.commit()
    moviecol = Moviecol.query.filter(Moviecol.user_id==session['user_id'],Moviecol.movie_id==id).first()
    return render_template('home/play.html',movie=movie,form=form,comments=comments,moviecol=moviecol)



