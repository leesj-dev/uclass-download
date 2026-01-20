from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time
import re


# configs
LINK = "https://lcme.ulsan.ac.kr/course/view.php?id=9175"
SECTIONS = [1, 2, 3, 4, 5, 6, 7]

# load environment variables
load_dotenv()
login_id = os.getenv("id")
login_pw = os.getenv("pw")

# set selenium options
options = webdriver.ChromeOptions()
# NOTE: headless mode is not supported because the video player playback button does not work in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(LINK)
driver.implicitly_wait(2)

# login
driver.find_element(By.ID, "input-username").send_keys(login_id)
driver.find_element(By.ID, "input-password").send_keys(login_pw)
driver.find_element(By.XPATH, "//input[@type='submit']").send_keys(Keys.RETURN)
time.sleep(2)


def parse_time(time_str):
    """Convert time string (HH:MM:SS or MM:SS) to seconds"""
    parts = time_str.strip().split(":")
    if len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    else:  # SS
        return int(parts[0])


def format_time(seconds):
    """Format seconds to (HH:)MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def parse_playback_rate(rate_str):
    """Parse playback rate from string like 'x 1.5' to float"""
    match = re.search(r"x?\s*([\d.]+)", rate_str.strip())
    if match:
        return float(match.group(1))
    return 1.0


def is_video_completed(driver):
    """Check if video is 100% completed"""
    try:
        progress_element = driver.find_element(By.CLASS_NAME, "vc-pctrl-seek-limit-progress")
        style = progress_element.get_attribute("style")
        return "width: 100%" in style or "width:100%" in style
    except:
        return False


def wait_for_video_completion(driver):
    """Wait for video to complete playback"""
    print("  초기 로딩 중 (3초)...")
    time.sleep(3)

    while True:
        try:
            # Check if already completed
            if is_video_completed(driver):
                print("\n  ✓ 이미 100% 완료된 영상입니다")
                return

            # Get current time, total duration, and playback rate
            curr_time_elem = driver.find_element(By.CLASS_NAME, "vc-pctrl-curr-time")
            total_duration_elem = driver.find_element(By.CLASS_NAME, "vc-pctrl-total-duration")
            playback_rate_elem = driver.find_element(By.CLASS_NAME, "vc-pctrl-playback-rate-toggle-btn")

            curr_time_str = curr_time_elem.text
            total_duration_str = total_duration_elem.text
            playback_rate_str = playback_rate_elem.text

            curr_seconds = parse_time(curr_time_str)
            total_seconds = parse_time(total_duration_str)
            playback_rate = parse_playback_rate(playback_rate_str)

            remaining_seconds = total_seconds - curr_seconds
            actual_wait_time = remaining_seconds / playback_rate

            remaining_formatted = format_time(remaining_seconds)
            wait_time_formatted = format_time(actual_wait_time)

            # Use \r to overwrite the same line
            print(f"\r  현재 {curr_time_str} / {total_duration_str} (배속 {playback_rate}x) | 남은 시간 {remaining_formatted} → 대기 {wait_time_formatted}", end="", flush=True)

            if remaining_seconds <= 0:
                print("\n  ✓ 영상 재생 완료!")
                break

            # Wait with a buffer time and periodic checks
            check_interval = min(10, actual_wait_time / 2)
            time.sleep(check_interval)

        except Exception as e:
            print(f"\n  영상 진행률 확인 오류: {e}")
            time.sleep(5)


# for each specified section
for i in SECTIONS:
    try:
        # get section and section name
        section = driver.find_element(By.ID, f"section-{i}")
        section_name = section.find_element(By.XPATH, ".//h3[@class='sectionname']/a").get_attribute("innerText")
        print(f"\n{'='*60}")
        print(f"섹션 {i}: {section_name}")
        print(f"{'='*60}")

        # get video list (only xncommons activities)
        video_list = section.find_elements(By.XPATH, ".//ul[@class='section img-text']/li[contains(@class, 'xncommons')]")
        print(f"이 섹션에서 {len(video_list)}개의 영상을 찾았습니다\n")

        # for each video in the list
        for idx, video in enumerate(video_list, 1):
            try:
                # get video link and video name
                link_element = video.find_element(By.XPATH, ".//div[@class='activityinstance']/a")
                onclick_attr = link_element.get_attribute("onclick")
                video_link = onclick_attr.split("'")[1]
                video_name = link_element.find_element(By.XPATH, ".//span[@class='instancename']").get_attribute("innerText").replace(" CMAKER", "").strip()

                print(f"[{idx}/{len(video_list)}] {video_name}")

                # open new tab
                driver.switch_to.new_window("tab")
                domain = "/".join(LINK.split("/")[:3])
                driver.get(domain + video_link)
                time.sleep(2)

                # switch to video frame
                driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='vod_viewer']/iframe"))
                driver.switch_to.frame(driver.find_element(By.ID, "ViewerFrame"))

                # check if already 100% completed
                if is_video_completed(driver):
                    print("  ✓ 이미 100% 완료, 건너뜁니다...")
                else:
                    # play video
                    try:
                        play_btn = driver.find_element(By.CLASS_NAME, "vc-front-screen-play-btn")
                        play_btn.click()
                        print("  ▶ 재생 시작...")
                    except:
                        print("  ▶ 이미 재생 중이거나 재생 버튼을 찾을 수 없습니다...")

                    # wait for completion
                    wait_for_video_completion(driver)

                # close tab and return to main window
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)

            except Exception as e:
                print(f"  ✗ 영상 처리 오류: {e}")
                # close tab if open and return to main window
                try:
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                except:
                    pass
                continue

    except Exception as e:
        print(f"\n✗ 섹션 {i} 처리 오류: {e}")
        continue

print("\n" + "=" * 60)
print("모든 영상 처리 완료!")
print("=" * 60)
driver.quit()
