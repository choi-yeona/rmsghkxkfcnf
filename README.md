# ⏱️ 시간은 모두에게 똑같이 흐를까? — 시간 지연 탐구 앱

교과서의 **시간 지연**에서 출발해 뮤온 → 중력(GPS) → 양자역학의 시간 → 양자중력의 '시간의 문제'까지 따라가는 체험형 학습 앱과 코랩 노트북입니다.

## 구성
| 파일 | 설명 |
|---|---|
| `physics.py` | 모든 물리 계산 (γ, 뮤온 몬테카를로, 중력 시간 지연, GPS, 슈뢰딩거 시뮬레이션, Page–Wootters 장난감 모형) |
| `app.py` | Streamlit 앱 (개념 설명 → 슬라이더 체험 → 퀴즈) |
| `quiz_data.py` | 퀴즈 문제 (문제·보기·정답·해설을 여기서 수정) |
| `notebooks/time_dilation_colab.ipynb` | 코랩 탐구 노트북 (같은 `physics.py` 사용) |

## 실행 방법
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포 (Streamlit Community Cloud)
1. 이 폴더를 GitHub 저장소로 올린다.
2. https://share.streamlit.io 에서 저장소를 연결하고 Main file을 `app.py`로 지정한다.
3. 발급된 주소로 QR코드를 만들어 발표 슬라이드에 넣는다.

## 코랩에서 사용
노트북 첫 셀의 `REPO_URL`을 자신의 저장소 주소로 바꾸면 `physics.py`를 자동으로 불러옵니다.

## 모델의 가정과 한계
- GPS 계산: 약한 중력장 근사, 지구 자전·타원 궤도 무시
- 중력 시간 지연: 정지한 시계 기준 슈바르츠실트 해
- 슈뢰딩거: ħ = m = 1 단위의 1차원 모형
- Page–Wootters: 개념 설명을 위해 크게 단순화한 이산 모형 (실제 양자중력 문제의 해결이 아님)
- 실험값(뮤온 도달 개수 등)과의 비교는 원 논문의 수치로 확인할 것

## 참고문헌
Frisch & Smith (1963) · Hafele & Keating (1972) · Ashby (2003) · Page & Wootters (1983) · Moreva et al. (2014) · Rovelli (2011)
