import json
import pickle
import base64
import os
import requests
import socket
from time import sleep
from api.client import recognize_request
from api.qas import get_answer
from api.tts_client import TTSClient
from api.api_chinese_client import TTSClient
from flask import Flask, jsonify, render_template, request, send_file, redirect, url_for
from flask_cors import CORS
import time
from crawler import search_news
import io

AudioPath = os.path.join(os.path.dirname(__file__), "static\\audio")


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
        if request.method == 'POST':
            # get data from web request
            model_name = request.form.get("model")
            audio_blob = request.files['file']
            fname = "temp/temp.wav"
            with open(fname, 'wb') as f:
                audio_blob.save(f)
            # turn data into what kaldi can read
            # make sure you have ffmpeg
            os.system(
                "ffmpeg -loglevel error -y -i temp/temp.wav -ar 16000 -ac 1 temp/renewed.wav")
            time.sleep(0.5)
            with open(f"temp/renewed.wav", "rb") as _f:
                raw_data = _f.read()
            audio_data = base64.b64encode(raw_data)
            msg_dict = {"model": "", "lang": "mandarin",
                        "token": 'aaa', "audio_data": audio_data,
                        "audio_name": "Temporary"}

            response = requests.post(
                "http://140.116.245.157:9500/asr", data=msg_dict)
            news_body = search_news(response.json()['hyps']['result'])
            # get data from crawler
            # 必須要分成 body category level，category 只存在以下五種種類:"社會", "政治", "健康", "經濟", "運動"
            # news_body = request.form.get("body")
            HOST = "140.116.245.152"
            PORT = 1112
            news = dict()

            tmp = news_body["body"]
            news_body_res = news_body['body']
            tmp.replace("\n", "").replace("\n\n", "")

            if len(tmp) > 300:
                tmp = tmp[0:300]

            news["body"] = tmp
            news["category"] = "經濟"
            news["modifier_level"] = "high"

            # call api
            token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzZXJ2aWNlX2lkIjoiMjciLCJuYmYiOjE2NjAxOTIyMTYsImV4cCI6MTgxNzg3MjIxNiwidmVyIjowLjEsImF1ZCI6IndtbWtzLmNzaWUuZWR1LnR3IiwidXNlcl9pZCI6IjEyMCIsImlzcyI6IkpXVCIsInN1YiI6IiIsInNjb3BlcyI6IjAiLCJpYXQiOjE2NjAxOTIyMTYsImlkIjo0NDN9.R1FXeE7Q2kgg8PzPnAX8r3cWjgWoIvfDwq-2pA6j6Lt8zoKjRrB2e0lmDlzhVhdk4BVUHtzbFm_ObS5cw1ndrhD-qcAT69hxaT3xfeJ7X7UPZvuUaW0kDJiyXP6Zs5sSic1x8T0SvkdHyge9Cv8LAl3EstoYVt22NdHeYzVfJmA"
            input_data = {"token": token, "news": news}
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
            client.sendall(pickle.dumps(input_data))
            serverMessage = pickle.loads(client.recv(4096))
            Sum = serverMessage["summary_ranking"]
            client.close()
            total_string = "得到的摘要為，"
            for each in Sum:
                total_string += each
                total_string += '，'

            # 模組名稱
            model = 'M60'
            language = 'chinese'

            # 呼叫 api
            tts_client = TTSClient()
            tts_client.set_language(language=language, model=model)
            tts_client.askForService(total_string)

            return jsonify({'message': "success", "Summary": Sum, "summaryText": total_string[:300], "news_body": news_body_res})

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/play_audio')
def play_audio():
    # 读取本地的output.wav文件
    with open('./output.wav', 'rb') as f:
        audio_data = f.read()

    # 将音频数据发送到客户端
    return send_file(
        './output.wav',
        mimetype='audio/wav',
        as_attachment=False,
        attachment_filename='output.wav'
    )


@app.route('/send_text', methods=['POST'])
def send_text():
    text = request.form['text']
    try:
        if request.method == 'POST':
            # get data from web request

            news_body = search_news(text)
            # get data from crawler
            # 必須要分成 body category level，category 只存在以下五種種類:"社會", "政治", "健康", "經濟", "運動"
            # news_body = request.form.get("body")
            HOST = "140.116.245.152"
            PORT = 1112
            news = dict()

            tmp = news_body["body"]
            tmp.replace("\n", "").replace("\n\n", "")
            news_body_res = tmp
            if len(tmp) > 300:
                tmp = tmp[0:300]

            news["body"] = tmp
            news["category"] = "經濟"
            news["modifier_level"] = "high"

            # call api
            token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzZXJ2aWNlX2lkIjoiMjciLCJuYmYiOjE2NjAxOTIyMTYsImV4cCI6MTgxNzg3MjIxNiwidmVyIjowLjEsImF1ZCI6IndtbWtzLmNzaWUuZWR1LnR3IiwidXNlcl9pZCI6IjEyMCIsImlzcyI6IkpXVCIsInN1YiI6IiIsInNjb3BlcyI6IjAiLCJpYXQiOjE2NjAxOTIyMTYsImlkIjo0NDN9.R1FXeE7Q2kgg8PzPnAX8r3cWjgWoIvfDwq-2pA6j6Lt8zoKjRrB2e0lmDlzhVhdk4BVUHtzbFm_ObS5cw1ndrhD-qcAT69hxaT3xfeJ7X7UPZvuUaW0kDJiyXP6Zs5sSic1x8T0SvkdHyge9Cv8LAl3EstoYVt22NdHeYzVfJmA"
            input_data = {"token": token, "news": news}
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
            client.sendall(pickle.dumps(input_data))
            serverMessage = pickle.loads(client.recv(4096))
            Sum = serverMessage["summary_ranking"]
            client.close()
            total_string = "得到的摘要為，"
            total_string += '，'.join(Sum)

            # 模組名稱
            model = 'M60'
            language = 'chinese'

            # 呼叫 api
            tts_client = TTSClient()
            tts_client.set_language(language=language, model=model)
            tts_client.askForService(total_string)

            return jsonify({'message': "success", "Summary": Sum, "summaryText": total_string[:300], "news_body": news_body_res})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == "__main__":
    app.run(debug=True)
