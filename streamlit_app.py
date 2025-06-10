import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 기본 설정
st.set_page_config(page_title="고로 출선 및 저선량 계산기", layout="centered")
st.title("⛏ 고로 출선 + 누적 저선량 시뮬레이션")

# --- 사이드바 입력 ---
st.sidebar.header("입력값 설정")
iron_rate = st.sidebar.number_input("선철 생성속도 (ton/min)", min_value=0.1, value=9.0, step=0.1)
tap_ratio = st.sidebar.number_input("출선비 (용선/슬래그)", min_value=0.1, value=2.25, step=0.05)
reduction_ratio = st.sidebar.number_input("환원제비 (Ore/Coke)", min_value=0.1, value=5.0, step=0.1)
time_interval = st.sidebar.slider("시간 간격 (분)", min_value=10, max_value=120, value=60, step=10)
total_time = st.sidebar.slider("총 시뮬레이션 시간 (분)", min_value=60, max_value=1440, value=1440, step=60)

# 출선 조건
tap_amount = st.sidebar.number_input("1회 출선량 (ton)", min_value=100.0, value=1358.0, step=10.0)
cast_duration = st.sidebar.number_input("1회 출선시간 (분)", min_value=60, value=270, step=10)
switch_gap = st.sidebar.number_input("출선구 교대 대기시간 (분)", min_value=5, value=12, step=1)
avg_casts_per_day = st.sidebar.number_input("하루 출선 횟수", min_value=1, value=9, step=1)

# 비트경 및 출선속도 계산
st.sidebar.header("비트경 기반 출선속도 계산")
k_diameter = st.sidebar.number_input("출선구 비트경 D (파이, mm)", min_value=10.0, value=45.0, step=1.0)
k_value = st.sidebar.number_input("출선속도 환산계수 K (ton/min·mm²)", min_value=0.0001, value=0.0024, step=0.0001)
tap_speed = k_value * k_diameter ** 2
st.sidebar.write(f"💡 계산된 출선속도: {tap_speed:.2f} ton/min")

# 조업 조건
st.sidebar.header("조업 입력 항목")
air_flow = st.sidebar.number_input("풍량 (Nm³/min)", min_value=0.0)
furnace_pressure = st.sidebar.number_input("노정압 (kg/cm²)", min_value=0.0)
oxygen_injection = st.sidebar.number_input("산소부화량 (Nm³/hr)", min_value=0.0)
raw_material_granulation = st.sidebar.number_input("원료 입도 (mm)", min_value=0.0)
furnace_lifetime = st.sidebar.number_input("고로 수명 (년)", min_value=0, step=1)

# 계산 버튼
if st.button("📊 계산하기"):

    # 조업지수 기반 추천 함수
    def recommend_adjustments():
        score = (air_flow + oxygen_injection + furnace_pressure + raw_material_granulation + furnace_lifetime) / (reduction_ratio + 1)
        if score > 500:
            return "⛏ 고온조업 유지, 출선 대기시간 단축 권장", "⚠️ 누적 저선량 위험 증가"
        elif score < 200:
            return "⚙️ 비트경 축소 또는 교대시간 연장 검토", "✅ 안정적 조업 상태"
        else:
            return "🛠 조업 조건 양호. 현상 유지 권장", "⚠️ 슬래그 적체 점검 필요"

    recommendation, warning = recommend_adjustments()

    # 누적 저선량 계산
    minutes = np.arange(0, total_time + 1, time_interval)
    cumulative_iron = iron_rate * minutes
    cumulative_slag = cumulative_iron / tap_ratio
    cumulative_total = cumulative_iron + cumulative_slag
    df_acc = pd.DataFrame({
        "시간(분)": minutes,
        "누적 용선량 (ton)": cumulative_iron,
        "누적 슬래그량 (ton)": cumulative_slag,
        "총 누적 저선량 (ton)": cumulative_total
    })

    # 출선 순환 시뮬레이션
    taphole_labels = ['A', 'B'] * (avg_casts_per_day // 2) + ['A'] * (avg_casts_per_day % 2)
    timeline = []
    current_time = 0
    for idx, taphole in enumerate(taphole_labels):
        timeline.append({
            "출선차수": idx + 1,
            "출선구": taphole,
            "출선시작": current_time,
            "출선종료": current_time + cast_duration
        })
        current_time += cast_duration + switch_gap
    df_timeline = pd.DataFrame(timeline)

    # 결과 출력
    st.subheader("📋 누적 저선량 시뮬레이션 결과")
    st.dataframe(df_acc, use_container_width=True)

    st.subheader("📈 시간대별 누적 용선/슬래그/저선량")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(minutes, cumulative_iron, label="용선 누적량 (ton)", linewidth=2)
    ax.plot(minutes, cumulative_slag, label="슬래그 누적량 (ton)", linewidth=2)
    ax.plot(minutes, cumulative_total, label="총 저선량 (ton)", linestyle='--', linewidth=2)
    ax.set_xlabel("시간 (분)")
    ax.set_ylabel("누적량 (ton)")
    ax.set_title("시간대별 누적 저선량 추이")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)

    st.subheader("📊 출선 순환 타임라인")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    for i, row in df_timeline.iterrows():
        ax2.barh(row["출선구"], row["출선종료"] - row["출선시작"],
                 left=row["출선시작"], height=0.4,
                 color="tab:blue" if row["출선구"] == "A" else "tab:orange")
        ax2.text(row["출선시작"] + 5, row["출선구"], f"{int(row['출선차수'])}", va='center', color="white", fontsize=8)
    ax2.set_xlabel("시간 (분)")
    ax2.set_title("고로 출선 순환 시뮬레이션 (A↔B)")
    ax2.set_yticks(['A', 'B'])
    ax2.set_xlim(0, df_timeline["출선종료"].max() + 30)
    ax2.grid(True, axis='x', linestyle='--', alpha=0.7)
    st.pyplot(fig2)
    st.dataframe(df_timeline)

    # 조업 조건 추천
    st.subheader("📌 조업 조건 추천 및 누적 저선 경보")
    st.success(recommendation)
    st.warning(warning)
