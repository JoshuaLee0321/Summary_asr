import json, pickle
import base64
import os, requests, socket
from time import sleep
from api.client import recognize_request
from api.qas import get_answer
from api.tts_client import TTSClient
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import time
AudioPath = os.path.join(os.path.dirname(__file__),"static\\audio")

class VueFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(variable_end_string="%%",
                              variable_start_string="%%"))

app = VueFlask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# index
@app.route("/")
def index():
    return render_template("index.html")

# 把辨識的結果套進關鍵字檢索爬蟲
@app.route("/recognition", methods=['GET', 'POST'])
def req_handler():
    try:
        result = {"status": "false"}
        if request.method == 'POST':
            # get data from web request
            model_name = request.form.get("model")
            audio_blob = request.files['file']
            fname = "temp/temp.wav"
            with open(fname,'wb') as f:
                audio_blob.save(f)
            # 可以抓到了
            os.system("ffmpeg -loglevel error -y -i temp/temp.wav -ar 16000 -ac 1 temp/renewed.wav")
            time.sleep(0.5)
            with open(f"temp/renewed.wav", "rb") as _f:
                raw_data = _f.read()
            audio_data = base64.b64encode(raw_data)
            msg_dict = {"model_name":"MTK_ch", "source":'P',\
                        "token":'aaa', "audio_data":audio_data,}
            response = requests.post("http://140.116.245.149:2802/asr", data=msg_dict)
            msg = json.loads(response.text)
        return msg['words'][0].replace("<SPOKEN_NOISE>" ,'')
    except Exception as e:
        return jsonify({'error': str(e)})

# 把找出來的文章丟進 <陳偉／柏楊的api>
@app.route("/Summary", method=['GET','POST'])
def sum_handler():
    try:
        if request.method == 'POST':
            # get data from crawler
            news_body = request.form.get("body")
            news_category = request.form.get("category")
            news_modifier_level = request.form.get("level")

            # establish news
            news = dict()
            news["body"] = news_body
            news["category"] = news_category
            news["modifier_level"] = news_modifier_level

            # call api
            input_data = {"token": '', "news": news}
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("140.116.245.152", "1112"))
            client.sendall(pickle.dumps(input_data))
            serverMessage = pickle.loads(client.recv(4096))
        return serverMessage
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)