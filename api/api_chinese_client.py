# !/usr/bin/env python
# _*_coding:utf-8_*_

# 給任何使用這支程式的人：這支程式是國台語和客語合成的API的client端。具體上會發送最下方變數text
# 給伺服器，並接收一個回傳的wav檔，output.wav

#客戶端 ，用來呼叫service_Server.py
import socket
import struct
import argparse

class TTSClient:
    def __init__(self):
        self.host = "140.116.245.157"

    ### Don't touch
    def askForService(self, text:str):
        '''
        Ask TTS server.
        Params:
            text    :(str) Text to be synthesized. If language is chinese, it must be chinese.If language is taiwanese or hakka, it can be chinese or tai-luo.
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if not len(text):
                raise  ValueError ( "Length of text must be bigger than zero")
            
            sock.connect((self.host, self.__port))
            msg = bytes(self.__token + "@@@"+ text +'@@@'+ self.__model+'@@@'+ self.language, "utf-8")
            msg = struct.pack(">I", len(msg)) + msg
            sock.sendall(msg)

            if 'pinyin' in self.language:
                l = sock.recv(8192)
                l = l.decode('UTF-8').lstrip().rstrip()
                print(l)
                return l
            else:
                with open('output.wav','wb') as f:
                    while True:
                        l = sock.recv(8192)
                        if not l: 
                            break
                        f.write(l)
                print("File received complete")
        finally:
            sock.close()

    def set_language(self, language:str, model:str):
        '''
        Set port and token by language.
        Set model by gender.
        Params:
            language    :(str) chinese \
                or taiwanese or taiwanese_sandhi or tailuo or tailuo_sandhi or hakka.
            model       :(str) HTS synthesis model name.
        '''
        self.language = language

        if 'hakka' in language:
            self.__port = 10010
            self.__token = "2022@course@tts@hakka"
            self.__model = model

        elif language == 'taiwanese' or language == 'tailuo':
            self.__port = 10011
            self.__token = "2022@course@tts@taiwanese"
            self.__model = model

        elif language == 'taiwanese_sandhi' or language == 'tailuo_sandhi':
            self.__port = 10012
            self.__token = "2022@course@tts@taiwanese"
            self.__model = model

        elif language == 'chinese':
            self.__port = 10015
            self.__token = "2022@course@tts@chinese"
            self.__model = 'M60'

        else:
            raise  ValueError ( "'language' param must be chinese \
                or taiwanese or taiwanese_sandhi or tailuo or tailuo_sandhi or hakka." )
      

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', default='chinese', help='Language to be synthesized, \
        chinese or taiwanese or taiwanese_sandhi or tailuo or tailuo_sandhi or hakka.')
    parser.add_argument('--model', default='M60', help='HTS synthesis model name.')
    parser.add_argument('--text', default='去', help='Text to be synthesized.')
    args = parser.parse_args()
    tts_client = TTSClient()
    tts_client.set_language(language=args.language, model=args.model)
    tts_client.askForService(args.text)