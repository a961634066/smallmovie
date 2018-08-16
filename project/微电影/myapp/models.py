from datetime import datetime
from myapp.ext import db


# 用户
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(30),unique=True)
    password = db.Column(db.Integer)
    email = db.Column(db.String(100),unique=True)
    phone = db.Column(db.String(11))
    # 个性简介
    info = db.Column(db.Text)
    # 头像
    face = db.Column(db.String(255))
    addtime = db.Column(db.DateTime,index=True,default=datetime.now)
    uuid = db.Column(db.String(255),unique=True)
    isdelete = db.Column(db.Boolean,default=False)
    userlogs = db.relationship('Userlog',backref='user',lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    moviecols = db.relationship('Moviecol', backref='user', lazy=True)

    # 定义返回类型
    def __repr__(self):
        return '<User %r>'%self.name

# 用户登录日志
class Userlog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 登录IP
    ip = db.Column(db.String(255))
    # 登录时间
    addtime = db.Column(db.DateTime,index=True,default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    # 定义返回类型
    def __repr__(self):
        return '<Userlog %r>' % self.name

# 标签
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255),unique=True)
    # 添加时间
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    movies = db.relationship('Movie',backref='tag',lazy=True)
    # 定义返回类型
    def __repr__(self):
        return '<Tag %r>' % self.name

# 电影
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255),unique=True)
    url = db.Column(db.String(255), unique=True)
    info = db.Column(db.Text)
    # 封面
    logo = db.Column(db.String(255))
    # 星级,小整形
    star = db.Column(db.SmallInteger)
    # 播放量
    playnum = db.Column(db.BigInteger)
    # 评论量
    commentnum = db.Column(db.BigInteger)
    # 上映时间
    release_time = db.Column(db.Date)
    # 时长
    alength = db.Column(db.String(255))
    # 上映地区
    area = db.Column(db.String(255))
    # 添加时间
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    # 所属标签
    tag_id = db.Column(db.Integer, db.ForeignKey(Tag.id))
    comments = db.relationship('Comment', backref='movie', lazy=True)
    moviecols = db.relationship('Moviecol', backref='movie', lazy=True)

    def __repr__(self):
        return '<Movie %r>' % self.title

# 上映预告
class Preview(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), unique=True)
    logo = db.Column(db.String(255))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    def __repr__(self):
        return '<Preview %r>' % self.title

# 评论
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    movie_id = db.Column(db.Integer,db.ForeignKey(Movie.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    def __repr__(self):
        return '<Comment %r>' % self.id

# 电影收藏
class Moviecol(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey(Movie.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    def __repr__(self):
        return '<Moviecol %r>' % self.id

# 权限
class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 名称
    name = db.Column(db.String(255), unique=True)
    # 地址
    url = db.Column(db.String(255), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    def __repr__(self):
        return '<Auth %r>' % self.name


 # 管理员
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True)
    password = db.Column(db.Integer)
    # 是否为超级管理员
    is_super = db.Column(db.SmallInteger)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    adminlogs = db.relationship('Adminlog',backref='admin',lazy=True)
    oplogs = db.relationship('Oplog', backref='admin', lazy=True)

    def __repr__(self):
        return '<Admin %r>' % self.id


 # 管理员登录日志
class Adminlog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 登录IP
    ip = db.Column(db.String(255))
    # 登录时间
    addtime = db.Column(db.DateTime,index=True,default=datetime.now)
    admin_id = db.Column(db.Integer, db.ForeignKey(Admin.id))
    # 定义返回类型
    def __repr__(self):
        return '<Adminlog %r>' % self.id

# 后台操作日志
class Oplog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 登录IP
    ip = db.Column(db.String(255))
    # 登录时间
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    # # 操作原因
    reason = db.Column(db.String(255))
    admin_id = db.Column(db.Integer, db.ForeignKey(Admin.id))
    def __repr__(self):
        return '<Oplog %r>' % self.id


