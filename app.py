import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import physics as ph
from quiz_data import QUIZ, TAG_TO_PAGE

st.set_page_config(page_title="시간은 모두에게 똑같이 흐를까?", page_icon="⏱️", layout="centered")

PAGES = ["시작", "1. 속도와 시간", "2. 미시세계: 뮤온", "3. 중력과 GPS",
         "4. 양자역학의 시간", "5. 시간의 문제", "퀴즈", "탐구 과정·자료"]
st.session_state.setdefault("page", PAGES[0])


def go(page):
    st.session_state.page = page


def next_button(target, label="다음 단계로 →"):
    st.button(label, on_click=go, args=(target,), key=f"next_{target}")


def key_point(text):
    st.success(f"**한 줄 정리** · {text}")


# ---------------------------------------------------------------- 시작
def page_start():
    st.title("⏱️ 시간은 모두에게 똑같이 흐를까?")
    st.write("교과서에서 배운 *시간 지연*에서 출발해, 양자역학과 양자중력의 '시간의 문제'까지 따라가 보는 약 10분짜리 체험 앱입니다.")
    st.markdown("""
1. **속도**가 빠르면 시간이 어떻게 달라질까?
2. 일상에서는 안 보이는데, **미시세계**에서는 정말 보일까?
3. **중력**도 시간을 바꿀까?
4. **양자역학**은 시간을 어떻게 다룰까?
5. 시간까지 양자적으로 다루면 어떻게 될까?
""")
    st.info("각 단계마다 직접 슬라이더를 움직여 보고, 마지막에 퀴즈로 확인해요.")
    st.button("시작하기 →", on_click=go, args=(PAGES[1],), type="primary")


# ---------------------------------------------------------------- 1
def fmt_sec(x):
    return f"{x:.2e} 초"


def page_speed():
    st.header("1. 속도와 시간")
    st.write("움직이는 시계는 느리게 갑니다. 느려지는 정도는 γ(감마)로 정해져요.")
    st.latex(r"\gamma = \frac{1}{\sqrt{1 - v^2/c^2}}")
    beta = st.slider("속도 (빛의 속도 c의 몇 배?)", 0.0, 0.999, 0.6, 0.001)
    g = float(ph.gamma(beta))
    c1, c2 = st.columns(2)
    c1.metric("γ (시간 지연 배율)", f"{g:.3f}")
    c2.metric("그 우주선 안 1시간 = 지구 기준", f"{g:.2f} 시간")

    bs = np.linspace(0, 0.999, 400)
    df = pd.DataFrame({"β": bs, "γ": ph.gamma(bs)})
    line = alt.Chart(df).mark_line().encode(x=alt.X("β", title="속도 (c 단위)"), y=alt.Y("γ", title="γ"))
    dot = alt.Chart(pd.DataFrame({"β": [beta], "γ": [g]})).mark_point(size=120, filled=True, color="red").encode(x="β", y="γ")
    st.altair_chart(line + dot, use_container_width=True)

    st.subheader("그런데 왜 일상에서는 안 보일까?")
    things = {"걷는 사람": 1.4, "고속열차": 83, "제트기": 250, "국제우주정거장": 7660, "0.99c 뮤온": 0.99 * ph.C}
    rows = [{"대상": k, "속도 (m/s)": f"{v:,.1f}", "γ − 1": f"{float(ph.gamma_minus_one(v / ph.C)):.2e}",
             "1초 동안 뒤처지는 시간": fmt_sec(float(ph.clock_lag(v)))} for k, v in things.items()]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.caption("일상의 속도에서는 γ가 1과 거의 같아서 효과가 너무 작아요. 효과가 크게 나타나려면 빛에 가까운 속도가 필요합니다.")
    key_point("법칙이 안 통하는 게 아니라, 일상 속도에서는 효과가 너무 작아서 안 보인다.")
    with st.expander("더 알아보기: 계산 방법"):
        st.write("v가 매우 작을 때 γ−1 ≈ v²/(2c²)입니다. 제트기(250 m/s)는 약 3.5×10⁻¹³ 정도입니다.")
    next_button(PAGES[2])


# ---------------------------------------------------------------- 2
@st.cache_data
def muon_run(n, d, beta):
    return ph.simulate_muons(n, d, beta, False), ph.simulate_muons(n, d, beta, True)


def page_muon():
    st.header("2. 미시세계: 뮤온")
    st.write("뮤온은 우주선(cosmic ray)이 대기와 부딪혀 생기는 입자로, 평균 수명이 약 **2.2 μs**밖에 안 됩니다. 그런데 지표면에서 계속 검출돼요. 왜일까요?")
    c1, c2 = st.columns(2)
    beta = c1.slider("뮤온 속도 (c 단위)", 0.90, 0.999, 0.99, 0.001)
    dist = c2.slider("날아가는 거리 (m)", 500, 20000, 4000, 100)
    n = st.select_slider("시뮬레이션 뮤온 수", [1000, 5000, 10000, 20000], value=10000)
    no_dil, dil = muon_run(n, dist, beta)
    st.bar_chart(pd.DataFrame({"도달한 뮤온 수": [no_dil, dil]}, index=["시간 지연 무시", "시간 지연 적용"]))
    a, b = st.columns(2)
    a.metric("시간 지연 무시", f"{no_dil:,}개 ({no_dil / n:.1%})")
    b.metric("시간 지연 적용", f"{dil:,}개 ({dil / n:.1%})")
    g = float(ph.gamma(beta))
    st.caption(f"γ = {g:.2f} → 지상에서 본 뮤온의 평균 수명 ≈ {g * 2.197:.1f} μs, "
               f"평균 비행거리 ≈ {beta * ph.C * g * ph.MUON_TAU:,.0f} m (시간 지연 무시 시 {beta * ph.C * ph.MUON_TAU:,.0f} m)")
    key_point("빠르게 움직이는 뮤온의 시간은 지상에서 보면 느리게 가서, 더 오래 살고 더 멀리 온다.")
    with st.expander("더 알아보기: 시뮬레이션 방법"):
        st.write("뮤온마다 고유 수명을 지수분포로 뽑고, 지상 기준 비행거리 = β·c·γ·(고유 수명)이 목표 거리 이상이면 도달한 것으로 셉니다. "
                 "실제 실험 비교(Frisch & Smith 1963)는 원 논문의 값으로 확인하세요.")
    next_button(PAGES[3])


# ---------------------------------------------------------------- 3
def page_gravity():
    st.header("3. 중력과 GPS")
    st.write("일반상대성이론에 따르면 **중력이 강한 곳일수록 시계가 느리게** 갑니다.")
    name = st.selectbox("어느 천체 표면의 시계를 볼까요? (멀리 떨어진 곳과 비교)", list(ph.PRESETS))
    m, r = ph.PRESETS[name]
    rate = float(ph.static_clock_rate(m, r))
    lag_day = (1 - rate) * 86400
    c1, c2 = st.columns(2)
    c1.metric("시계 빠르기 (먼 곳 = 1)", f"{rate:.10f}")
    c2.metric("하루 동안 뒤처지는 시간", f"{lag_day:.3g} 초")
    st.caption(f"슈바르츠실트 반지름 {ph.schwarzschild_radius(m):.4g} m, 천체 반지름 {r:.4g} m")

    st.subheader("실제로 쓰이는 곳: GPS")
    alt_km = np.linspace(300, 40000, 200)
    off = ph.gps_clock_offsets(alt_km * 1e3 + ph.R_EARTH)
    df = pd.DataFrame({"고도 (km)": alt_km, "속도 효과 (μs/일)": off["sr_us"],
                       "중력 효과 (μs/일)": off["gr_us"], "합계 (μs/일)": off["net_us"]}).set_index("고도 (km)")
    st.line_chart(df)
    g = ph.gps_clock_offsets()
    a, b, c = st.columns(3)
    a.metric("속도 효과", f"{float(g['sr_us']):+.1f} μs/일")
    b.metric("중력 효과", f"{float(g['gr_us']):+.1f} μs/일")
    c.metric("합계 (GPS 고도 약 20,200 km)", f"{float(g['net_us']):+.1f} μs/일")
    st.write(f"보정하지 않으면 위치 오차가 하루에 약 **{float(g['range_error_km']):.0f} km** 쌓입니다.")
    key_point("속도는 시계를 느리게, 중력(높은 곳)은 빠르게 한다. GPS는 둘 다 보정해야 정확하다.")
    with st.expander("더 알아보기: 가정과 한계"):
        st.write("약한 중력장 근사를 쓰고 지구 자전·타원 궤도는 무시한 계산이에요. 정밀한 값은 Ashby(2003) 총설을 참고하세요.")
    next_button(PAGES[4])


# ---------------------------------------------------------------- 4
@st.cache_data
def packet_run(kind):
    x = ph.make_grid()
    V = ph.potential(x, kind)
    probs = ph.evolve(ph.gaussian_packet(x), x, V, steps=500 if kind != "free" else 400)
    return x, probs, V


def page_quantum():
    st.header("4. 양자역학의 시간")
    st.write("양자역학에서 입자는 파동함수 ψ로 표현되고, ψ가 시간에 따라 어떻게 변하는지는 **슈뢰딩거 방정식**이 알려줍니다.")
    st.latex(r"i\hbar \frac{\partial}{\partial t}\psi = \hat{H}\psi")
    names = {"free": "자유 공간", "harmonic": "용수철 같은 퍼텐셜", "barrier": "장벽 (터널링)"}
    kind = st.radio("환경 선택", list(names), format_func=names.get, horizontal=True)
    x, probs, V = packet_run(kind)
    i = st.slider("시간 진행", 0, len(probs) - 1, 0)
    ymax = float(probs.max()) * 1.1
    d = pd.DataFrame({"x": x, "확률밀도": probs[i]})
    chart = alt.Chart(d).mark_area(opacity=0.6).encode(
        x=alt.X("x", title="위치"), y=alt.Y("확률밀도", scale=alt.Scale(domain=[0, ymax])))
    if np.any(V):
        vs = V / V.max() * ymax * 0.8
        chart += alt.Chart(pd.DataFrame({"x": x, "V": vs})).mark_line(color="red").encode(x="x", y="V")
    st.altair_chart(chart, use_container_width=True)
    st.caption("파랑: 입자를 발견할 확률 분포, 빨강: 퍼텐셜(있을 때). 슬라이더가 '시간'입니다.")
    st.warning("방금 움직인 슬라이더(t)를 누가 정했나요? 방정식 **바깥에서** 우리가 정해 준 숫자예요. "
               "양자역학에서 시간은 위치와 달리 연산자가 아니라 그냥 매개변수입니다.")
    key_point("양자역학에서 시간은 방정식 바깥에서 주어지는 변수다. 상대성이론의 시간과는 다른 지위를 갖는다.")
    with st.expander("더 알아보기: 계산 방법"):
        st.write("ħ=m=1 단위에서 split-step 푸리에 방법으로 수치 계산합니다. 시간-에너지 불확정성도 위치-운동량과 성격이 다르다는 점이 알려져 있어요 (Busch 2002).")
    next_button(PAGES[5])


# ---------------------------------------------------------------- 5
def page_problem():
    st.header("5. 시간의 문제")
    st.write("일반상대성이론과 양자역학을 합치려는 양자중력에서는 기본 방정식(휠러–드위트 방정식)에 **시간 변수가 없습니다.**")
    st.latex(r"\hat{H}\,|\Psi\rangle = 0")
    st.write("그럼 우리가 느끼는 시간의 흐름은 어디서 나올까요? 한 가지 아이디어(Page–Wootters)는 *시계와 나머지의 관계*에서 시간이 나타난다는 것입니다. 아주 단순화한 장난감 모형으로 확인해 봐요.")
    c1, c2 = st.columns(2)
    n = c1.slider("시계 눈금 수", 4, 32, 16)
    w = c2.slider("큐비트 변화 속도 ω", 0.5, 3.0, 1.0, 0.1)
    out = ph.page_wootters_toy(n, w)
    df = pd.DataFrame({"시계 눈금으로 조건 건 값": out["cond_z"], "직접 푼 슈뢰딩거 해": out["expected_z"]},
                      index=np.round(out["times"], 2))
    df.index.name = "시계가 가리키는 시각"
    st.line_chart(df)
    a, b = st.columns(2)
    a.metric("시계를 무시하고 본 큐비트 ⟨σz⟩", f"{out['z_without_clock']:.3f}")
    b.metric("시계–큐비트 얽힘 (비트)", f"{out['entropy_bits']:.2f}")
    st.markdown("- **전체 상태는 하나로 고정**돼 있고 변하지 않아요.\n"
                "- 시계 눈금으로 조건을 걸면 큐비트가 **변해 가는 것처럼** 보여요 (두 선이 겹침).\n"
                "- 시계를 무시하면 변화가 사라져요 (왼쪽 값이 0 근처). 시간은 *관계*에서 나옵니다.")
    key_point("시간을 '원래 있는 것'이 아니라 '시계와의 상관관계에서 나타나는 것'으로 보는 관점이 있다. 아직 풀리지 않은 문제다.")
    st.caption("이 모형은 개념을 보여주기 위한 단순화입니다. 실제 양자중력의 시간 문제는 훨씬 복잡하고 미해결 상태예요 (Rovelli 2011, Anderson 2012).")
    next_button("퀴즈", "퀴즈 풀러 가기 →")


# ---------------------------------------------------------------- 퀴즈
def page_quiz():
    st.header("📝 퀴즈")
    rnd = st.session_state.setdefault("quiz_round", 0)
    result = st.session_state.get("quiz_result")
    if result is None:
        with st.form(f"quiz_form_{rnd}"):
            answers = []
            for i, q in enumerate(QUIZ):
                st.markdown(f"**Q{i + 1}. {q['question']}**")
                answers.append(st.radio("답", q["options"], index=None, key=f"q{rnd}_{i}", label_visibility="collapsed"))
            submitted = st.form_submit_button("제출하고 채점하기", type="primary")
        if submitted:
            st.session_state.quiz_result = answers
            st.rerun()
        return

    score, review = 0, set()
    for i, (q, a) in enumerate(zip(QUIZ, result)):
        ok = a == q["options"][q["answer"]]
        score += ok
        if not ok:
            review.add(q["tag"])
        with st.expander(f"{'✅' if ok else '❌'} Q{i + 1}. {q['question']}", expanded=not ok):
            st.write(f"내 답: {a or '(선택 안 함)'}")
            st.write(f"정답: **{q['options'][q['answer']]}**")
            st.info(q["explanation"])
    st.subheader(f"점수: {score} / {len(QUIZ)}")
    if review:
        st.write("다시 보면 좋은 단계: " + ", ".join(TAG_TO_PAGE[t] for t in sorted(review)))
    else:
        st.balloons()
    if st.button("다시 풀기"):
        st.session_state.quiz_round += 1
        st.session_state.quiz_result = None
        st.rerun()


# ---------------------------------------------------------------- 탐구 과정·자료
def page_about():
    st.header("탐구 과정·자료")
    st.markdown("""
**우리의 질문 흐름**  
교과서의 시간 지연 → 왜 일상에서 안 보이지? → 미시세계(뮤온) → 중력은? (GPS) → 양자역학의 시간 → 양자중력의 시간 문제

**참고 자료**
- Frisch & Smith (1963), *American Journal of Physics* 31 — 뮤온 시간 지연 측정
- Hafele & Keating (1972), *Science* 177 — 원자시계 비행 실험
- Ashby (2003), *Living Reviews in Relativity* 6 — GPS와 상대성이론
- Page & Wootters (1983), *Physical Review D* 27 — 얽힘과 시간
- Moreva et al. (2014), *Physical Review A* 89 — 얽힘에서 나타나는 시간의 실험적 예시
- Rovelli (2011), "Forget Time", *Foundations of Physics* 41
""")
    st.caption("이 앱의 코드는 GitHub에 공개되어 있습니다. (링크를 여기에 넣으세요)")


ROUTES = {PAGES[0]: page_start, PAGES[1]: page_speed, PAGES[2]: page_muon, PAGES[3]: page_gravity,
          PAGES[4]: page_quantum, PAGES[5]: page_problem, "퀴즈": page_quiz, "탐구 과정·자료": page_about}

st.sidebar.radio("단계 선택", PAGES, key="page")
ROUTES[st.session_state.page]()
