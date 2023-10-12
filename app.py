from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import os
import openai
import requests
from utils.AuthV3Util import addAuthParams
import json


app = Flask(__name__)
api = Api(app)
CORS(app)
# 设置上传文件保存路径
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
openai.api_key = os.getenv("OPENAI_API_KEY")

# 您的应用ID
YOUDAO_APP_KEY = os.getenv("YOUDAO_API_KEY")
# 您的应用密钥
YOUDAO_APP_SECRET = os.getenv("YOUDAO_API_SECRET")

YOUDAO_APP_ADDRESS='https://openapi.youdao.com/api'


def doCall(url, header, params, method):
    if 'get' == method:
        return requests.get(url, params)
    elif 'post' == method:
        return requests.post(url, params, header)


class AudioUpload(Resource):
    def post(self):
        try:
            audio_file = request.files['audio']
            if audio_file:
                filename = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.wav')
                audio_file.save(filename)
                audio_file=open("uploads/audio.wav","rb")
                #获取录入的音频文本
                transcript = openai.Audio.transcribe("whisper-1", audio_file,temperature=0)
                transcript=transcript.text
                transcript.encode(encoding="utf-8")

                #翻译音频文本
                lang_from = 'zh-CHS'
                lang_to = 'en'
                data = {'q': transcript, 'from': lang_from, 'to': lang_to}
                addAuthParams(YOUDAO_APP_KEY,YOUDAO_APP_SECRET, data)
                header = {'Content-Type': 'application/x-www-form-urlencoded'}
                res = doCall(YOUDAO_APP_ADDRESS, header, data, 'post')
                res=str(res.content,"utf-8")
                res=json.loads(res)
                en_translation=res['translation'][0]

                

                return {'message': transcript+"  "+en_translation}, 200
            else:
                return {'message': '没有找到音频文件'}, 400
        except Exception as e:
            return {'message': '音频处理失败', 'error': str(e)}, 500

# 添加API路由
api.add_resource(AudioUpload, '/upload')

if __name__ == '__main__':
    app.run(debug=True)
