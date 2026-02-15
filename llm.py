from yandex_cloud_ml_sdk import YCloudML
import os 
import json
from qwen_api.client import Qwen
from qwen_api.core.types.chat import ChatMessage
import requests

class LLM:
    def __init__(self, model):
        self.model = model
    
    def generate_response(self, data):
        if self.model == 'yandex':
            sdk = YCloudML(
                folder_id="b1gu835v82q677s36ekg",
                auth="AQVN1439cSbZ3zvfEBeKusU4CPtgTVpvxMa5BOQb",
            )
            model = sdk.models.completions("yandexgpt-lite")
            model = model.configure(temperature=0.2)
            result = model.run(data)
            answer = result.alternatives[0].text
            answer = answer.replace("*", "")
            return answer
        elif self.model == 'qwen':
            client = Qwen(api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImQ1MThkYjU2LWRjYzAtNGViYi05MDA3LTJkMDRlZGMwY2Q3MCIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzU4ODIyNTI1LCJleHAiOjE3NjEyMTIxNDh9.RhfF2mOPNtVgu8lkNnoCguYGP2HWpQcrLOyD_lDxl00", cookie="")
            messages = [
                ChatMessage(
                    role="user",
                    content=data,
                    web_search=True,
                    thinking=False,
                )
            ]
            response = client.chat.create(
                messages=messages,
                model="qwen-max-latest",
            )
            print(response)
            return response
        
        elif self.model == 'gemini':
            from google import genai

            client = genai.Client(api_key="AIzaSyA-HIRoBDF_t0t8Ylh7VdUcEvrssvRMkpA")

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=data,
            )

            return response.text
                                    



    def generate_insitute_hint(self, inst, data):
        with open("/Users/deniz_mlg/Desktop/Универ/Введение в разработку ИС/kfu_programs_by_institute.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        pr = data["institutes"][inst]["programs"]
        inst_data = '\n'.join(pr)
        prompt = f"""
Ты специалист приёмной комиссии Казанского Федерального Университета, экспертная система подобрала образовательную программа - тебе нужно вывести её и добавить краткое объяснение, почему она подходит на основании данных об абитуренте.
Входные данные:
Образовательная программа:
"""
        


    