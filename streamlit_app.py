import streamlit as st
import numpy as np

# 기본값
default_K = 0.0024

st.set_page_config(page_title="고로 출선작업 계산기", layout="centered")
st.title("고로 출선작업 계산기 🔥")

# --- 사이드바 자동계산 ---
st.sidebar.header("🔍 출선속도 환산계수(K) 계산기")
k_speed = st.sidebar.number_input("출선속도 V (ton/min)", min_value=0.0, step=0.1)
k_diameter = st.sidebar.number_input("출선구 비트경 D (mm)", min_value=1.0, step=1.0)
if k_diameter > 0:
    k_result = k_speed / (k_diameter ** 2)
    st.sidebar.write(f"→ 환산계수 K = {k_result:.5f} ton/min·mm²")

# --- 입력 ---
st.header("출선구 설정")
lead_phi = st.number_input("선행 출선구 비트경 (Φ, mm)", min_value=30.0, value=45.0, step=1.0)
follow_phi = st.number_input("후행 출선구 비트경 (Φ, mm)", min_value=30.0, value=45.0, step=1.0)
K = st.number_input("출선속도 환산계수 K", min_value=0.0001, value=default_K, step=0.0001)

st.header("출선 조건")
tap_amount = st.number_input("1회 출선량 (ton)", min_value=0.0, value=1358.0, step=1.0)
wait_time = st.number_input("차기 출선까지 대기 시간 (분)", min_value=0.0, value=15.0, step=1.0)

st.header("고로 조업 입력")
ore_coke_ratio = st.number_input("Ore/Coke 비율", min_value=0.0, step=0.01)
air_flow = st.number_input("풍량 (Nm³/min)", min_value=0.0)
air_pressure = st.number_input("풍압 (kg/cm²)", min_value=0.0)
furnace_pressure = st.number_input("노정압 (kg/cm²)", min_value=0.0)
furnace_temperature = st.number_input("용선온도 (°C)", min_value=0.0)
oxygen_injection = st.number_input("산소부화량 (Nm³/hr)", min_value=0.0)
moisture_content = st.number_input("조습량 (g/Nm³)", value=0.0)  # ← 수정됨
tfe_percent = st.number_input("T.Fe (%)", min_value=0.0)
daily_production = st.number_input("일일생산량 (ton)", min_value=0.0)
raw_material_granulation = st.number_input("원료 입도 (mm)", min_value=0.0)
furnace_lifetime = st.number_input("고로 수명 (년)", min_value=0, value=0, step=1)
ore_charge = st.number_input("1회 Ore 장입량 (ton)", value=165.0)
coke_charge = st.number_input("1회 Coke 장입량 (ton)", value=33.0)
daily_charge = st.number_input("일일 Charge 수", value=126)
iron_speed = st.number_input("선철 생성속도 (ton/min)", value=9.0)
slag_ratio = st.number_input("출선비 (용선:슬래그)", value=2.25)  # ← 수정됨

# --- 자동 계산 ---
daily_ore = ore_charge * daily_charge
daily_coke = coke_charge * daily_charge
auto_ratio = daily_ore / daily_coke if daily_coke else 0
hourly_charge = daily_charge / 24
daily_iron = iron_speed * 1440
daily_slag = daily_iron / slag_ratio if slag_ratio else 0
total_radiation = (daily_iron + daily_slag) * 0.05

st.sidebar.header("📊 자동 계산 항목")
st.sidebar.write(f"Ore/Coke 비율: {auto_ratio:.2f}")
st.sidebar.write(f"시간당 Charge 수: {hourly_charge:.2f} 회/hr")
st.sidebar.write(f"하루 출선량: {daily_iron:.0f} ton")
st.sidebar.write(f"슬래그량 추정: {daily_slag:.0f} ton")
st.sidebar.write(f"총 저선량 예측: {total_radiation:.1f} ton")

# --- 결과 계산 ---
def calc_speed(K, dia):
    return K * dia**2

lead_speed = calc_speed(K, lead_phi)
follow_speed = calc_speed(K, follow_phi)
dual_speed = lead_speed + follow_speed

lead_time = tap_amount / lead_speed if lead_speed > 0 else 0
follow_time = tap_amount / follow_speed if follow_speed > 0 else 0
dual_time = tap_amount / dual_speed if dual_speed > 0 else 0

# 추천 비트경
def recommend_phi(radiation):
    if radiation > 8:
        return "Φ48 (강제 배출 목적)"
    elif radiation > 5:
        return "Φ45 (유동성 확보)"
    else:
        return "Φ43 (정상 운전 유지)"

rec_phi = recommend_phi(total_radiation)

# --- 결과 출력 ---
st.header("📌 계산 결과")
st.write(f"■ 선행 출선속도: {lead_speed:.2f} ton/min → 출선시간: {lead_time:.1f} 분")
st.write(f"■ 후행 출선속도: {follow_speed:.2f} ton/min → 출선시간: {follow_time:.1f} 분")
st.success(f"▶ 2공 동시 1회 출선 예상시간: {dual_time:.2f} 분")
st.write(f"총 저선량 예측: {total_radiation:.1f} ton/day")
st.markdown(f"✅ **추천 비트경:** {rec_phi}")