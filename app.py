import json, pickle
import base64
import os, requests, socket
from time import sleep
from api.client import recognize_request
from api.qas import get_answer
from api.tts_client import TTSClient
from api.api_chinese_client import TTSClient
from flask import Flask, jsonify, render_template, request, send_file
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
            # turn data into what kaldi can read
            # make sure you have ffmpeg
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
@app.route("/Summary", methods=['GET','POST'])
def sum_handler():
    try:
        if request.method == 'POST':
            # get data from crawler
            # 必須要分成 body category level，category 只存在以下五種種類:"社會", "政治", "健康", "經濟", "運動"
            news_body = request.form.get("body")
            

            # establish news
            news = dict()
            news["body"] = news_body
            news["category"] = '社會'
            news["modifier_level"] = 'high'

            # call api
            token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzZXJ2aWNlX2lkIjoiMjciLCJuYmYiOjE2NjAxOTIyMTYsImV4cCI6MTgxNzg3MjIxNiwidmVyIjowLjEsImF1ZCI6IndtbWtzLmNzaWUuZWR1LnR3IiwidXNlcl9pZCI6IjEyMCIsImlzcyI6IkpXVCIsInN1YiI6IiIsInNjb3BlcyI6IjAiLCJpYXQiOjE2NjAxOTIyMTYsImlkIjo0NDN9.R1FXeE7Q2kgg8PzPnAX8r3cWjgWoIvfDwq-2pA6j6Lt8zoKjRrB2e0lmDlzhVhdk4BVUHtzbFm_ObS5cw1ndrhD-qcAT69hxaT3xfeJ7X7UPZvuUaW0kDJiyXP6Zs5sSic1x8T0SvkdHyge9Cv8LAl3EstoYVt22NdHeYzVfJmA"
            input_data = {"token": token, "news": news}
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("140.116.245.152", "1112"))
            client.sendall(pickle.dumps(input_data))
            serverMessage = pickle.loads(client.recv(4096))
            Sum = serverMessage["summary_ranking"]
            
        return ' '.join(Sum)
    except Exception as e:
        return jsonify({"error": str(e)})
# 得到新聞摘要或是內文之後把內容拿去合成
@app.route("/synthesis", methods=["GET","POST"])
def synthesis_handler():
    try:
        if request.method == "POST":
            # 進來的文字
            tts_text = request.form.get("tts_text")

            # 模組名稱
            model = 'M60'
            language = 'chinese'

            # 呼叫 api
            tts_client = TTSClient()
            tts_client.set_language(language=language, model=model)
            tts_client.askForService(tts_text)
            
        synt_path = './temp/renewed.wav'
        return send_file(synt_path, as_attachment=True)
    except Exception as e:
        return {'error': str(e)}
if __name__ == "__main__":
    app.run(debug=True)