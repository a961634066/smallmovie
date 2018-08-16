import os, uuid, datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from myapp.admin.forms import LoginForm, TagForm, PreviewForm, PwdForm, AuthForm, AdminForm
from myapp.ext import db
from myapp.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol, Adminlog, Oplog, Userlog, Auth
from myapp.sttings import UPLOAD_DIR, UPLOAD_VIDEO, UPLOAD_LOGO, UPLOAD_LOGO_USER
from sqlalchemy import or_




# 蓝图
admin = Blueprint('admin', __name__)
def init_blue_admin(app):
    app.register_blueprint(blueprint=admin, url_prefix='/admin')


# 定义上下文处理器（可以将变量直接给模板使用）
@admin.context_processor
def template():
    if 'admin' in session:
        admin = Admin.query.filter_by(id=session['admin_id']).first()
        register_time = admin.addtime
        statu = '在线'
    else:
        register_time = None
        statu = '不在线'
    data = dict(register_time = register_time,statu = statu)
    return data

# 定义全局变量，每页列表显示页数
limits = 10

# 定义登录判断装饰器
def admin_login(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # session不存在时请求登录
        if "admin" not in session:
            flash('你还没有登录！')
            return redirect(url_for("admin.login", next=request.url))  # 跳转到登录页，并获取到跳转地址
        return func(*args, **kwargs)
    return decorated_function


# 后台页面
@admin.route('/')
@admin_login
def adm():
    return render_template('admin/admin.html')


# 控制面板
@admin.route('/index/')
@admin_login
def index():
    return render_template('admin/index.html')


# 后台登录
@admin.route('/login/', methods=['GET', 'POST'])
def login():
    # 导入登录表单
    form = LoginForm()
    if form.validate_on_submit():                                             # 验证是否有提交表单，POST请求
        data = form.data                                                      # 获取数据，格式类似于字典,里边数据是字符串格式
        admin = Admin.query.filter_by(name=data['account']).first()          # 通过姓名过滤
        if admin:                                                             # 管理员用户名存在
            # if not check_password_hash(str(admin.password),data['pwd']):   # 哈希密文密码判断
            if not admin.password == int(data['pwd']):                      # 判断密码是否正确
                flash('密码错误!')                                          # 消息闪现,错误提示
                return redirect(url_for('admin.login'))
            session['admin'] = data['account']
            session['admin_id'] = admin.id
            adminlog = Adminlog()                                                # 保存登录日志
            adminlog.ip = request.remote_addr                                 # 获取登录IP
            adminlog.admin_id = admin.id                                       # 管理员id
            db.session.add(adminlog)
            db.session.commit()
            return redirect(request.args.get("next") or url_for('admin.adm'))  # 重定向到后台首页
        else:                                                                 # 用户名不存在
            flash('用户名错误！')
            return render_template('admin/login.html', form=form)
    else:                                                                     # 不是表单提交
        return render_template('admin/login.html', form=form)


# 后台退出
@admin.route('/loginout/',methods=['GET'])
@admin_login
def loginout():
    session.pop('admin')
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route('/pwd/',methods=['POST','GET'])
@admin_login
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session['admin']).first()
        if int(data['old_pwd']) == admin.password:                        # 此处可进行哈希摩玛加密，此处未加密
            admin.password = int(data['new_pwd'])
            db.session.add(admin)
            db.session.commit()
            return redirect(url_for('admin.loginout'))
        else:
            flash('旧密码输入错误，请重新输入！','err')
            return redirect(url_for('admin.pwd'))
    return render_template('admin/pwd.html',form=form)


# 标签添加
@admin.route('/tag/add/', methods=['GET', 'POST'])
@admin_login
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data['name']).count()
        if tag == 1:  # 说明标签存在
            flash('标签已存在，请重新添加', 'err')
            return redirect(url_for('admin.tag_add'))
        else:  # 标签不存在，存入数据库
            tag = Tag()
            tag.name = data['name']
            db.session.add(tag)
            db.session.commit()
            flash('添加标签成功！', 'ok')
            oplog = Oplog(
                admin_id=session["admin_id"],
                ip=request.remote_addr,
                reason="添加新标签：%s" % data["name"]
            )
            db.session.add(oplog)
            db.session.commit()
            return redirect(url_for('admin.tag_add'))
    return render_template('admin/tag_add.html', form=form)


# 标签列表
@admin.route('/tag/list/')
@admin.route('/tag/list/<int:page>', methods=['GET'])
@admin_login
def tag_list(page=None):
    if page == None:
        page = 1
    page_data = Tag.query.paginate(page,limits)  # 先所有的标签，然后根据前端请求页码分页
    return render_template('admin/tag_list.html', paginate=page_data)


# 删除标签
@admin.route('/tag/del/<int:id>', methods=['GET'])
@admin_login
def del_tag(id):
    tag = Tag.query.get_or_404(id)  # 对于不存在的，会跳转到404页面
    db.session.delete(tag)
    db.session.commit()
    flash('删除标签成功！', 'ok')
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除标签：%s" % tag.name
    )
    db.session.add(oplog)
    db.session.commit()
    return redirect(url_for('admin.tag_list'))


# 编辑标签
@admin.route('/tag/edit/<int:id>/', methods=['GET', 'POST'])
@admin_login
def tag_edit(id):
    form = TagForm()
    tag = Tag.query.get_or_404(id)
    if request.method == 'GET':
        return render_template('admin/tag_edit.html', tag=tag, form=form)
    elif request.method == 'POST':
        data = form.data
        tag_count = Tag.query.filter_by(name=data['name']).count()  # 通过输入过滤是否已有标签
        if tag_count > 0:  # 数据库已存在修改标签名
            flash('标签名已存在，请重新输入！', 'err')
            return redirect(url_for('admin.tag_edit', id=id))
        else:
            oplog = Oplog(
                admin_id=session["admin_id"],
                ip=request.remote_addr,
                reason="修改标签“%s”为“%s”" % (tag.name, data["name"])
            )
            db.session.add(oplog)
            db.session.commit()

            tag.name = data['name']
            db.session.add(tag)
            db.session.commit()
            flash('标签已更改！', 'ok')
            return render_template('admin/tag_edit.html', form=form, tag=tag)


# 电影添加
@admin.route('/movie/add/', methods=['GET', 'POST'])
@admin_login
def movie_add():
    tags = Tag.query.all()
    if request.method == 'GET':
        return render_template('admin/movie_add.html', tags=tags)
    elif request.method == 'POST':
        input_title = request.form.get('input_title')               # 片名
        input_url = request.files.get('input_url')                   # 文件名
        input_info = request.form.get('input_info')                 # 介绍
        input_logo = request.files.get('input_logo')                 # 封面
        input_star = request.form.get('input_star')                 # 星级
        input_area = request.form.get('input_area')                 # 地区
        input_length = request.form.get('input_length')               # 片长
        input_release_time = request.form.get('input_release_time')  # 上映时间
        input_tag_id = request.form.get('input_tag_id')               # 标签

        movie = Movie.query.filter(Movie.title == input_title)
        if movie.count() > 0:  # 说明影片已存在
            flash('影片已存在，请添加别的影片', 'err')
            return redirect(url_for('admin.movie_add'))
        if not os.path.exists(UPLOAD_DIR):              # 保存地址拼接,判断保存文件夹是否存在
            os.makedirs(UPLOAD_DIR)                      # 不存在，则创建目录
            os.chmod(UPLOAD_DIR, 'rw')                  # 给文件夹读写权限
        url_name = input_url.filename                    # 上传文件需要处理,但secure_filename取不出来中文名
        logo_name = input_logo.filename
        url_name_bm = '%s_%s_%s' % (
            datetime.datetime.now().strftime("%Y%m%d%H%M%S"), uuid.uuid4(), url_name)  # 对图片名进行编码唯一性
        logo_name_bm = '%s_%s_%s' % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), uuid.uuid4(), logo_name)
        url_path = os.path.join(UPLOAD_VIDEO, url_name_bm)
        logo_path = os.path.join(UPLOAD_LOGO, logo_name_bm)
        input_url.save(url_path)
        input_logo.save(logo_path)
        movie = Movie(
            title=input_title,
            url=url_name_bm,
            info=input_info,
            logo=logo_name_bm,
            star=int(input_star),
            area=input_area,
            alength=input_length,
            tag_id=int(input_tag_id),
            release_time=input_release_time,
            playnum=0,
            commentnum=0
        )
        db.session.add(movie)
        db.session.commit()
        flash('添加成功！', 'ok')
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加新电影：%s" % movie.title
        )
        db.session.add(oplog)
        db.session.commit()
        return render_template('admin/movie_add.html')


# 电影列表
@admin.route('/movie/list/<int:page>', methods=['GET'])
@admin_login
def movie_list(page):
    if page is None:
        page = 1
    movies = Movie.query.paginate(page, limits)
    return render_template('admin/movie_list.html', movies=movies)


# 删除电影
@admin.route('/movie/del/<int:id>', methods=['GET'])
@admin_login
def movie_del(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    flash('删除电影成功！', 'ok')
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除电影：%s" % movie.title
    )
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除电影：%s" % movie.title
    )
    db.session.add(oplog)
    db.session.commit()
    return redirect(url_for('admin.movie_list', page=1))


# 编辑电影
@admin.route('/movie/edit/<int:id>', methods=['GET', 'POST'])
@admin_login
def movie_edit(id):
    movie = Movie.query.get_or_404(id)
    tags = Tag.query.all()
    if request.method == 'GET':
        return render_template('admin/movie_edit.html', movie=movie, tags=tags)
    elif request.method == 'POST':
        input_title = request.form.get('input_title')                # 片名
        input_url = request.files.get('input_url')                  # 文件名
        input_info = request.form.get('input_info')                 # 介绍
        input_logo = request.files.get('input_logo')                 # 封面
        input_star = request.form.get('input_star')                 # 星级
        input_area = request.form.get('input_area')                  # 地区
        input_length = request.form.get('input_length')              # 片长
        input_release_time = request.form.get('input_release_time')  # 上映时间
        input_tag_id = request.form.get('input_tag_id')              # 标签

        if input_url != None:
            if os.path.exists(UPLOAD_VIDEO + movie.url):             # 如果老文件存在，删除老文件
                os.remove(UPLOAD_VIDEO + movie.url)
            url_name = input_url.filename                              # 上传文件需要处理
            url_name_bm = '%s_%s_%s' % (
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"), uuid.uuid4(), url_name)  # 对图片名进行编码唯一性
            url_path = os.path.join(UPLOAD_VIDEO, url_name_bm)
            input_url.save(url_path)                                 # 保存
            movie.url = url_name_bm


        if input_logo != None:
            if os.path.exists(UPLOAD_LOGO + movie.logo):             # 如果老文件存在，删除老文件
                os.remove(UPLOAD_LOGO + movie.logo)
            logo_name = input_logo.filename
            logo_name_bm = '%s_%s_%s' % (
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"), uuid.uuid4(), logo_name)
            logo_path = os.path.join(UPLOAD_LOGO, logo_name_bm)
            input_logo.save(logo_path)
            movie.logo = logo_name_bm
        if input_title == movie.title:
            oplog = Oplog(
                admin_id=session["admin_id"],
                ip=request.remote_addr,
                reason="修改电影：%s 成功！" % input_title
            )
        else:
            oplog = Oplog(
                admin_id=session["admin_id"],
                ip=request.remote_addr,
                reason="修改电影：%s（原名：%s）" % (input_title, movie.title)
            )
        db.session.add(oplog)
        db.session.commit()

        movie.title = input_title
        movie.info = input_info
        movie.star = int(input_star)
        movie.area = input_area
        movie.alength = input_length
        movie.tag_id = int(input_tag_id)
        movie.release_time = input_release_time
        db.session.add(movie)
        db.session.commit()
        flash('编辑成功！', 'ok')
        return redirect(url_for("admin.movie_list", page=1))


# 预告添加
@admin.route('/preview/add/', methods=['GET', 'POST'])
@admin_login
def preview_add():
    form = PreviewForm()
    data = form.data
    if form.validate_on_submit():
        preview_count = Preview.query.filter_by(title=data['title']).count()
        if preview_count > 0:  # 预告片已存在
            flash('此预告片已存在，请添加别的影片！', 'err')
            return redirect(url_for('admin.preview_add'))
        else:
            preview = Preview()
            logo_name = form.logo.data.filename
            # 进行唯一性地址拼接
            logo_name_bm = '%s_%s_%s' % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), uuid.uuid4(), logo_name)
            logo_path = os.path.join(UPLOAD_LOGO, logo_name_bm)
            if not os.path.exists(UPLOAD_LOGO):
                os.makedirs(UPLOAD_LOGO)
                os.chmod(UPLOAD_LOGO, "rw")
            form.logo.data.save(logo_path)
            preview.title = data['title']
            preview.logo = logo_name_bm
            db.session.add(preview)
            db.session.commit()
            flash('添加预告成功！', 'ok')
            oplog = Oplog(
                admin_id=session["admin_id"],
                ip=request.remote_addr,
                reason="添加新电影预告：%s" % data["title"]
            )
            db.session.add(oplog)
            db.session.commit()
            return redirect(url_for("admin.preview_add"))
    return render_template('admin/preview_add.html', form=form)


# 预告编辑
@admin.route('/preview/edit/<int:id>', methods=['GET', 'POST'])
@admin_login
def preview_edit(id):
    form = PreviewForm()
    preview = Preview.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        previews = Preview.query.filter_by(title=data['title']).count()
        if previews > 0:
            flash('此预告名已存在！', 'err')
            return redirect(url_for('admin.preview_edit', id=id))
        else:
            if form.logo.data.filename != None:
                logo_name = form.logo.data.filename
                logo_name_bm = '%s_%s_%s' % (
                    datetime.datetime.now().strftime("%Y%m%d%H%M%S"), uuid.uuid4(), logo_name)
                logo_path = os.path.join(UPLOAD_LOGO, logo_name_bm)
                data['logo'].save(logo_path)
                preview.logo = logo_name_bm
                if os.path.exists(UPLOAD_LOGO + preview.logo):
                    os.remove(UPLOAD_LOGO + preview.logo)
            preview.title = data['title']
            db.session.add(preview)
            db.session.commit()
            flash('编辑成功！', 'ok')
            oplog = Oplog(
                admin_id=session["admin_id"],
                ip=request.remote_addr,
                reason="修改电影预告：%s（原名：%s）" % (data["title"], preview.title)
            )
            db.session.add(oplog)
            db.session.commit()
            return redirect(url_for('admin.preview_edit', id=id))
    return render_template('admin/preview_edit.html', form=form, preview=preview)


# 预告删除
@admin.route('/preview/del/<int:id>', methods=['GET'])
@admin_login
def preview_del(id):
    preview = Preview.query.get_or_404(id)
    if preview is None:
        flash('删除的预告片不存在！', 'err')
        return redirect(url_for('admin.preview_list'))
    else:
        db.session.delete(preview)
        db.session.commit()
        flash('删除成功', 'ok')
        if os.path.exists(UPLOAD_LOGO + preview.logo):
            os.remove(UPLOAD_LOGO + preview.logo)
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="删除电影预告：%s" % preview.title
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for('admin.preview_list', page=1))


# 预告列表
@admin.route('/preview/list/<int:page>', methods=['GET', 'POST'])
@admin_login
def preview_list(page=None):
    if page is None:
        page = 1
    paginate_data = Preview.query.paginate(page, limits)
    return render_template('admin/preview_list.html', paginate_data=paginate_data)


# 会员列表
@admin.route('/user/list/<int:page>/',methods=['GET'])
@admin_login
def user_list(page=None):
    if page is None:
        page = 1
    users = User.query.filter_by(isdelete=False).paginate(page, limits)
    return render_template('admin/user_list.html', users=users)


# 会员信息
@admin.route('/user/view/<int:id>',methods=['GET'])
@admin_login
def user_view(id):
    user = User.query.filter(User.isdelete==False).filter(User.id==id).first()
    return render_template('admin/user_view.html',user=user)


# 删除会员
@admin.route('/user/view/<int:id>/', methods=['GET'])
@admin_login
def user_del(id):
    user = User.query.get(id)
    if user is None:
        flash('此会员不存在！', 'err')
        return redirect(url_for('admin.user_list', page=1))
    else:
        user.isdelete = True
        db.session.add(user)
        db.session.commit()
        flash("删除会员成功！", "ok")
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="删除会员：%s" % user.name
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for('admin.user_list', page=1))


# 评论管理列表
@admin.route('/comments/list/<int:page>/',methods=['GET'])
@admin_login
def comments(page=None):
    if page == None:
        page = 1
    comments = Comment.query.filter(User.id==Comment.user_id,Movie.id==Comment.movie_id).paginate(page,5)
    return render_template('admin/comment_list.html',comments=comments)


# 评论删除
@admin.route('/comments/del/<int:id>/',methods=['GET'])
@admin_login
def comment_del(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('删除成功！','ok')
    return redirect(url_for('admin.comments',page=1))


# 电影收藏管理列表
@admin.route('/moviecol/list/<int:page>/',methods=['GET'])
@admin_login
def moviecol_list(page=None):
    if page == None:
        page = 1
    moviecols = Moviecol.query.filter(User.id==Moviecol.user_id,Movie.id==Moviecol.movie_id).paginate(page,5)
    return render_template('admin/moviecol_list.html',moviecols=moviecols)


# 删除收藏
@admin.route('/moviecol/del/<int:id>/',methods=['GET'])
@admin_login
def moviecol_del(id):
    moviecol = Moviecol.query.get_or_404(id)
    db.session.delete(moviecol)
    db.session.commit()
    flash('删除成功！','ok')
    return redirect(url_for('admin.moviecol_list',page=1))


# 管理员操作日志列表
@admin.route('/oplog/list/<int:page>/',methods=['GET'])
@admin_login
def oplog_list(page=None):
    if page == None:
        page = 1
    oplogs = Oplog.query.filter(Oplog.admin_id == Admin.id).paginate(page,10)
    return render_template('admin/oplog_list.html',oplogs=oplogs)


# 管理员登录日志列表
@admin.route('/adminloginlog/list/<int:page>/',methods=['GET'])
@admin_login
def adminloginlog_list(page=None):
    if page == None:
        page = 1
    adminlogs = Adminlog.query.filter(Adminlog.admin_id == Admin.id).paginate(page,10)
    return render_template('admin/adminloginlog_list.html',adminlogs=adminlogs)


# 会员登录日志列表
@admin.route('/userloginlog/list/<int:page>/')
@admin_login
def userloginlog_list(page=None):
    if page == None:
        page = 1
    userlogs = Userlog.query.filter_by(user_id=User.id).paginate(page,limits)
    return render_template('admin/userloginlog_list.html',userlogs=userlogs)


# 权限添加
@admin.route('/auth/add/',methods=['GET','POST'])
@admin_login
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth.query.filter(or_(Auth.name == data['name'],Auth.url == data['url']))
        if auth.count()>0:
            flash('权限名或地址已存在！','err')
            return redirect(url_for('admin.auth_add'))
        auth = Auth()
        auth.name = data['name']
        auth.url = data['url']
        db.session.add(auth)
        db.session.commit()
        flash('权限添加成功！','ok')
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加新权限：%s" % data["name"]
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for('admin.auth_add'))
    return render_template('admin/auth_add.html',form=form)


# 权限列表
@admin.route('/auth/list/<int:page>/',methods=['GET'])
@admin_login
def auth_list(page=None):
    if page == None:
        page = 1
    auths = Auth.query.paginate(page,limits)
    return render_template('admin/auth_list.html',auths=auths)

# 删除权限
@admin.route('/auth/del/<int:id>/',methods=['GET'])
@admin_login
def auth_del(id):
    auth = Auth.query.get_or_404(id)
    db.session.delete(auth)
    db.session.commit()
    flash('删除权限成功！','ok')
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除权限：%s" % auth.name
    )
    db.session.add(oplog)
    db.session.commit()
    return redirect(url_for('admin.auth_list',page=1))


# 编辑权限
@admin.route('/auth/edit/<int:id>/',methods=['GET','POST'])
@admin_login
def auth_edit(id):
    form = AuthForm()
    auth = Auth.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        auth.name = data['name']
        auth.url = data['url']
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="修改权限：%s（原名：%s）" % (data["name"], auth.name)
        )
        db.session.add(oplog)
        db.session.commit()

        db.session.add(auth)
        db.session.commit()
        flash('修改权限成功！','ok')
        return redirect(url_for('admin.auth_list',page=1))
    return render_template('admin/auth_edit.html',form=form,auth=auth)



# 管理员添加
@admin.route('/admin/add/',methods=['GET','POST'])
@admin_login
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data['name'])
        if admin.count() > 0:                                             # 说明管理员名已存在
            flash('此管理员已存在！请重新添加！','err')
            return redirect(url_for('admin.admin_add'))
        else:
            admin = Admin(
                name=data['name'],
                password=int(data['pwd']),
                is_super=int(data['is_super'])
            )
            flash('添加成功！','ok')
            db.session.add(admin)
            db.session.commit()
            oplog = Oplog(
                admin_id=session["admin_id"],
                ip=request.remote_addr,
                reason="添加新管理员：%s" % data["name"]
            )
            db.session.add(oplog)
            db.session.commit()
            return redirect(url_for('admin.admin_add'))
    return render_template('admin/admin_add.html',form=form)


# 管理员列表
@admin.route('/admin/list/<int:page>/',methods=['GET'])
@admin_login
def admin_list(page=None):
    if page == None:
        page = 1
    admins = Admin.query.paginate(page,limits)
    return render_template('admin/admin_list.html',admins=admins)
