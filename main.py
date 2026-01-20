from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time
import json
import requests


# configs
LINK = "https://ulms.ulsan.ac.kr/course/view.php?id=40630"
SECTIONS = None  # None이면 모든 섹션을 자동으로 찾습니다. 특정 섹션만 원하면 [1, 2, 3] 형태로 지정하세요.
SAVEPATH = "/Users/leesj/Documents/대학교/예과 2학년/선택과정/병원 밖 진료실"

# load environment variables
load_dotenv()
login_id = os.getenv("id")
login_pw = os.getenv("pw")

# set selenium options
options = webdriver.ChromeOptions()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})  # enable network response logging
# NOTE: headless mode is not supported because the video player playback button does not work in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(LINK)
driver.implicitly_wait(2)

# login
driver.find_element(By.CSS_SELECTOR, ".btn.btn-sso").click()
driver.find_element(By.ID, "id").send_keys(login_id)
driver.find_element(By.ID, "pw").send_keys(login_pw)
driver.find_element(By.CSS_SELECTOR, ".login.btn-login").send_keys(Keys.RETURN)
time.sleep(2)

# auto-detect sections if not specified
if SECTIONS is None:
    all_sections = driver.find_elements(By.CSS_SELECTOR, "li.section.main[id^='section-']")
    SECTIONS = []
    for section in all_sections:
        section_id = section.get_attribute("id")
        if section_id and section_id.startswith("section-"):
            try:
                section_num = int(section_id.replace("section-", ""))
                if section_num > 0:  # section-0은 제외 (Course Summary)
                    SECTIONS.append(section_num)
            except ValueError:
                pass
    SECTIONS.sort()
    print(f"자동으로 감지된 섹션: {SECTIONS}\n")

# for each specified section
for i in SECTIONS:
    # get section XPATH and section name
    section = driver.find_element(By.ID, f"section-{i}")
    section_name = section.find_element(By.XPATH, ".//h3[@class='sectionname']/span/a").get_attribute("innerText")
    os.makedirs(os.path.join(SAVEPATH, section_name), exist_ok=True)

    # get video list
    video_list = section.find_elements(By.XPATH, ".//ul[@class='section img-text']/li[contains(@class, 'activity')]")

    # for each video in the list
    for video in video_list:
        # get video link and video name
        try:
            link_element = video.find_element(By.XPATH, ".//div[@class='activityinstance']/a")
            onclick_attr = link_element.get_attribute("onclick")
            video_link = onclick_attr.split("'")[1]
            video_name = link_element.find_element(By.XPATH, ".//span[@class='instancename']").get_attribute("innerText").replace(" CMAKER", "").strip()
        except:  # 학습자료 등이 있을 경우 예외처리
            continue

        # open new tab
        try:
            driver.switch_to.new_window("tab")
            domain = "/".join(LINK.split("/")[:3])
            driver.get(domain + video_link)
            driver.implicitly_wait(2)
        except:  # mp3 등이 있을 경우 예외처리
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue

        # play video
        driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='vod_viewer']/iframe"))
        driver.switch_to.frame(driver.find_element(By.ID, "ViewerFrame"))
        driver.find_element(By.CLASS_NAME, "vc-front-screen-play-btn").click()
        time.sleep(4)  # wait for ssvideo to load

        # get ssvideo url
        def process_browser_log_entry(entry):
            response = json.loads(entry["message"])["message"]
            return response

        browser_log = driver.get_log("performance")
        events = [process_browser_log_entry(entry) for entry in browser_log]
        events = [event for event in events if "Network.response" in event["method"]]

        for event in events:
            params = event["params"]
            if "response" in params:
                url = params["response"]["url"]
                if url.endswith("ssmovie.mp4"):
                    ssvideo_url = url
                    break

        # save video
        if ssvideo_url:
            with open(os.path.join(SAVEPATH, section_name, f"{video_name}.mp4"), "wb") as f:
                f.write(requests.get(ssvideo_url).content)

        # close tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
