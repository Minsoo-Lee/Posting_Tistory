import google.generativeai as genai
import time

gemini_key = "AIzaSyC-_RsZlNX73tC--cLmz_T4c2DR0pbsMVM"
model = None

def init_gemini():
    global model
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

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
    result = []
    while response is None:
        response = model.generate_content("""
            내가 제품과 관련된 키워드를 던져주면, 그 제품에 대해서 설명을 해줘. 
            본문과 제목은 자연스럽게 유지하고, 사람이 쓴 것처럼 구조를 잘 배치해 줘야 해. 
            이해했으면 OK라고 말해줘.
        """)

    time.sleep(2)

    response = model.generate_content(keyword)
    time.sleep(2)
    response = model.generate_content(response.text + """
        \n여기까지가 너가 작성해 준 내용인데, 사진을 총 다섯 군데에 넣을거야. 
        사진이 들어갈 만한 위치에 [사진]이라는 구분자를 넣어줘.
    """)
    time.sleep(2)
    photos = model.generate_content(response.text + """
        \n여기까지가 너가 작성해 준 내용인데, [사진]이라는 구분자를 대체할 수 있는 사진 5장을 생성하고 싶어.
        내가 다른 AI에서 사진을 생성할 수 있도록, 사진 5장에 관한 설명을 차례대로 [] 안에 넣어서 설명해 줘.
        그리고 그 설명 외에 부연설명이나 잡스러운 말들은 절대 하지 말고 사진 설명만 [] 안에 넣어줘.
    """)
    time.sleep(5)

    # 정규 표현식을 사용하여 대괄호 안의 내용을 추출합니다.
    matches = re.findall(r'\[(.*?)\]', photos.text)

    # 추출된 내용을 리스트로 저장합니다.
    descriptions = list(matches)
    print(descriptions)

    return response.text

