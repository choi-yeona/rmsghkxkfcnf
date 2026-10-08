"""시간 지연 탐구 - 물리 계산 모듈 (Streamlit 앱과 Colab 노트북이 함께 사용)"""
import numpy as np

C = 299_792_458.0            # 광속 (m/s)
G = 6.67430e-11              # 중력상수
GM_EARTH = 3.986004418e14    # 지구 GM
R_EARTH = 6.371e6            # 지구 반지름 (m)
GPS_ORBIT_RADIUS = 2.6561e7  # GPS 궤도 반지름 (m)
MUON_TAU = 2.1969811e-6      # 뮤온 고유 수명 (s)

# ---------- 1. 특수상대성이론 ----------
def gamma(beta):
    beta = np.asarray(beta, dtype=float)
    return 1.0 / np.sqrt(1.0 - beta**2)

def gamma_minus_one(beta):
    """γ-1을 작은 속도에서도 정확히 계산 (일상 속도에서 γ-1은 매우 작다)"""
    beta = np.asarray(beta, dtype=float)
    root = np.sqrt(1.0 - beta**2)
    return beta**2 / (root * (1.0 + root))

def clock_lag(v_ms, duration_s=1.0):
    """속도 v로 움직인 시계가 정지한 관측자 시계보다 뒤처지는 시간 t(1-1/γ)"""
    gm1 = gamma_minus_one(np.asarray(v_ms, dtype=float) / C)
    return duration_s * gm1 / (1.0 + gm1)

# ---------- 2. 뮤온 ----------
def muon_survival_fraction(distance_m, beta, dilation=True):
    g = float(gamma(beta)) if dilation else 1.0
    return float(np.exp(-distance_m / (beta * C * g * MUON_TAU)))

def simulate_muons(n, distance_m, beta, dilation=True, seed=0):
    """몬테카를로: 뮤온 n개 중 distance_m 를 날아 도달하는 개수"""
    rng = np.random.default_rng(seed)
    g = float(gamma(beta)) if dilation else 1.0
    proper_lifetimes = rng.exponential(MUON_TAU, n)
    travel = beta * C * g * proper_lifetimes   # 지상 관측자 기준 비행 거리
    return int(np.sum(travel >= distance_m))

# ---------- 3. 중력 시간 지연 ----------
PRESETS = {  # 이름: (질량 kg, 반지름 m)
    "지구 표면": (5.972e24, 6.371e6),
    "태양 표면": (1.989e30, 6.957e8),
    "백색왜성 표면": (1.989e30, 7.0e6),
    "중성자별 표면": (2.784e30, 1.2e4),
}

def schwarzschild_radius(mass_kg):
    return 2 * G * mass_kg / C**2

def static_clock_rate(mass_kg, radius_m):
    """먼 곳 관측자 시간 대비 정지한 시계의 빠르기 dτ/dt = sqrt(1 - rs/r)"""
    return np.sqrt(1.0 - schwarzschild_radius(mass_kg) / radius_m)

def gps_clock_offsets(orbit_radius=GPS_ORBIT_RADIUS, ground_radius=R_EARTH, day=86400.0):
    """위성 시계가 지상 시계보다 하루에 얼마나 어긋나는지 (약한 중력장 근사, 지구 자전 무시)"""
    orbit_radius = np.asarray(orbit_radius, dtype=float)
    v = np.sqrt(GM_EARTH / orbit_radius)
    sr = -(v**2) / (2 * C**2) * day
    gr = GM_EARTH / C**2 * (1 / ground_radius - 1 / orbit_radius) * day
    return {"v": v, "sr_us": sr * 1e6, "gr_us": gr * 1e6,
            "net_us": (sr + gr) * 1e6, "range_error_km": np.abs(sr + gr) * C / 1e3}

# ---------- 4. 슈뢰딩거 방정식 (ħ = m = 1) ----------
def make_grid(n=1024, length=100.0):
    return np.linspace(-length / 2, length / 2, n, endpoint=False)

def gaussian_packet(x, x0=-15.0, k0=2.0, sigma=1.5):
    psi = np.exp(-((x - x0) ** 2) / (4 * sigma**2)) * np.exp(1j * k0 * x)
    return psi / np.sqrt(np.sum(np.abs(psi) ** 2) * (x[1] - x[0]))

def potential(x, kind="free"):
    if kind == "harmonic":
        return 0.5 * 0.15**2 * x**2
    if kind == "barrier":
        return np.where(np.abs(x) < 1.0, 3.0, 0.0)
    return np.zeros_like(x)

def evolve(psi0, x, V, dt=0.05, steps=400, every=8):
    """split-step Fourier 방법. 반환: |ψ|² 프레임 배열 (프레임 수, 격자 수)"""
    k = 2 * np.pi * np.fft.fftfreq(len(x), d=x[1] - x[0])
    half_v = np.exp(-0.5j * V * dt)
    kin = np.exp(-0.5j * k**2 * dt)
    psi, frames = psi0.astype(complex), [np.abs(psi0) ** 2]
    for s in range(1, steps + 1):
        psi = half_v * psi
        psi = np.fft.ifft(kin * np.fft.fft(psi))
        psi = half_v * psi
        if s % every == 0:
            frames.append(np.abs(psi) ** 2)
    return np.array(frames)

# ---------- 5. 시간의 문제: Page-Wootters 장난감 모형 ----------
def page_wootters_toy(n_clock=16, omega=1.0, dt=None):
    """시계 n_clock 눈금 + 큐비트 1개의 '역사 상태' 모형 (단순화된 교육용 모형).
    전체 상태는 하나로 고정돼 있지만, 시계 눈금 k로 조건을 걸면 큐비트가 시간에 따라 변하는 것처럼 보인다."""
    if dt is None:
        dt = 2 * np.pi / (omega * n_clock)       # 한 주기를 시계 눈금으로 나눔
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    evals, evecs = np.linalg.eigh(0.5 * omega * sx)
    U = lambda t: evecs @ np.diag(np.exp(-1j * evals * t)) @ evecs.conj().T
    psi0 = np.array([1, 0], dtype=complex)
    times = np.arange(n_clock) * dt
    branches = np.array([U(t) @ psi0 for t in times])           # (n_clock, 2)
    cond_z = np.array([np.real(np.vdot(b, sz @ b)) for b in branches])
    rho_s = sum(np.outer(b, b.conj()) for b in branches) / n_clock   # 시계를 무시한 큐비트
    rho_c = branches @ branches.conj().T / n_clock                   # 시계의 축소 상태
    p = np.linalg.eigvalsh(rho_c); p = p[p > 1e-12]
    return {"times": times, "cond_z": cond_z, "expected_z": np.cos(omega * times),
            "z_without_clock": float(np.real(np.trace(rho_s @ sz))),
            "entropy_bits": float(-np.sum(p * np.log2(p)))}
