# 导入表单基类，falsk-wtf使用秘钥生成加密令牌，用加密令牌验证请求中表单数据的真伪
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo


# 管理员登录表单
class LoginForm(FlaskForm):
    account = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],                               # 验证器
        description="账号",              # 描述符
        render_kw={  # 附加选项
            "class": "form-control",
            "placeholder": "请输入账号！",
            "required": "required"  # 添加强制属性，H5会在前端验证
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
            "required": "required"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )


# 标签表单，添加标签
class TagForm(FlaskForm):
    name = StringField(
        label='标签名称',
        validators=[
            DataRequired("请输入标签！")
        ],
        description="标签",
        render_kw={
            "class":"form-control",
            "placeholder":"请输入标签名称！",
        }
    )
    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary"
        }
    )


# 预告管理表单
class PreviewForm(FlaskForm):
    title = StringField(
        label = '预告标题',
        validators = [
            DataRequired('请输入标题！')
        ],
        description='预告标题',
        render_kw={

            "class":"form-control",
            "id":"input_title",
            "placeholder":"请输入预告标题！"
        }

    )
    logo = FileField(
        label="预告封面",
        validators=[
            DataRequired("请上传预告封面！")
        ],
        description="预告封面",
        render_kw={
            "id": "input_logo"
        }
    )
    submit = SubmitField(
        '提交',
        render_kw={
            "class": "btn btn-primary"
        }
    )


# 修改密码表单
class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label = '旧密码',
        validators = [
            DataRequired('请输入旧密码！')
        ],
        description='旧密码',
        render_kw={
            "class":"form-control",
            "id":"input_pwd",
            "placeholder":"请输入旧密码！"
        }

    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码！")
        ],
        description="新密码",
        render_kw={
            "class":"form-control",
            "id":"input_newpwd",
            "placeholder":"请输入新密码！"
        }
    )
    submit = SubmitField(
        '修改',
        render_kw={
                "class": "btn btn-primary"
        }
    )


# 添加权限表单
class AuthForm(FlaskForm):
    name = StringField(
        label='权限名称',
        validators=[
            DataRequired("请输入权限名称！")
        ],
        description="权限名称",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入权限名称！"
        }
    )

    url = StringField(
        label='权限地址',
        validators=[
            DataRequired("请输入权限地址！")
        ],
        description="权限地址",
        render_kw={
            "class": "form-control",
            "id": "input_url",
            "placeholder": "请输入权限地址！"
        }
    )

    submit = SubmitField(
        '添加',
        render_kw={
            "class": "btn btn-primary"
        }
    )

# 添加管理员表单
class AdminForm(FlaskForm):
    name = StringField(
        label='管理员名称',
        validators=[
            DataRequired("请输入管理员名称！")
        ],
        description="管理员名称",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入管理员名称！"
        }
    )

    pwd = PasswordField(
        label='管理员密码',
        validators=[
            DataRequired("请输入管理员密码！")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "id": "input_pwd",
            "placeholder": "请输入管理员密码！"
        }
    )

    re_pwd = PasswordField(
        label='管理员重复密码',
        validators=[
            DataRequired("请再次输入管理员密码！"),
            EqualTo('pwd', message="两次密码输入不一致！")
        ],
        description="管理员重复密码",
        render_kw={
            "class": "form-control",
            "id": "input_pwd",
            "placeholder": "请再次输入管理员密码！"
        }
    )
    is_super = SelectField(
        label='管理员类型',
        validators=[
            DataRequired("请输入管理员管理员类型！")
        ],
        coerce=int,
        choices=[(0, "未选择"), (1, "超级管理员"), (2, "普通管理员")],
        description="管理员类型",
        render_kw={
            "class": "form-control",
            "id": "input_super",
            "placeholder": "请输入管理员管理员类型！"
        }
    )
    submit = SubmitField(
        '提交',
        render_kw={
            "class": "btn btn-primary"
        }
    )