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
LINK = "https://lcme.ulsan.ac.kr/course/view.php?id=9096"
SECTIONS = [4]
SAVEPATH = "/Users/leesj/Documents/대학교/예과 2학년 1학기/세포와대사"

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
driver.find_element(By.ID, "input-username").send_keys(login_id)
driver.find_element(By.ID, "input-password").send_keys(login_pw)
driver.find_element(By.XPATH, "//input[@type='submit']").send_keys(Keys.RETURN)

# for each specified section
for i in SECTIONS:
    # get section XPATH and section name
    section = driver.find_element(By.ID, f"section-{i}")
    section_name = section.find_element(By.XPATH, ".//div/h3/a").get_attribute("innerText")
    os.makedirs(os.path.join(SAVEPATH, section_name), exist_ok=True)

    # get video list
    video_list = []
    j = 1
    while True:
        try:
            video = section.find_element(By.XPATH, f".//div/ul/li[{j}]")
            video_list.append(video)
            j += 1
        except:
            break

    # for each video in the list
    for video in video_list:
        # get video link and video name
        try:
            video_link = video.find_element(By.XPATH, ".//div/div/div[2]/div/a").get_attribute("onclick").split("'")[1]
            video_name = video.find_element(By.XPATH, ".//div/div/div[2]/div/a/span").get_attribute("innerText").replace("\nCMAKER", "")
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
