import os



# 注册上传文件路径
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/upload')
UPLOAD_VIDEO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/upload/video/')
UPLOAD_LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/upload/logo/')
UPLOAD_LOGO_USER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/upload/logo/users/')
# 设置环境
# 连接数据库拼接
def database_uri(DATABASE):
    db = DATABASE.get('DB') or 'mysql'
    driver = DATABASE.get('DRIVER') or 'pymysql'
    username = DATABASE.get('USERNAME') or 'root'
    password = DATABASE.get('PASSWORD') or '123456'
    host = DATABASE.get('HOST') or '127.0.0.1'
    port = DATABASE.get('PORT') or '3306'
    dbname = DATABASE.get('DBNAME') or 'microfilm'
    return '{}+{}://{}:{}@{}:{}/{}'.format(db,driver,username,password,host,port,dbname)

# 配置基类
class BaseConfig():
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'ASDFGHJKLQWERTYUI35465jhkjOPZXCVBNM'
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


# 开发环境
class DevelopConfig(BaseConfig):

    DEBUG = True
    DATABASE = {
        'DB':'mysql',
        'DRIVER':'pymysql',
        'USERNAME':'root',
        'PASSWORD':'123456',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'DBNAME':'microfilm'
    }
    SQLALCHEMY_DATABASE_URI = database_uri(DATABASE)


# 测试环境
class TestingConfig(BaseConfig):
    TESTING = True
    DATABASE = {
        'DB':'mysql',
        'DRIVER':'pymysql',
        'USERNAME':'root',
        'PASSWORD':'123456',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'DBNAME':'microfilm'
    }
    SQLALCHEMY_DATABASE_URI = database_uri(DATABASE)

# 演示环境
class StagingConfig(BaseConfig):
    DATABASE = {
        'DB':'mysql',
        'DRIVER':'pymysql',
        'USERNAME':'root',
        'PASSWORD':'123456',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'DBNAME':'microfilm'
    }
    SQLALCHEMY_DATABASE_URI = database_uri(DATABASE)

# 线上环境
class ProductConfig(BaseConfig):
    DATABASE = {
        'DB':'mysql',
        'DRIVER':'pymysql',
        'USERNAME':'root',
        'PASSWORD':'123456',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'DBNAME':'microfilm'
    }
    SQLALCHEMY_DATABASE_URI = database_uri(DATABASE)


config = {
    'default':DevelopConfig,
    'develop':DevelopConfig,
    'testing':TestingConfig,
    'Staging':StagingConfig,
    'product':ProductConfig
}