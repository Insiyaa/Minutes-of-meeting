from flask import Flask, request, render_template, url_for, flash
from gensim.summarization import summarize
from werkzeug import secure_filename
import os
import speech_recognition as sr
from pydub import AudioSegment
import dropbox
import re
import datetime
import sqlite3


UPLOAD_FOLDER = '/tmp/'
app = Flask(__name__)
app.secret_key = 'some secret key'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def update_db(title, agenda, date_added, link="https://www.dropbox.com/s/dimtj312vrz6nrl/audio1..txt?dl=0"):
    with sqlite3.connect("app.db") as db:
        db.execute(f"INSERT INTO data (title, agenda, date, link) VALUES ('{title}', '{agenda}', '{date_added}', '{link}')")


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
    msg = "Go on and <i>upload</i> the voice recording of your meeting in MP3 format and hit the Go button. <br><br> Here you'll get a brief summary of the meet mentioning the agenda and attendees.<br><br> A copy of summary would be uploaded to dropbox with the same name as of the audio uploaded. "
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

        title = request.form.get('title')

        if music_file[-3:] == 'mp3':
            audio_file = convert(music_file)
        else:
            audio_file = sr.AudioFile(music_file)

        r = sr.Recognizer()
        
        with audio_file as source:
            audio = r.record(source)
        text = r.recognize_ibm(audio, username="918493fe-7aab-48af-bc21-fd414d43a0fe", password="QSo5jRTeJdza")
        # text = "hello thank you for joining the senior management team of experts and basically run clothing manufacturer I'm Smith Mason chief executive officer of now like to invite my colleagues to introduce themselves \nhi I'm Alex unlimited information \nhi I'm Rachel and I work in administration \nI am gonna nine had a fine I'm not the head of research \nso the first item on the agenda is something that is useful to us as regarding Staal working from home but he can you give us a little bit of a background on some okay thanks and bye I've been talking to the team %HESITATION we had a stuff meeting last week announced they feel very strongly that they would really appreciate a field a section soak a view on stuff working from high as United they have slightly different jobs to some of my colleagues in that dialogue rising and not necessarily on serving the funds that they find it extremely difficult to concentrate in an office is busy that was on they'd like to feel that they are working from home was endorsed by some kind of policy view rather than something that was a base out whole Catherine's made to feel guilty about and something else to bring this issue to the senior management team lead off we've never objected to stop working from home the full if from time to time and is of your team wanted what I'm not that's fine I mean why do you feel that we need to put a policy in place regarding this I mean what time we just continue as we are facing a single we can \nBucks I guess they feel that can be some nations I'm is some other colleagues may feel differently %HESITATION down there are probably some procedural issues about that practical things K. \nwhat a real feel this what they think the \nwell to me this is just another pine sky schemas group of Ford has anyone done any weapon costing all we can to providing computers for them there will be some insurance applications to I just don't think this is been very walkable town yeah costumes of certainly concerned anyone else \nAlex how do you feel about this \neither see costing is that much of an issue given the most of our members have computers I'm ready so that would be one less thing to worry about I think it's a very good idea for all members will some of our members to work from home be tiki ones with families as they would be able to have more input with them during the whole day period also fail they would be less stressed if I could do was hold something report like a big project from hi thank you for that \nwhat is definitely an endorsement of X. which I actually work administration Conover because the pool so nineteen to work from home \n%HESITATION I we have children to use that would be fed to one section of the team and \nso I don't think it's a good idea to unless you want to present an image of a unique sinks and members of stuff \nlike I say it's going to be difficult to make this the across the board \nJohn %HESITATION regarding the insurance sign go would we be liable if %HESITATION invoices standin injure me yes that all of a sudden the health and safety implications here and I think we should look further into this before announces show okay well obviously we have relevant concerns on all sides Matthew had the feedback of what do you think \nthe only additional thing I would say is that it is a competitive market town that %HESITATION and flexible working is increasingly something that happens in a kind of field and family friendly work means today do you think it's something we should look at that may be reasons as well I need to hear as to why it's not going to work but I do think it's something we should continue to explore because I think the team would feel very fed up with it was just built on the head of this point \nwe are certainly have some very strong arguments in favor of increasing flexibility accommodating working parents islands were aware of how busy the office can get making a very difficult environment to what can \nwe were called into the phones ring all the time and it's something that John I've been trying to address Sir yes there was suddenly positives except for when it comes to regions team where the %HESITATION proposal isn't so attractive and of course cost is a major concern I mean John I presented you with the financial statements for this year and we just need to be realistic about what we can change \nserver moving forward \ncan I also use of with John hops %HESITATION lookups are researching this proposal father look at other reservations I have taken this practice on board the Cole soon though %HESITATION in regards to insurance and then present to us with that information next meeting \nyes bus fine job of the story yes that's fine okay well our next meeting is scheduled for four nights and you will give a joint presentation of what will and get together in Saturday so we talked for the next meeting escaped and doctor by accident well if that's all nice and move on to the next one which is the strategic plan not take everyone's with papers "
        text = re.sub('(\s)%\w+', '', text, flags=re.IGNORECASE)

        # Handling corner cases
        if "Staal" in text:
            text = text.replace("Staal", 'staff')

        # STANFORD NER TAGGER
        from nltk.tag import StanfordNERTagger
        tagger = StanfordNERTagger('/home/insiyeah/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                                    '/home/insiyeah/stanford-ner/stanford-ner.jar', encoding='utf-8')
        tags = tagger.tag(text.split())
        ner_dict = {"PERSON":[], "ORGANIZATION":[], "LOCATION":[]}

        for tag in tags:
            if tag[1] == "PERSON":
                ner_dict["PERSON"].append(tag[0])
            elif tag[1] == "ORGANIZATION":
                ner_dict["ORGANIZATION"].append(tag[0])
            elif tag[1] == "LOCATION":
                ner_dict["LOCATION"].append(tag[0])

        persons = list(set(ner_dict["PERSON"]))
        if "I've" in persons:
            persons.remove("I've")
        orgs = list(set(ner_dict["ORGANIZATION"]))
        if "I'm" in orgs:
            orgs.remove("I'm")

        common_words = ['okay', 'good', 'listen', 'can I get your attention', 'may I get your attention', 'oh okay', 'can I draw your attention', 'hello', 'good morning', 'thank you', 'bye', 'please let me know', 'sure thanks', 'thank you very much', 'very much', 'for being here', 'late']

        for word in common_words:
            if word in text:
                text = text.replace(word, '')
        

        persons = ", ".join(persons)
        locs = ", ".join(list(set(ner_dict["LOCATION"])))
        orgs = ", ".join(orgs)

        aloc = text.find('agenda')
        agenda = text[aloc+10:aloc+77]

        actn = text.find('need')
        actn = text[actn:1380]
        dtime = str(datetime.datetime.now().date())
        flash_data = "<b>Title: </b>" + title + ".<br> <i>Date: " + dtime + "</i>" + "<hr><br><b> The Agenda is: </b>" + str(agenda) + "<br><b>Attendees</b> " + str(persons)+ "<br><b>Actions Required: </b>" + str(actn) + ".<br>" + "<br><i>Some important tags are:</i> " + "<br>"+ "<b>Locations discussed:</b> " + str(locs) + "<br>" + "<b>Organizations:</b> " + str(orgs)

        flash(flash_data)

        # More verbose summary
        # Gensim summary
        summary = summarize(text, ratio=0.1)
        sync_data = "Title: " + title + "\nDate:" + dtime + "\nThe Agenda is:\n" + agenda + "\nAttendees: " + persons + "\nActions Required: \n" + actn + ".\n" + "Some important tags are: \n" + "\n"+ "Locations discussed: " + locs + "\n" + "Organizations: " + orgs + "\n.Date: " + dtime + "." + "\n\nVerbose Summary: \n" + summary


        syncDB(sync_data, filename[:-3])
        update_db(title, agenda, dtime)
        return render_template('index.html')

@app.route('/history', methods=["GET", "POST"])
def history():
    with sqlite3.connect("app.db") as db:
        result = db.execute(f"SELECT * FROM data")
    
    data = []
    for row in result:
        data.append(row)
    return render_template('history.html', data=data)
       

if __name__ == "__main__":
    app.run(debug=True)