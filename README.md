# AFPK 영플래너 재무목표 테스트 V0.1

가상의 고객 금융자산과 월 저축액으로 목표시점 예상 금융자산을 계산하는 한국어 Streamlit 앱입니다. 생성형 AI나 API 키를 사용하지 않습니다. 직접 지정하는 외부 패키지는 Streamlit 하나이며, 설치 시 Streamlit의 필수 의존 패키지는 함께 설치됩니다.

## 1. 설치 방법

1. [Python 공식 사이트](https://www.python.org/downloads/)에서 Python 3.12 또는 3.13을 설치합니다. Windows 설치 화면에서는 **Add python.exe to PATH**를 선택하세요.
2. `app.py`, `requirements.txt`, `README.md`를 같은 폴더에 놓습니다. 이 문서가 있는 `outputs` 폴더를 그대로 사용해도 됩니다.
3. 해당 폴더를 탐색기로 열고 주소창에 `powershell`을 입력한 뒤 Enter를 눌러 터미널을 엽니다.
4. 아래 명령을 한 줄씩 실행합니다. 패키지 설치에는 인터넷 연결이 필요합니다.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`python` 명령을 찾을 수 없다면 Python 설치 후 터미널을 다시 열어보세요. `py --version`이 동작하는 환경에서는 처음 두 명령의 `python`을 `py`로 바꿀 수 있습니다. 가상환경을 따로 활성화하지 않으므로 PowerShell 실행 정책을 변경할 필요가 없습니다.

macOS/Linux에서는 다음 명령을 사용합니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 2. 실행 방법

Windows에서 세 파일이 있는 폴더의 터미널에서 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

macOS/Linux:

```bash
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

브라우저가 자동으로 열리지 않으면 [로컬 앱](http://localhost:8501)을 여세요. 실행 중에는 터미널을 열어두고, 종료할 때는 `Ctrl+C`를 누릅니다. 포트 사용 중 오류가 나면 실행 명령 끝에 `--server.port 8502`를 붙이고 `http://localhost:8502`로 접속하세요.

고객 정보와 목표를 입력하면 결과가 자동 갱신됩니다. 금액은 **원**, 수익률은 **%** 단위입니다. 기본 예제는 금융자산 2,000만 원, 월 저축 100만 원, 5년, 연 3%, 목표 1억 원입니다. 인간 검토 메모에 모델의 한계와 최종 판단을 기록하세요. 메모는 접속 세션에서만 유지되고 영구 저장되지 않으며, 새로고침이나 연결 종료 시 사라질 수 있습니다. 입력값을 바꿔도 메모 내용은 자동 갱신되지 않으므로 다시 검토해야 합니다.

## 3. 파일 구조

```text
outputs/
├── app.py            # 한국어 화면 및 순수 Python 계산 함수
├── requirements.txt  # Streamlit 의존성
└── README.md         # 설치·실행·계산 설명
```

설치 후 생성되는 `.venv/`는 이 프로젝트 전용 Python 환경입니다. 별도 데이터베이스나 AI 서비스는 필요하지 않습니다.

## 4. 계산 방식

변수: 현재 금융자산 `A`, 매월 말 저축액 `P`, 목표기간(년) `Y`, 입력 연수익률(%) `R`, 목표금액 `T`.

```text
n = Y × 12
r = R / 100
i = (1 + r)^(1/12) − 1

현재 금융자산 미래가치 = A × (1 + i)^n
월 저축액 미래가치 = P × ((1 + i)^n − 1) / i
  단, R = 0이면 P × n
예상 금융자산 = 현재 금융자산 미래가치 + 월 저축액 미래가치
차액 = 예상 금융자산 − T
```

연수익률은 **연 실효수익률**로 해석합니다. 현재 자산은 기간 전체에 걸쳐 운용하고, 저축은 매월 말 납입합니다. 마지막 달 저축에는 수익이 붙지 않습니다. Python 표준 라이브러리 `math.log1p`와 `math.expm1`으로 위 수식을 구현하여 작은 수익률에서의 오차를 줄였습니다.

차액이 0 이상이면 단순 계산상 달성 가능, 음수이면 달성 어려움으로 표시합니다. 판정은 원 단위 표시 반올림 이전의 값으로 하되 부동소수점의 극미한 오차만 보정합니다. 달성 비율은 예상 금융자산/목표금액이며 확률이 아닙니다.

검산 예: 현재 자산 2,000만 원, 월 저축 100만 원, 5년, 수익률 0%이면 자산 미래가치 2,000만 원 + 저축 미래가치 6,000만 원 = 8,000만 원입니다. 목표가 1억 원이면 2,000만 원 부족입니다.

입력 범위: 나이 0~120세, 기간 1~50년, 수익률 -99~100%, 월 소득·저축 0~100억 원, 현재 자산·부채 0~1조 원, 목표 1원~1조 원. 이 범위는 테스트 입력 제한이며 수익률의 현실성을 의미하지 않습니다. 월 저축액이 월 소득보다 크면 검토 경고를 표시합니다.

## 모델의 한계와 인간 검토

- 세금, 물가, 수수료, 소득변화, 수익률 변동을 반영하지 않습니다.
- 현재 부채는 현재 순금융자산 표시용입니다. **미래 금융자산과 목표달성 판정에서 부채를 차감하지 않으며**, 부채 이자·상환도 계산하지 않습니다.
- 나이는 목표시점 나이 표시용, 월 소득은 저축액 점검용입니다. 소득을 자산에 추가하지 않습니다.
- 모든 금융자산을 동일 수익률로 운용하고 같은 금액을 계속 저축한다고 가정합니다. 생활비·비상자금·투자위험을 반영하지 않습니다.
- 실제 개인정보를 입력하지 마세요. 테스트 결과는 수익이나 실제 목표달성을 보장하지 않습니다. 사람이 가정과 부채 부담 등을 검토하고 최종 판단을 작성해야 합니다.

UI 구성과 실행 방식 참고: [Streamlit 공식 문서](https://docs.streamlit.io/develop/quick-reference/cheat-sheet).

## 5. 다른 사람에게 공유하기: 온라인 배포

`localhost` 또는 `127.0.0.1` 주소는 실행한 컴퓨터에서만 열립니다. 공개 링크를 만들려면 [Streamlit Community Cloud](https://share.streamlit.io/)에 배포합니다. 계정 로그인과 GitHub 연결이 필요합니다.

1. GitHub에 이 앱 전용 저장소를 만들고 `app.py`, `requirements.txt`, `README.md`를 저장소 최상위에 올립니다. `.venv`, `work`, 실제 고객 정보는 올리지 않습니다.
2. Streamlit Community Cloud에 로그인하고 GitHub 계정을 연결합니다.
3. 앱 생성 메뉴에서 해당 저장소와 파일이 있는 브랜치를 선택합니다. 메인 파일 경로는 `app.py`로 지정합니다.
4. 고급 설정에서 Python 3.12를 선택하고 배포합니다.
5. 실행 완료 후 앱 공유 설정을 확인하여 링크를 받은 사람이 볼 수 있게 설정합니다. 발급된 `https://….streamlit.app` 주소를 공유합니다.

기존 폴더 구조 그대로 저장소에 올렸다면 메인 파일 경로는 `outputs/app.py`입니다. `requirements.txt`는 `app.py`와 같은 폴더에 두세요. 배포 후에도 메모는 영구 저장되지 않습니다.

배포 확인: 로그인하지 않은 브라우저에서 공유 주소를 열어 입력·결과·메모 동작을 확인하세요. 기본 예제에서 연수익률을 0%로 바꾸면 예상 금융자산은 8,000만 원입니다.

공식 안내: [앱 배포](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [앱 공유](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app).
