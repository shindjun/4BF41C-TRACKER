import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- 기본값 및 현장 데이터 ---
avg_casts_per_day = 9
cast_duration = 270   # 각 출선 시간 (분)
switch_gap = 12       # 출선구 교대 대기시간 평균 (분)
default_tap_amount = 1358
default_wait_time = 15
default_K = 0.0024     # 출선속도 환산 계수(ton/min·mm²)
slag_ratio = 2.25     # 용선 대비 슬래그량 비
iron_speed = 9        # 선철 생성속도 기준 (ton/min)

st.set_page_config(page_title="고로 출선 작업 계산기", layout="centered")
st.title("고로 출선작업 계산기 🔥")

# K 계산기 섹션
st.sidebar.header("🔍 출선속도 환산계수(K) 계산기")
k_speed = st.sidebar.number_input("출선속도 V (ton/min)", min_value=0.0, step=0.1)
k_diameter = st.sidebar.number_input("출선구 비트경 D (mm)", min_value=1.0, step=1.0)
if k_diameter > 0:
    k_result = k_speed / (k_diameter ** 2)
    st.sidebar.write(f"→ 환산계수 K = {k_result:.5f} ton/min·mm²")

# 자동계산 기반 장입량
st.sidebar.header("🧮 자동 계산 지표")
daily_charges = 126
ore_per_charge = 165
coke_per_charge = 33
charge_per_hour = 3

ore_total = daily_charges * ore_per_charge
coke_total = daily_charges * coke_per_charge
ore_hourly = ore_per_charge * charge_per_hour
coke_hourly = coke_per_charge * charge_per_hour
ore_coke_ratio_auto = ore_total / coke_total if coke_total else 0
total_iron_generated = iron_speed * 60 * 24
slag_estimated = total_iron_generated / slag_ratio

st.sidebar.write(f"Ore 장입량 (일): {ore_total} ton")
st.sidebar.write(f"Coke 장입량 (일): {coke_total} ton")
st.sidebar.write(f"시간당 Ore: {ore_hourly} ton")
st.sidebar.write(f"시간당 Coke: {coke_hourly} ton")
st.sidebar.write(f"Ore/Coke 비율 (자동): {ore_coke_ratio_auto:.2f}")
st.sidebar.write(f"선철 생성량 (일): {total_iron_generated:.0f} ton")
st.sidebar.write(f"예상 슬래그량: {slag_estimated:.0f} ton")

# 실시간 출선속도 입력
st.sidebar.header("📡 실시간 출선속도 입력")
realtime_speed_lead = st.sidebar.number_input("선행 출선구 속도 (ton/min)", min_value=0.0, value=4.5, step=0.1)
realtime_speed_follow = st.sidebar.number_input("후행 출선구 속도 (ton/min)", min_value=0.0, value=4.2, step=0.1)
elapsed_time = st.sidebar.number_input("출선 경과 시간 (분)", min_value=0.0, value=120.0, step=5.0)

realtime_total_iron = (realtime_speed_lead + realtime_speed_follow) * elapsed_time
realtime_slag = realtime_total_iron / slag_ratio if slag_ratio > 0 else 0
realtime_total_radiation = realtime_total_iron + realtime_slag

st.subheader("📈 실시간 노내 저선량 예측")
st.write(f"▶ 경과 시간: {elapsed_time:.0f} 분")
st.write(f"용선 배출량: {realtime_total_iron:.1f} ton")
st.write(f"슬래그 배출량: {realtime_slag:.1f} ton")
st.success(f"노내 누적 저선량: {realtime_total_radiation:.1f} ton")

# 시계열 그래프
time_range = np.arange(0, elapsed_time + 1, 10)
iron_curve = (realtime_speed_lead + realtime_speed_follow) * time_range
slag_curve = iron_curve / slag_ratio
radiation_curve = iron_curve + slag_curve

fig_line, ax_line = plt.subplots()
ax_line.plot(time_range, iron_curve, label='용선량', linewidth=2)
ax_line.plot(time_range, slag_curve, label='슬래그량', linewidth=2)
ax_line.plot(time_range, radiation_curve, label='총 저선량', linestyle='--', linewidth=2)
ax_line.set_title("출선속도 기반 노내 누적 저선량")
ax_line.set_xlabel("경과 시간 (분)")
ax_line.set_ylabel("ton")
ax_line.legend()
ax_line.grid(True)
st.pyplot(fig_line)