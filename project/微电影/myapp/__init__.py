import os

from flask import Flask, render_template
from myapp.ext import init_ext
from myapp.sttings import config
from myapp.home.views import init_blue
from myapp.admin.views_admin import init_blue_admin


def create_app(evn_name=None):
    app = Flask(__name__)

    # 初始化，获取开发环境
    app.config.from_object(config.get(evn_name or 'default'))

    # 初始化蓝图
    init_blue(app)

    # 初始化ext.py
    init_ext(app)

    # 初始化admin蓝图
    init_blue_admin(app)

    # 404页面的返回
    @app.errorhandler(404)
    def handler404(error):
        return render_template('home/404.html'), 404


    return app