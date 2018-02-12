from flask import request,jsonify,url_for,g,flash,redirect,render_template,session
from . import api
from ..models import Post,Permission,User
from .authentication import auth
#import json
from .decorators import permission_required
from .. import db
from .errors import forbidden
from flask_login import current_user
from .forms import LoginForm


@api.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            return redirect(url_for('main.index'))
        if user.verify_password(form.password.data):
            return 'login success!'
    return render_template('login_api.html',form=form)

@api.route('/posts')
@auth.login_required
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts':[post.to_json() for post in posts]})



@api.route('/posts/',methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()),201,\
                   {'Location': url_for('api.get_post',id=post.id,_external=True)}

@api.route('/posts/<int:id>')
#@permission_required(Permission.WRITE_ARTICLES)
def get_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
        not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    #post.body = request.json.get('body',post.body)
    #db.session.add(post)
    return jsonify(post.to_json())

@api.route('/users/<int:id>')
def get_user(id):
    pass
@api.route('/post_comments/<int:id>')
def get_post_comments(id):
    pass


#@api.route('/test/')
@api.route('/get_pass')
@auth.login_required
def get_pass():
    email='gan@kingguo.top'
    user = User.query.filter_by(email=email).first()
    return jsonify({'username':user.username})



@api.route('/test')
def test():
    #return "%s" %request.headers['Authorization'].split(None,1)
    return render_template('test.html')
    return '12345'
    return g.current_user.username