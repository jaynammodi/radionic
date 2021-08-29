from flask.templating import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_debugtoolbar import DebugToolbarExtension
from wtforms.validators import DataRequired
from flask import Flask, send_file
import os
import numpy
from pydub import AudioSegment
from pathlib import Path
from scipy.io.wavfile import write
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime, date
from moviepy.video import VideoClip
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
    frequency1 = DecimalField("Frequency1", validators=[DataRequired()], places=2)
    frequency2 = DecimalField("Frequency2", places=2)
    frequency3 = DecimalField("Frequency3", places=2)
    frequency4 = DecimalField("Frequency4", places=2)
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

def generateAudio(frequency_list, duration, outfile):
    outlist = []
    sample_rate = 44100
    count = 0
    for freq in frequency_list:
        frequency = int(freq)
        print(" > Genrating Frequency : ", frequency)
        samples = ""
        samples = (numpy.sin(2 * numpy.pi * numpy.arange(sample_rate * duration) * frequency / sample_rate)).astype(numpy.float32)
        write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", outfile + "_" + str(count) + ".wav"), sample_rate, samples)
        outlist.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", outfile + "_" + str(count) + ".wav"))
        count += 1
        print(outlist)

    sound = AudioSegment.from_file(file=outlist[0], format="wav")
    for x in range(1, len(outlist)):
        sound2 = AudioSegment.from_file(file=outlist[x], format="wav")
        sound = sound.overlay(sound2, position=0)

    sound.export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", outfile + ".mp3"), format="mp3")




def generateVideo(name, photo, rr, wish, freq, len):
    processPhoto(photo, [name, wish, "RR Code - " + rr, " - Radionic Tone Healing"])
    image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edited")
    filename = Path(photo).stem
    duration = len * 60
    generateAudio(freq, duration, filename)

    audioclip = AudioFileClip(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", filename + ".mp3"))

    clip = ImageClip(os.path.join(image_folder, photo)).set_duration(audioclip.duration)
    clip = clip.set_audio(audioclip)
    clip.write_videofile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", filename + ".mp4"), fps=1)
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
        freq_list = [form.frequency1.data, form.frequency2.data, form.frequency3.data, form.frequency4.data]

        video_op = generateVideo(form.name.data, photoname, form.rr_code.data, form.wish.data, freq_list, form.duration.data)

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