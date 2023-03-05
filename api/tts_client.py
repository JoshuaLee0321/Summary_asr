# !/usr/bin/env python
# _*_coding:utf-8_*_

# 給任何使用這支程式的人：這支程式是國台語合成的 API 的 client 端。
# 具體上會發送最下方變數 data 給伺服器，並接收一個回傳的 wav 檔，output.wav

# 客戶端 ，用來呼叫 service_Server.py

import argparse
import socket
import struct


class TTSClient:
    def __init__(self):
        self.host = "140.116.245.157"

    # Don't touch
    def askForService(self, data: str):
        '''
        Ask TTS server.
        Params:
            data    :(str) Text to be synthesized. If language is chinese, it must be chinese.If language is taiwanese, it can be chinese or tai-luo.
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if not len(data):
                raise ValueError("Length of data must be bigger than zero")

            sock.connect((self.host, self.__port))
            msg = bytes(self.__token + "@@@" + data +
                        '@@@' + self.__model, "utf-8")
            msg = struct.pack(">I", len(msg)) + msg
            sock.sendall(msg)

            with open('output.wav', 'wb') as f:
                while True:
                    l = sock.recv(8192)
                    if not l:
                        break
                    f.write(l)
            # print("File received complete")
        finally:
            sock.close()

    def set_language(self, language: str, gender: str):
        '''
        Set port and token by language.
        Set model by gender.
        Params:
            language    :(str) chinese or taiwanese.
            gender      :(str) male or female. We don't have female in chinese.
        '''
        if language == 'chinese':
            self.__port = 10015
            self.__token = "2022@course@tts@chinese"
            self.__model = 'M60'

        elif language == 'taiwanese' or language == 'CCH_T':
            self.__port = 10012
            self.__token = "2022@course@tts@taiwanese"

            if gender == 'male':
                self.__model = 'M12_5'
            elif gender == 'female':
                self.__model = 'F14'
            else:
                raise ValueError("'gender' param must be male or female")

        else:
            raise ValueError("'language' param must be taiwanese or chinese")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', default='taiwanese', help='Language to be synthesized, chinese or taiwanese')
    parser.add_argument('--gender', default='male', help='Gender to be synthesized, male or female')
    parser.add_argument('--data', default='phái-sè，gua2 thiann1 be7 tshing1-tsho2 li2 kong2 siann2-mih4', help='Text to be synthesized')
    args = parser.parse_args()
    tts_client = TTSClient()
    tts_client.set_language(args.language, args.gender)
    tts_client.askForService(args.data)
