import json
import socket
import struct


def askForService(token: str, model_name: str, data: bytes) -> dict:
    '''
    DO NOT MODIFY THIS PART
    '''
    HOST = "140.116.245.157"
    PORT = 2802
    lang = "Mandarin"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    myJson = None

    try:
        sock.connect((HOST, PORT))
        msg_dict = {"token": token, "source": "P", "lang": lang,
                    "model": model_name, "service_id": str(PORT), "data_len": len(data)}
        # msg_dict = {"token": token, "source": "P", "model": model_name, "service_id": str(PORT),"data_len": len(data)}

        msg = json.dumps(msg_dict).encode('utf-8')
        msg = struct.pack(">I", len(msg)) + msg  # add msg len
        sock.sendall(msg)  # send message to server
        sock.sendall(data)  # send audio data to server

        # receive result
        received_all = ''
        while 1:
            received = str(sock.recv(1024), "utf-8")
            if len(received) == 0:
                sock.close()
                break
            received_all += received
    except Exception as e:
        myJson = {"error": e}
        print("ERROR: ", e)
    finally:
        sock.close()
    if myJson:
        return myJson
    # json expecting property name enclosed in double quotes

    return json.loads(received_all.replace("'", '"'))


def recognize_request(file_pth: str, model_name) -> dict:
    '''
    Mi2S ASR API
    lang: 
        Mandarin(中文), taiwanese(台語)
    '''
    token = "testing"
    audio = open(file_pth, 'rb').read()  # read wav in binary mode
    # audio= wave.open(file_pth,'rb')
    # audio =requests.get(file_pth)
    # audio = audio.content
    # audio= audio.readframes(audio.getnframes())
    # print("file_pth: ", file_pth)
    # print("AUDIO: "+(str)(audio))
    # print("Begin Asking for service.")
    result = askForService(token, model_name, audio)
    # print(result)
    return result


if __name__ == "__main__":

    result = recognize_request("../output.wav", "CCH_t")
    print(result)
