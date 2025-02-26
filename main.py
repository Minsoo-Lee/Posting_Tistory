import threading

import os
import wx, openpyxl, time, wx._xml, random, sys, uuid, requests, csv
import wx.richtext as rt
import driver, gemini

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

def append_log(log):
    current_time = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime())
    # 내 환경에서 테스트 시에만 흰색
    # color = wx.BLACK
    color = wx.WHITE
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
    print(file_path)

    try:
        with open(file_path, 'r', newline='') as file:
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
    wx.CallAfter(time.sleep, 2)


def execute_thread():
    global thread_running, csv_files
    gemini.init_gemini()
    contents = []

    load_csv()



    # for keyword in csv_files:
    #     contents.append(gemini.get_response(keyword))
    #     wx.CallAfter(time.sleep, 2)

    print(gemini.get_response("맥북 M1 프로"))

    # 일단 Gemini 테스트 먼저
    # # csv에서 키워드를 가져온 후 내부 메모리에 저장

    #
    #
    #
    # # 홈페이지 접속 및 포스팅 화면 진입
    # driver.init_chrome()
    # wx.CallAfter(append_log, "티스토리에 접속합니다.")
    # driver.open_tistory()
    # wx.CallAfter(append_log, "로그인을 실행합니다.")
    # driver.click_login()
    # driver.login(kakaoId_input.Value, kakaoPw_input.Value)
    # wx.CallAfter(append_log, "로그인 완료")
    # driver.click_posting()

    #
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

code_input_label = wx.StaticText(left_panel, wx.ID_ANY, "추천인 코드", size=(90, 20))
code_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20))

code_sizer = wx.BoxSizer(wx.HORIZONTAL)
code_sizer.Add(code_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
code_sizer.Add(code_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

csv_listbox = wx.ListBox(left_panel, wx.ID_ANY, style=wx.LB_SINGLE, size=(330, 400))

id_input_label = wx.StaticText(left_panel, wx.ID_ANY, "ID", size=(90, 20))
id_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20))

id_sizer = wx.BoxSizer(wx.HORIZONTAL)
id_sizer.Add(id_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
id_sizer.Add(id_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

pw_input_label = wx.StaticText(left_panel, wx.ID_ANY, "비밀번호", size=(90, 20))
pw_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20), style=wx.TE_PASSWORD)

pw_sizer = wx.BoxSizer(wx.HORIZONTAL)
pw_sizer.Add(pw_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
pw_sizer.Add(pw_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

url_input_label = wx.StaticText(left_panel, wx.ID_ANY, "페이지 URL", size=(90, 20))
url_input = wx.TextCtrl(left_panel, wx.ID_ANY, size=(230, 20))

url_sizer = wx.BoxSizer(wx.HORIZONTAL)
url_sizer.Add(url_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
url_sizer.Add(url_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

execute_button = wx.Button(left_panel, wx.ID_ANY, "작업 수행", size=(330, 30))
execute_button.Bind(wx.EVT_BUTTON, execute)
execute_button.Enable(True)

left_sizer.Add(kakaoId_sizer, 0, wx.ALL, 10)
left_sizer.Add(kakaoPw_sizer, 0, wx.ALL, 10)
left_sizer.Add(code_sizer, 0, wx.ALL, 10)
left_sizer.Add(csv_listbox, 1, wx.LEFT | wx.RIGHT, 10)  # proportion을 1로 설정
left_sizer.Add(id_sizer, 0, wx.ALL, 10)
left_sizer.Add(pw_sizer, 0, wx.ALL, 10)
left_sizer.Add(url_sizer, 0, wx.ALL, 10)
left_sizer.Add(execute_button, 0, wx.ALL, 10)
left_panel.SetSizer(left_sizer)

# 구분선
separator_line = wx.StaticLine(panel, wx.ID_ANY, style=wx.LI_VERTICAL, size=(1, 750))

# 오른쪽 공간
right_panel = wx.Panel(panel, wx.ID_ANY)
right_sizer = wx.BoxSizer(wx.VERTICAL)

log_text_widget = rt.RichTextCtrl(right_panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(500, 730))

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
