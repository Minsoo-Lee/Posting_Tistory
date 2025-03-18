import threading
import json
import os
import wx, openpyxl, time, wx._xml, random, sys, uuid, requests, csv
import wx.richtext as rt
import driver, gemini, coupang
import json

thread_running = False
app = wx.App(False)
frame = wx.Frame(None, wx.ID_ANY, "PostingFacebook")
max_time = 2100
min_time = 900
# max_time = 2
# min_time = 1
thread_end = False
account_index = 1
post_check = True
csv_files = []
URL = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/search"
IF_FIRST = True

def append_log(log):
    current_time = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime())
    # 내 환경에서 테스트 시에만 흰색
    color = wx.BLACK
    # color = wx.WHITE
    if '[ERROR]' in log or '오답' in log:
        color = wx.RED
    if '작업이 모두 끝났습니다.' in log or '완료' in log:
        color = wx.GREEN
    if '초기화' in log:
        color = wx.BLUE
    log = current_time + log

    log_text_widget.BeginTextColour(color)  # 텍스트 색상 시작
    log_text_widget.WriteText(log + "\n")
    log_text_widget.EndTextColour()  # 텍스트 색상 종료
    log_text_widget.ShowPosition(log_text_widget.GetLastPosition())

def load_csv():
    global csv_files
    csv_num = 0
    csv_files.clear()

    file_path = "keyword.csv"

    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                if len(row) != 1:
                    # 로그 창에 띄우기
                    wx.CallAfter(append_log, f"[ERROR] 잘못된 데이터입니다. 열 개수를 확인해주세요.")
                    return
                csv_files.append(row)
                csv_listbox.Append(row[0])
    except Exception as e:
        # 파일 열기 실패 처리
        wx.CallAfter(append_log, f"[ERROR] 파일을 열 수 없습니다: {e}")
        return

    # 파일 불러오기 완료
    wx.CallAfter(append_log, "파일 불러오기 완료")


def execute_thread():
    global thread_running, csv_files, IF_FIRST

    # 1. 홈페이지 접속 및 포스팅 화면 진입
    driver.init_chrome()
    wx.CallAfter(append_log, "티스토리에 접속합니다.")
    driver.open_tistory()
    wx.CallAfter(append_log, "로그인을 실행합니다.")
    driver.click_login()
    driver.login("minsoo1101", "msLee9164@@")
    # driver.login(kakaoId_input.Value, kakaoPw_input.Value)
    wx.CallAfter(append_log, "로그인 완료")
    posting_url = driver.enter_posting()


    # 2. CSV 파일 읽어오기
    load_csv()
    time.sleep(1)
    #
    # 3. Gemini 초기화
    gemini.init_gemini()
    wx.CallAfter(append_log, f"Gemini API를 초기화합니다")
    time.sleep(1)

    # csv_files에서 가져온 키워드들을 Gemini로 글 생성
    wx.CallAfter(append_log, f"Gemini API를 사용하여 작성할 글을 생성합니다.")
    #
    # 5. 키워드를 돌아가면서 글 작성
    for keyword in csv_files:
        # 그림 인덱스
        index = 1
        if IF_FIRST is False:
            driver.enter_url(posting_url)
        wx.CallAfter(append_log, "포스팅 화면 진입")
        driver.select_category("JAVA")
        # driver.select_category(category_input.Value)

        # 5-1. 쿠팡 API로 데이터 수신
        path = coupang.get_path(keyword[0], 10)
        coupang_response = coupang.get_response(path)
        # print(json.dumps(coupang_response, indent=4, ensure_ascii=False))

        api_data = coupang.filter_products(keyword[0], coupang_response)          # 쿠팡 API로 상품 정보 먼저 긁어오기
        # print(json.dumps(api_data, indent=4, ensure_ascii=False))

        image_urls = coupang.download_images(api_data)
        image_qty = len(image_urls)
        coupang_url = coupang_response['landingUrl']           # 제휴 url을 내부 메모리에 저장
        coupang.add_border(50, "blue", image_qty)               # 이미지에 테두리 추가

        # 5-2. Gemini API로 글 생성
        response = gemini.get_response(keyword, image_qty)
        wx.CallAfter(append_log, f"{response[0]}\n{response[1]}")

        title, content = response[0], response[1]
        time.sleep(1)

        # final_content = driver.make_final_content(content_list, image_qty, os.getcwd())

        # 5-4. 열려있는 화면에서 글 작성하기
        driver.post_title(title)
        driver.align_center()
        driver.enter_iframe()

        content_list = driver.divide_content(content)
        i = 0
        for i in range(0, image_qty):
            driver.post_content(content_list[i])
            driver.post_image(i + 1)
        driver.post_content(content_list[i + 1])
        driver.post_content("<br><b>[" + keyword[0] + " 구매하기]</b><br>", False)

        #     driver.post_content(content_list[i])
        #     driver.post_image(i + 1)
        # driver.post_content(content_list[i])

        # driver.post_content(final_content)
        driver.post_href(coupang_url)
        driver.quit_frame()

        driver.click_posting()
        driver.post_public()
        wx.CallAfter(append_log, f"[{keyword[0]}]포스팅 완료")

        # 5-5. 다운받은 이미지 삭제
        coupang.remove_images(len(image_urls))
        IF_FIRST = False

    # 작업 다 끝나면 버튼 다시 활성화, 쓰레드 종료
    wx.CallAfter(execute_button.Enable, True)
    thread_running = False

def execute(event):
    global thread_running
    if thread_running:
        return

    thread_running = True
    thread = threading.Thread(target=execute_thread)
    execute_button.Enable(False)  # 버튼 비활성화
    thread.start()

# 전체 패널
panel = wx.Panel(frame, wx.ID_ANY)
panel.SetBackgroundColour("#f5f5f5")  # 배경 색상 설정
panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
frame_sizer = wx.BoxSizer(wx.VERTICAL)

# 왼쪽 공간
left_panel = wx.Panel(panel, wx.ID_ANY)
left_panel.SetBackgroundColour("#ffffff")  # 배경 색상 설정
left_sizer = wx.BoxSizer(wx.VERTICAL)

# Kakao ID 입력 필드
kakaoId_input_label = wx.StaticText(left_panel, wx.ID_ANY, "ID", size=(90, 30))
kakaoId_input_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
kakaoId_input_label.SetForegroundColour(wx.Colour(0, 102, 204))  # 텍스트 색상 설정
kakaoId_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 30), style=wx.TE_LEFT)
kakaoId_input.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

kakaoId_sizer = wx.BoxSizer(wx.HORIZONTAL)
kakaoId_sizer.Add(kakaoId_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
kakaoId_sizer.Add(kakaoId_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

# Kakao 비밀번호 입력 필드
kakaoPw_input_label = wx.StaticText(left_panel, wx.ID_ANY, "비밀번호", size=(90, 30))
kakaoPw_input_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
kakaoPw_input_label.SetForegroundColour(wx.Colour(0, 102, 204))
kakaoPw_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 30), style=wx.TE_PASSWORD)
kakaoPw_input.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

kakaoPw_sizer = wx.BoxSizer(wx.HORIZONTAL)
kakaoPw_sizer.Add(kakaoPw_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
kakaoPw_sizer.Add(kakaoPw_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

# 카테고리명 입력 필드
category_input_label = wx.StaticText(left_panel, wx.ID_ANY, "카테고리명", size=(90, 30))
category_input_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
category_input_label.SetForegroundColour(wx.Colour(0, 102, 204))
category_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 30))
category_input.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

category_sizer = wx.BoxSizer(wx.HORIZONTAL)
category_sizer.Add(category_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
category_sizer.Add(category_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

# CSV 목록 (리스트박스 스타일 변경)
csv_listbox = wx.ListBox(left_panel, wx.ID_ANY, style=wx.LB_SINGLE, size=(330, 250))
csv_listbox.SetBackgroundColour(wx.Colour(245, 245, 245))  # 리스트박스 배경 색상 설정
csv_listbox.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

# 작업 수행 버튼
execute_button = wx.Button(left_panel, wx.ID_ANY, "작업 수행", size=(330, 40))
execute_button.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
execute_button.SetBackgroundColour(wx.Colour(0, 153, 255))  # 버튼 배경 색상 설정
execute_button.SetForegroundColour(wx.Colour(255, 255, 255))  # 버튼 텍스트 색상 설정
execute_button.Bind(wx.EVT_BUTTON, execute)

left_sizer.Add(kakaoId_sizer, 0, wx.ALL, 10)
left_sizer.Add(kakaoPw_sizer, 0, wx.ALL, 10)
left_sizer.Add(category_sizer, 0, wx.ALL, 10)
left_sizer.Add(csv_listbox, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)  # proportion을 1로 설정
left_sizer.Add(execute_button, 0, wx.ALL | wx.ALIGN_CENTER, 10)
left_panel.SetSizer(left_sizer)

# 구분선
separator_line = wx.StaticLine(panel, wx.ID_ANY, style=wx.LI_VERTICAL, size=(1, 580))

# 오른쪽 공간
right_panel = wx.Panel(panel, wx.ID_ANY)
right_panel.SetBackgroundColour("#ffffff")  # 배경 색상 설정
right_sizer = wx.BoxSizer(wx.VERTICAL)

# 로그 텍스트 영역
log_text_widget = rt.RichTextCtrl(right_panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(500, 580))
log_text_widget.SetBackgroundColour(wx.Colour(240, 240, 240))  # 배경 색상 설정
log_text_widget.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

right_sizer.Add(log_text_widget, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
right_panel.SetSizer(right_sizer)

# 패널들을 전체 패널에 배치
panel_sizer.Add(left_panel, 0)
panel_sizer.Add(separator_line, 0)
panel_sizer.Add(right_panel, 0)
panel.SetSizer(panel_sizer)

frame_sizer.Add(panel, 1, wx.EXPAND)
frame.SetSizerAndFit(frame_sizer)
frame.Show()

app.MainLoop()

# 패널 배치 끝
