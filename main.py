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
    driver.input_login("minsoo1101", "msLee9164@@")
    # driver.login(kakaoId_input.Value, kakaoPw_input.Value)
    # wx.CallAfter(append_log, "캡챠를 해결해주세요")
    # time.sleep(30)

    driver.complete_login()

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
        driver.select_category("- 사진 + 150자 제거")
        # driver.select_category(category_input.Value)

        # 5-1. 쿠팡 API로 데이터 수신
        path = coupang.get_path(keyword[0], 10)
        coupang_response = coupang.get_response(path)
        # print(json.dumps(coupang_response, indent=4, ensure_ascii=False))

        api_data = coupang.filter_products(keyword[0], coupang_response)          # 쿠팡 API로 상품 정보 먼저 긁어오기
        # print(json.dumps(api_data, indent=4, ensure_ascii=False))

        image_urls = coupang.download_images(api_data, keyword[0])
        # print(json.dumps(image_urls, indent=4, ensure_ascii=False))
        image_qty = len(image_urls)
        coupang_url = coupang_response['landingUrl']           # 제휴 url을 내부 메모리에 저장
        coupang.add_border(50, "blue", image_qty, keyword[0])               # 이미지에 테두리 추가

        # 5-2. Gemini API로 글 생성
        response = gemini.get_response(keyword, image_qty)
        # print(keyword)
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
            driver.post_image(i + 1, keyword[0])
        driver.post_content(content_list[i + 1])
        driver.post_content("<br><b>[" + keyword[0] + " 구매하기]</b><br>", False)

        #     driver.post_content(content_list[i])
        #     driver.post_image(i + 1)
        # driver.post_content(content_list[i])

        # driver.post_content(final_content)
        driver.post_href(coupang_url)
        driver.quit_frame()


        driver.click_posting()
        time.sleep(120)

        # driver.post_public()
        wx.CallAfter(append_log, f"[{keyword[0]}]포스팅 완료")

        # 5-5. 다운받은 이미지 삭제
        coupang.remove_images(len(image_urls), keyword[0])
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

def check(event):
    driver.init_chrome()
    titles = [
        "정관장 홍삼정: 면역력 강화와 활력 충전을 한 번에!",
        "황제의 기품을 담은 종근당 황제 침향단",
        "종근당 침향환 골드: 황제의 비밀, 당신의 건강에 드리는 선물",
        "락토핏 골드, 온 가족 장 건강 지킴이",
        "고려홍삼정 365 스틱: 당신의 하루를 채워줄 진짜 활력",
        "오로나민C: 당신의 하루에 생기를 불어넣는 비타민C 드링크!",
        "광동 배도라지 쌍화, 환절기 건강 지킴이",
        "데이퓨어로 매일 빛나는 피부, 꿈꿔본 적 있나요?"
    ]
    is_first = True;

    for x in range(1, len(titles)):
        driver.enter_url("https://www.google.com")
        driver.search_posting(titles[x], is_first)
        is_first = False

# 전체 패널
panel = wx.Panel(frame, wx.ID_ANY)
panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
frame_sizer = wx.BoxSizer(wx.VERTICAL)

# 왼쪽 공간
left_panel = wx.Panel(panel, wx.ID_ANY)
left_sizer = wx.BoxSizer(wx.VERTICAL)

kakaoId_input_label = wx.StaticText(left_panel, wx.ID_ANY, "ID", size=(90, 20))
kakaoId_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20))

kakaoId_sizer = wx.BoxSizer(wx.HORIZONTAL)
kakaoId_sizer.Add(kakaoId_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
kakaoId_sizer.Add(kakaoId_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

kakaoPw_input_label = wx.StaticText(left_panel, wx.ID_ANY, "비밀번호", size=(90, 20))
kakaoPw_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20), style=wx.TE_PASSWORD)

kakaoPw_sizer = wx.BoxSizer(wx.HORIZONTAL)
kakaoPw_sizer.Add(kakaoPw_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
kakaoPw_sizer.Add(kakaoPw_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

category_input_label = wx.StaticText(left_panel, wx.ID_ANY, "카테고리명", size=(90, 20))
category_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20))

category_sizer = wx.BoxSizer(wx.HORIZONTAL)
category_sizer.Add(category_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
category_sizer.Add(category_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

csv_listbox = wx.ListBox(left_panel, wx.ID_ANY, style=wx.LB_SINGLE, size=(330, 400))

# id_input_label = wx.StaticText(left_panel, wx.ID_ANY, "ID", size=(90, 20))
# id_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20))
#
# id_sizer = wx.BoxSizer(wx.HORIZONTAL)
# id_sizer.Add(id_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
# id_sizer.Add(id_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
#
# pw_input_label = wx.StaticText(left_panel, wx.ID_ANY, "비밀번호", size=(90, 20))
# pw_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20), style=wx.TE_PASSWORD)
#
# pw_sizer = wx.BoxSizer(wx.HORIZONTAL)
# pw_sizer.Add(pw_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
# pw_sizer.Add(pw_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
#
# url_input_label = wx.StaticText(left_panel, wx.ID_ANY, "페이지 URL", size=(90, 20))
# url_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20))
#
# url_sizer = wx.BoxSizer(wx.HORIZONTAL)
# url_sizer.Add(url_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
# url_sizer.Add(url_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

execute_button = wx.Button(left_panel, wx.ID_ANY, "작업 수행", size=(330, 30))
execute_button.Bind(wx.EVT_BUTTON, execute)
execute_button.Enable(True)

check_button = wx.Button(left_panel, wx.ID_ANY, "SEO Check", size=(330, 30))
check_button.Bind(wx.EVT_BUTTON, check)
check_button.Enable(True)

left_sizer.Add(kakaoId_sizer, 0, wx.ALL, 10)
left_sizer.Add(kakaoPw_sizer, 0, wx.ALL, 10)
left_sizer.Add(category_sizer, 0, wx.ALL, 10)
left_sizer.Add(csv_listbox, 1, wx.LEFT | wx.RIGHT, 10)  # proportion을 1로 설정
# left_sizer.Add(id_sizer, 0, wx.ALL, 10)
# left_sizer.Add(pw_sizer, 0, wx.ALL, 10)
# left_sizer.Add(url_sizer, 0, wx.ALL, 10)
left_sizer.Add(execute_button, 0, wx.ALL, 10)
left_sizer.Add(check_button, 0, wx.ALL, 10)
left_panel.SetSizer(left_sizer)

# 구분선
separator_line = wx.StaticLine(panel, wx.ID_ANY, style=wx.LI_VERTICAL, size=(1, 580))

# 오른쪽 공간
right_panel = wx.Panel(panel, wx.ID_ANY)
right_sizer = wx.BoxSizer(wx.VERTICAL)

log_text_widget = rt.RichTextCtrl(right_panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(500, 580))

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
