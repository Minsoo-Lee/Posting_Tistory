import google.generativeai as genai
import time, re

gemini_key = "AIzaSyC-_RsZlNX73tC--cLmz_T4c2DR0pbsMVM"
model = None

def init_gemini():
    global model
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    # 모델 찾기
    # models = genai.list_models()
    # for model in models:
    #     print(f"Model: {model.name}")
    #     print(f"Description: {model.description}")
    #     print(f"Supported Generation Methods: {model.supported_generation_methods}")
    #     print("-" * 20)


def get_response(keyword):
    global model
    response = None
    while response is None:
        response = model.generate_content(f"""
            내가 너에게 제품을 알려줄거야. 그 제품에 대해서 자세하게 설명을 해줘. 
            본문과 제목은 자연스럽게 유지하고, 사람이 쓴 것처럼 구조를 잘 배치해 줘야 해. 
            내용은 한 10줄 정도였으면 좋겠어.
            그리고 너가 작성한 내용에서 사진을 총 다섯 군데에 넣을거야.
            사진이 들어갈 만한 위치에 [사진]이라는 구분자를 넣어줘.
            
            자, 이제 너가 설명할 제품은 {keyword}야.
        """)

    print(f"response: {response.text}")

    return response.text

