import os
from PIL import Image
from uuid import uuid4
from dotenv import load_dotenv
from elevenlabs import generate
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField
from genprompt import generate_prompt
from flask import Flask, render_template, request, redirect, url_for, abort

#load .env variables
load_dotenv()

# Save generated audio file
def save_audio(audio_bytes):
    filename = f"{uuid4()}.mp3"  # Generate unique filename
    filepath = os.path.join(app.config['AUDIO_FOLDER'], filename)
    with open(filepath, 'wb') as f:
        f.write(audio_bytes)
    return filename  # Return filename for reference in template

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Set upload folder
app.config['AUDIO_FOLDER'] = 'static/audio'  # Set upload folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size (16 MB)
app.config['SECRET_KEY'] = os.urandom(24)

class ImageForm(FlaskForm):
    photo = FileField('Upload Photo', validators=[FileRequired()])
    user_filename = StringField('Enter Name')

trusted_ips = os.environ.get('trusted_ips')


@app.before_request
def limit_remote_addr():
    if request.remote_addr not in trusted_ips:
        print(trusted_ips)
        abort(404)  # Not Found

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ImageForm()
    voice_id = 'Bviom6iVLYrnrbbh3bVY'
    if form.validate_on_submit():
        
        user_filename = form.user_filename.data.strip()
        if not user_filename.endswith('.'):
            orig_filename = form.photo.data.filename
        orig_ext = os.path.splitext(orig_filename)[1]  # Extract original extension
        user_filename += orig_ext

        if not user_filename:
            filename = secure_filename(form.photo.data.filename)
        else:
            filename = secure_filename(user_filename)
            
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter = 1
        while os.path.exists(filepath):
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{counter}{ext}"  # Use f-string for formatting
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1  # Increment counter after filename generation

        form.photo.data.save(filepath)
        image_url = url_for('static', filename='uploads/' + filename)
        img = Image.open(image_url.strip("/"))
        response = generate_prompt(img)
        response.resolve()
        gentext = response.text
        audio = generate(gentext, voice=voice_id)
        audio_filename = save_audio(audio)

        return redirect(url_for('results', gentext=gentext, audio_filename=audio_filename, image_url=image_url))  # Stay on index page
    return render_template('index.html', form=form)

@app.route('/results')
def results():
    gentext = request.args.get('gentext')
    audio_filename = request.args.get('audio_filename')
    image_url = request.args.get('image_url')
    return render_template('results.html', gentext=gentext, audio_filename=audio_filename, image_url=image_url)

if __name__ == "__main__":
    app.run()