from datetime import datetime
from flask import render_template,session,redirect,url_for,abort,flash,request,make_response
from . import main
from .forms import PostForm,CommentForm
from .. import db
from ..models import Post,Student,Class,Follow
from ..models import User,Permission,Comment
from  flask_login import login_required,current_user
from ..decorators import admin_required,permission_required


@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if form.validate_on_submit() and \
            current_user.can(Permission.WRITE_ARTICLES):
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=5,error_out=False)
    posts = pagination.items
    return render_template('index.html',form=form,posts=posts,pagination=pagination)

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user,posts=posts)



@main.route('/edit/<int:id>',methods=["POST",'GET'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated. ')
        return redirect(url_for('.user',username=post.author.username))
    form.body.data = post.body
    return render_template('edit_post.html',form=form)



@main.route('/post/<int:id>',methods=['POST','GET'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post',id=post.id))
    page = request.args.get('page',1,type=int)
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,per_page=10,
        error_out=False)
    comments = pagination.items
    return render_template('post.html',
                           posts=[post],form=form,
                           comments=comments,pagination=pagination)



@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('you are already following this user.')
        return redirect(url_for('.user',username=username))
    current_user.follow(user)
    flash('you are now following %s' %username)
    return redirect(url_for('.user',username=username))
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('you are not following this user.')
        return redirect(url_for('.user',username=username))
    current_user.unfollow(user)
    flash('you are not following %s anymore'% username)
    return redirect(url_for('.user',username=username))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(page,per_page=5,error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp}
               for item in pagination.items]
    # return "%s" %follows[0].user.username
    return render_template('followers.html',
                           user=user,
                           title='Followers of',
                           endpoint='.followers',
                           pagination=pagination,
                           follow=follows)
@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(page,per_page=5,error_out=False)
    follows = [{'user':item.followed,'timestamp':item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',
                           user=user,
                           title='Followed by',
                           endpoint='.followed_by',
                           pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp=make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page,per_page=10,
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html',comments=comments,pagination=pagination,page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment=Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))



###############################
@main.route('/test_pwd')
def test_pwd():
    Post.generate_fake(100)

@main.route('/admin')
@admin_required
@login_required
def for_admin_only():
    return 'For administrators!'

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return 'For comment Moderators!'

@main.route('/test_permission')
def test_permission():
    return '%s' %current_user.role.permissions



@main.route('/test_add_student')
def add_student():
    s=Student(name='peng')
    try:
        db.session.add(s)
        db.session.commit()
        return "success!"
    except:
        return "some errors"

@main.route('/test_add_class')
def add_class():
    c=Class(name='japan')
    try:
        db.session.add(c)
        db.session.commit()
        return "success!"
    except:
        return "some errors"
@main.route('/test_reg')
def add_reg():
    s=Student.query.filter_by(name='gan').first()
    c=Class.query.filter_by(name='english').first()
    try:
        s.classes.append(c)
        db.session.add(s)
        db.session.commit()
        return "success!"
    except:
        return "some errors"

@main.route('/test_see')
def add_see():
    s=Student.query.filter_by(name='gan').first()
    c=Class.query.filter_by(name='japan').first()
    try:
        s.classes.remove(c)
        db.session.add(s)
        db.session.commit()
        return "student :%s remove %s"%(s.name,c.name)
    except:
        return "some error!"
@main.route('/test/123')
def test_123():
    return render_template('test_123.html')

@main.route('/test_query')
def test_query():
    #posts=db.session.query(Post).select_from(Follow).filter_by(follower_id=current_user.id).join(Post,Follow.followed_id==Post.author_id).all()
    posts=Post.query.join(Follow,Follow.followed_id==Post.author_id).filter(Follow.follower_id==current_user.id)
    return render_template('list.html',posts=posts)
@main.route('/test_make_response')
def test_make_response():
    resp = make_response('hellow world!!')
    resp.set_cookie('myname','gan-jiangpeng',max_age=3600)
    return resp