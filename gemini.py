import google.generativeai as genai
import time, re

gemini_key = "AIzaSyC-_RsZlNX73tC--cLmz_T4c2DR0pbsMVM"
model = None

INTRO = "<br>쿠팡 활동의 일환으로 수수료를 받습니다.<br><br>"

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


def get_response(keyword, n):
    global model
    response = None
    while response is None:
        # 제품 상세 글 작성 시
        # response = model.generate_content(f"""
        #             내가 너에게 제품을 알려줄거야. 그 제품에 대해서 자세하게 설명을 해줘.
        #             제목은 키워드 그대로 쓰지 말고, 제품을 잘 어필할 수 있었으면 좋겠어.
        #             본문과 제목은 자연스럽게 유지하고, 사람이 쓴 것처럼 구조를 잘 배치해 줘야 해.
        #             내용은 한 2000자 정도였으면 좋겠어.
        #             그리고 제목 뒤에 [구분]이라는 구분자를 넣어주고, 제목을 마크다운 언어로 쓰지 말고 그냥 작성해 줘.
        #             그리고 본문에 줄바꿈 문자를 적절하게 써서 가독성을 높여줘.
        #
        #             자, 이제 너가 설명할 제품은 {keyword}야.
        #         """)

        response = model.generate_content(f"""
                    내가 너에게 제품을 알려줄거야. 너는 그 제품을 홍보하는 마케터야.
                    제목은 키워드 그대로 쓰지 말고, 제품을 잘 어필할 수 있었으면 좋겠어. 그리고 제목은 반드시 제품 이름으로 시작해 줘.
                    본문과 제목은 자연스럽게 유지하고, 사람이 쓴 것처럼 구조를 잘 배치해 줘야 해. 
                    제목 뒤에 [구분]이라는 구분자를 넣어주고, 제목과 본문 모두 마크다운 언어로 쓰지 말고 그냥 작성해 줘.
                    
                    제목을 작성하고 나서는 공백 포함 150자 이내로 사람들의 관심을 끌 수 있는 핵심 문장들을 서론으로 적어 주고, 서론 다음에는 <br> 태그를 두 개 넣어줘.
                    서론이 끝나면 "쿠팡 활동의 일환으로 수수료를 받습니다." 라는 문장을 적고, 그 뒤에 <br> 태그를 두 개 적어줘
                    
                    그리고 본문에 줄바꿈 문자를 적절하게 써서 가독성을 높여주고 소제목은 {n}개만 작성해 줘. 소제목 뒤에는 [사진 삽입]이라는 구분자를 넣어줘.
                    소제목에 해당하는 내용들은 500자 정도로 작성해 줘.     
                    
                    본문에서 소제목으로 할 문장은 <h3></h3> 태그로 감싸주고, 굵게 할 문장 혹은 단어는 <b></b> 태그로 감싸주고,
                    좀 중요한 문장이다 싶은 것들은 <span style="color:blue;"></span> 태그로 감싸줘.
                    그리고 줄바꿈 할 때는 문장 앞에 <br>태그를 넣어주는데, 소제목 다음에 처음 나오는 문장에는 넣지 마.
                    그리고 소제목 앞에는 <br> 태그를 2개 넣어줘.
                    
                    마지막으로, 내가 이 요청을 할 때마다 본문과 제목은 전부 다 다르게 해 줘.                    
                    
                    자, 이제 너가 설명할 제품은 {keyword}야.
                """)

    # outro = f"<br><br>[{keyword[0]} 구매하기]<br>"
    split_pcs = response.text.split("[구분]")
    split_pcs[1] = split_pcs[0] + "<br><br>" + split_pcs[1].strip()
    # split_pcs[1] = split_pcs[0] + "<br>" + INTRO + split_pcs[1].strip()
    # split_pcs[1] = split_pcs[0] + "<br>" + INTRO + split_pcs[1].strip() + outro
    wait(1)

    return split_pcs

def wait(sec):
    time.sleep(sec)
