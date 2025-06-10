import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 기본값 및 현장 데이터 ---
avg_casts_per_day = 9
default_tap_amount = 1358
default_wait_time = 15
default_K = 0.0024   # 출선속도 환산 계수(ton/min·mm²)

st.set_page_config(page_title="고로 출선 작업 계산기", layout="centered")
st.title("고로 출선작업 계산기 🔥")

st.header("출선구별 비트경 입력")
tap_diameter_lead = st.number_input("선행 출선구 비트경 (mm)", min_value=30.0, max_value=80.0, value=45.0, step=1.0)
tap_diameter_follow = st.number_input("후행 출선구 비트경 (mm)", min_value=30.0, max_value=80.0, value=45.0, step=1.0)
K = st.number_input("출선속도 환산계수(K, ton/min·mm²)", min_value=0.0001, value=default_K, step=0.0001)

tap_speed_lead = K * tap_diameter_lead ** 2
tap_speed_follow = K * tap_diameter_follow ** 2

tap_amount = st.number_input("1회 출선시 배출량 (ton)", min_value=0.0, value=float(default_tap_amount), step=1.0)
wait_time = st.number_input("차기 출선까지 대기 시간 (min)", min_value=0.0, value=float(default_wait_time), step=1.0)

st.header("고로 조업 입력 항목")
ore_coke_ratio = st.number_input("Ore/Coke 비율", min_value=0.0, step=0.01)
air_flow = st.number_input("풍량 (Nm³/min)", min_value=0.0)
air_pressure = st.number_input("풍압 (kg/cm²)", min_value=0.0)
furnace_pressure = st.number_input("노정압 (kg/cm²)", min_value=0.0)
furnace_temperature = st.number_input("용선온도 (°C)", min_value=0.0)
oxygen_injection = st.number_input("산소부화량 (Nm³/hr)", min_value=0.0)
moisture_content = st.number_input("조습량 (g/Nm²)", min_value=0.0)
tfe_percent = st.number_input("T.Fe (%)", min_value=0.0)
daily_production = st.number_input("일일생산량 (ton)", min_value=0.0)
raw_material_granulation = st.number_input("원료 입도 (mm)", min_value=0.0)
furnace_lifetime = st.number_input("고로 수명 (년)", min_value=0, value=0, step=1)

# 계산 공식
def predict_slag_amount():
    return daily_production * (1 - (tfe_percent / 100))

def predict_blast_furnace_output():
    return daily_production * ore_coke_ratio * 0.8

def calculate_blast_furnace_radiation(blast_furnace_output):
    return blast_furnace_output * 0.05

def calculate_slag_radiation(slag_amount):
    return slag_amount * 0.02

def calc_tap_time(amount, speed):
    return amount / speed if speed > 0 else 0

def calc_dual_taphole_time():
    total_output = tap_amount * avg_casts_per_day
    total_speed = tap_speed_lead + tap_speed_follow
    return total_output / total_speed if total_speed > 0 else 0

def predict_casting_time():
    k = 0.1
    return (air_flow + oxygen_injection + furnace_pressure + raw_material_granulation + furnace_lifetime) / (ore_coke_ratio + 1 + k)

# 실행
if st.button("계산하기"):
    slag_amount = predict_slag_amount()
    blast_furnace_output = predict_blast_furnace_output()
    slag_radiation = calculate_slag_radiation(slag_amount)
    blast_furnace_radiation = calculate_blast_furnace_radiation(blast_furnace_output)
    total_radiation = slag_radiation + blast_furnace_radiation

    tap_time_lead = calc_tap_time(tap_amount, tap_speed_lead)
    tap_time_follow = calc_tap_time(tap_amount, tap_speed_follow)
    dual_taphole_time = calc_dual_taphole_time()
    casting_time = predict_casting_time()
    total_tap_output = tap_amount * avg_casts_per_day

    st.header("예상 결과")
    st.write(f"■ 선행 출선구(비트경 {tap_diameter_lead:.0f}mm): 출선속도 {tap_speed_lead:.2f} ton/min, 1회 출선시간 {tap_time_lead:.1f} 분")
    st.write(f"■ 후행 출선구(비트경 {tap_diameter_follow:.0f}mm): 출선속도 {tap_speed_follow:.2f} ton/min, 1회 출선시간 {tap_time_follow:.1f} 분")
    st.success(f"2개 출선구 동시 사용시 1일 예상 소요시간: {dual_taphole_time:.1f} 분")

    st.write("---")
    st.write(f"용선 저선량: {blast_furnace_radiation:.2f} ton")
    st.write(f"슬래그 저선량: {slag_radiation:.2f} ton")
    st.write(f"노내 예상 총 저선량: {total_radiation:.2f} ton")
    st.write(f"출선 작업 시간 예측(조업지수참고): {casting_time:.2f} 분")
    st.write(f"하루 예상 총 출선량: {total_tap_output:.2f} ton")
    st.write(f"차기 출선까지 평균 대기시간: {wait_time:.0f} 분")