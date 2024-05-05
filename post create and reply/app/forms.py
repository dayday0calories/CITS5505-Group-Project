from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    # Form for creating a new post
    title = StringField('Title', validators=[DataRequired()])  # Title field must not be empty
    content = TextAreaField('Content', validators=[DataRequired()])  # Content field must not be empty
    tags = StringField('Tags (comma-separated)')  # Optional field for tags, input as comma-separated values
    submit = SubmitField('Post')  # Submit button for the form

class ReplyForm(FlaskForm):
    # Form for replying to an existing post
    content = TextAreaField('Reply', validators=[DataRequired()])  # Content field for the reply, must not be empty
    submit = SubmitField('Reply')  # Submit button for the form


