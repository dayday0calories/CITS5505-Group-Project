from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required, login_user
from . import user
from app.models.models import Post, Reply, User, db
import os
from werkzeug.utils import secure_filename
from .forms import UpdatePictureForm, ChangePasswordForm
from werkzeug.security import generate_password_hash


@user.route('/user/profile/<int:user_id>',methods=['GET', 'POST'])
@login_required
def user_profile(user_id, tab='posts'):
    print("Current tab:", tab)
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all() if tab == 'posts' else None
    replies = Reply.query.filter_by(user_id=user_id).all() 
    print("Replies: ", replies)
    return render_template('user/user_profile.html', user=user, posts=posts, replies=replies, active_tab=tab)


@user.route('/user_settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    picture_form = UpdatePictureForm()
    password_form = ChangePasswordForm()

    if picture_form.validate_on_submit() and 'submit_picture' in request.form:
        if picture_form.picture.data:
            filename = secure_filename(picture_form.picture.data.filename)
            filepath = os.path.join(current_app.root_path, 'static/uploads', filename)
            picture_form.picture.data.save(filepath)
            current_user.profile_image_url = url_for('static', filename='uploads/' + filename)
            db.session.commit()
            flash('Profile picture updated successfully.')
        return redirect(url_for('user.user_settings'))

    if password_form.validate_on_submit() and 'submit_password' in request.form:
        current_user.password = generate_password_hash(password_form.password.data)
        db.session.commit()
        flash('Password updated successfully.')
        return redirect(url_for('user.user_settings'))

    return render_template('user/user_settings.html', picture_form=picture_form, password_form=password_form, user=current_user)






