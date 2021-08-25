from flask.helpers import flash
from flask.templating import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_debugtoolbar import DebugToolbarExtension
from wtforms.validators import DataRequired
from flask import Flask, send_file
import os
import numpy
from pathlib import Path
from scipy.io.wavfile import write
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime, date
import moviepy.video.io.ImageSequenceClip
from moviepy.editor import *

global dict_data_store

def clearMedia():
        dirs = ["audio", "output", "uploads"]
        for dir in dirs:
            for f in os.listdir(dir):
                if("nodel" not in f):
                    os.remove(os.path.join(dir, f))

SECRET_KEY = os.urandom(32)

class appForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    rr_code = StringField("RR Code", validators=[DataRequired()])
    wish = StringField("Wish", validators=[DataRequired()])
    photo = FileField("Photo", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    frequency = DecimalField("Frequency", validators=[DataRequired()], places=2)
    duration = IntegerField("Duration", validators=[DataRequired()])

def processPhoto(photo, msgs):
    old_im = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", photo))
    old_size = old_im.size
    aspect_ratio = old_size[1]/old_size[0]
    old_im = old_im.resize((1080, int(1080*aspect_ratio)), Image.NEAREST)
    old_size = old_im.size
    new_size = (1080, 1920)
    new_im = Image.new("RGB", new_size)   ## luckily, this is already black!
    new_im.paste(old_im, ((new_size[0]-old_size[0])//2, (new_size[1]-old_size[1])//2))

    textfont = ImageFont.truetype('Calibri.ttf', 50)
    W = 1080
    H = 1920
    draw = ImageDraw.Draw(new_im)

    msg = ""
    for x in msgs:
        msg += x + "\n\n"

    draw.text((W/2, H), msg, align="center", font=textfont, anchor="md")
    new_im.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "edited", photo))



def generateVideo(name, photo, rr, wish, freq, len):
    processPhoto(photo, [name, wish, "RR Code - " + rr, " - Radionic Tone Healing"])
    image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edited")
    fps = 1/60
    filename = Path(photo).stem
    sample_rate = 44100
    duration = len * 60
    frequency = int(freq)
    imgseq = []
    for x in range(len):
        imgseq.append(os.path.join(image_folder, photo))

    samples = (numpy.sin(2 * numpy.pi * numpy.arange(sample_rate * duration) * frequency / sample_rate)).astype(numpy.float32)
    write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", filename + ".wav"), sample_rate, samples)

    audioclip = AudioFileClip(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", filename + ".wav"))

    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(imgseq, fps=fps)
    clip = clip.set_audio(audioclip)
    clip.write_videofile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", filename + ".mp4"))
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", filename + ".mp4")



app = Flask("Radionic Tone Healing Script", template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))
app.config['SECRET_KEY'] = SECRET_KEY
app.debug = False
toolbar = DebugToolbarExtension(app)

@app.route('/', methods = ['GET', 'POST'])
def index():
    # clearMedia()
    global dict_data_store
    form = appForm()
    if form.validate_on_submit():
        upload_dir = os.path.join(os.path.dirname(app.instance_path), 'uploads')

        p = form.photo.data
        photoname = datetime.now().strftime("%d%m%Y%H%M%S") + Path(p.filename).suffix
        p.save(os.path.join(upload_dir, photoname))
        dict_data_store = [form.name.data, photoname, form.rr_code.data, form.wish.data, form.frequency.data, form.duration.data]

        video_op = generateVideo(form.name.data, photoname, form.rr_code.data, form.wish.data, form.frequency.data, form.duration.data)

        return send_file(video_op, as_attachment=True)

    return render_template('index.html', form=form)

@app.route('/uploaded', methods=['GET'])
def postUpload():
    global dict_data_store

    return render_template

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)