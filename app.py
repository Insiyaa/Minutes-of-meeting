from flask import Flask, request, render_template, url_for, flash
from gensim.summarization import summarize
from werkzeug import secure_filename
import os
import speech_recognition as sr
from pydub import AudioSegment
import dropbox
import re


UPLOAD_FOLDER = '/tmp/'
app = Flask(__name__)
app.secret_key = 'some secret key'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def convert(music_file):
    song = AudioSegment.from_mp3(music_file)
    song.export(UPLOAD_FOLDER + "temp.wav", format="wav")
    return sr.AudioFile(UPLOAD_FOLDER + "temp.wav")

def syncDB(text, filename):
    dbx = dropbox.Dropbox('5TvCqDE9xNAAAAAAAAACVk0U8XnCuncuYrDCfUu-_f6U5DGliCa_ErotxIC4rVIk')
    with open('temp.txt', 'w') as f:
        f.write(text)
    with open('temp.txt', 'rb') as f:
        dbx.files_upload(f.read(), '/' + filename + '.txt')


@app.route("/")
def index():
    msg = "Go on and Upload the voice recording of your meeting in MP3 or WAV formats and hit the Go button. Here you'll get a brief summary of the meet and some important dates and persons of the same. A more verbose summary would be uploaded to dropbox with the same name as of the audio uploaded. "
    flash(msg)
    return render_template('index.html')


@app.route('/results', methods=["GET", "POST"])
def results():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        if 'music' not in request.files:
            return redirect('/')
        music = request.files['music']

        if music.filename == '':
            return redirect('/')

        filename = secure_filename(music.filename)
        music.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        music_file = UPLOAD_FOLDER + filename
        
        if music_file[-3:] == 'mp3':
            audio_file = convert(music_file)
        else:
            audio_file = sr.AudioFile(music_file)

        r = sr.Recognizer()
        
        with audio_file as source:
            audio = r.record(source)

        text = r.recognize_ibm(audio, username="918493fe-7aab-48af-bc21-fd414d43a0fe", password="QSo5jRTeJdza")
        text = re.sub('(\s)%\w+', '', text, flags=re.IGNORECASE)
        # print(text)
        summary = summarize(text, ratio=0.20)
        syncDB(summary, filename[:-3])

        summary_print = summarize(text, ratio=0.15)



        from nltk.tag import StanfordNERTagger
        tagger = StanfordNERTagger('/home/insiyeah/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                                    '/home/insiyeah/stanford-ner/stanford-ner.jar', encoding='utf-8')
        tags = tagger.tag(summary)
        ner_dict = {"PERSON":[], "ORGANIZATION":[], "LOCATION":[]}

        for tag in tags:
            if tag[1] == "PERSON":
                ner_dict["PERSON"].append(tag[0])
            elif tag[1] == "ORGANIZATION":
                ner_dict["ORGANIZATION"].append(tag[0])
            elif tag[1] == "LOCATION":
                ner_dict["LOCATION"].append(tag[0])

        persons = ", ".join(ner_dict["PERSON"])
        locs = ", ".join(ner_dict["LOCATION"])
        orgs = ", ".join(ner_dict["ORGANIZATION"])

        flash_data = "The brief summary is" + summary_print + ".<br>" + "Some important tags are: <br>" + "Person involved: " + persons + "<br>"+ "Locations discussed: " + locs + "<br>" + "Organizations: " + orgs
        flash(flash_data)
        return render_template('index.html')
        

if __name__ == "__main__":
    app.run(debug=True)