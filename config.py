import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    CSRF_ENABLED = True
    SECRET_KEY=os.environ.get('SECRIT_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    FLASK_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASK_MAIL_SENDER='Flasky Admin <gan@kingguo.top>'
    FLASK_ADMIN=os.environ.get('FLASK_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG=True
    MAIL_SERVER='smtp.kingguo.top'
    MAIL_PORT=25
    MAIL_USE_TLS=False
    MAIL_USERNAME="gan@kingguo.top"
    MAIL_PASSWORD="123456"
    SQLALCHEMY_DATABASE_URI='mysql://root:123456@localhost/blog'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/blog_t'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/blog_t'

config = {
'development': DevelopmentConfig,
'testing': TestingConfig,
'production': ProductionConfig,
'default': DevelopmentConfig
}