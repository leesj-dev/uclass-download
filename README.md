# uclass-download
울산대학교 온라인 LMS의 동영상들을 자동적으로 다운로드하는 Selenium 매크로입니다. 강좌의 전체 또는 일부 영상을 자동적으로 다운로드한 뒤 생성된 폴더에 동영상을 저장합니다. 이 프로그램은 영상자료가 아닌 음성자료, pdf 자료 등은 다운로드하지 않습니다.

## 개발 배경
온라인 LMS의 동영상을 다운로드하는 것은 그리 어려운 일이 아닙니다. 개발자 도구의 Network 탭에서 동영상의 URL을 찾아서 다운로드를 하면 됩니다. 그러나 이 방법은 강의영상에 일일이 들어가서 동영상의 URL을 찾는 것이 번거롭다는 단점이 있습니다. 이 프로그램은 Selenium을 이용하여 이러한 과정을 자동화하였습니다.

## 이용 방법
1. pip를 이용하여 `python-dotenv`, `selenium`, `webdriver-manager` 패키지를 설치해줍니다.
`pip install python-dotenv selenium webdriver-manager`
2. `main.py`가 있는 디렉토리에 `.env` 파일을 생성하고 크레덴셜을 넣습니다.
```
id = (아이디를 여기에 넣습니다)
pw = (비밀번호를 여기에 넣습니다)
```
3. `main.py`에 들어가서 `configs`를 수정해줍니다. `LINK`는 크롤링할 강좌 과목의 링크, `SECTIONS`는 대단원 블럭 중 크롤링할 블럭의 번호, `SAVEPATH`는 파일 저장 경로입니다.
```
LINK = "https://lcme.ulsan.ac.kr/course/view.php?id=9096"
SECTIONS = [2, 3, 4]
SAVEPATH = "/Users/leesj/Documents/대학교/예과 2학년 1학기/세포와대사"
```

## 법적 고지
저작권법 제30조에 의해, 공표된 저작물을 개인적으로 이용하거나 가정 및 이에 준하는 한정된 범위 안에서 이용하는 경우에는 저작물을 복제할 수 있습니다. 따라서 이 프로그램을 이용하여 다운로드한 동영상을 개인적으로 이용하는 것은 저작권법에 위배되지 않습니다. 그러나 다운로드한 동영상을 다른 사람에게 배포하거나 상업적인 목적으로 이용하는 것은 저작권법 제136조에 위배됩니다. 또한 저작권자가 다운로드를 금지하였을 때에는 민사적 문제가 발생할 수 있습니다.

이 프로그램을 사용하여 발생하는 모든 문제에 대한 책임은 사용자에게 있으며, 프로그램 사용으로 인한 법적 문제에 대해서는 책임을 지지 않습니다.