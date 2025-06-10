import streamlit as st

st.set_page_config(page_title="고로 출선작업 계산기", layout="centered")
st.title("고로 출선작업 계산기 🔥")

# --- ① 출선구 설정 ---
st.header("① 출선구 설정")
lead_phi = st.number_input("선행 출선구 비트경 (Φ, mm)", min_value=30.0, value=45.0, step=1.0)
follow_phi = st.number_input("후행 출선구 비트경 (Φ, mm)", min_value=30.0, value=45.0, step=1.0)

# --- ② 출선 조건 입력 ---
st.header("② 출선 조건 입력")
tap_amount = st.number_input("1회 출선량 (ton)", min_value=0.0, value=1358.0, step=1.0)
wait_time = st.number_input("차기 출선까지 대기 시간 (분)", min_value=0.0, value=15.0, step=1.0)

# --- ③ 현재 출선속도 입력 ---
st.header("③ 현재 출선속도 입력")
lead_current_speed = st.number_input("선행 출선속도 (ton/min)", min_value=0.0, value=8.0)
follow_current_speed = st.number_input("후행 출선속도 (ton/min)", min_value=0.0, value=8.0)

# --- ④ K 계산 ---
calc_K_lead = lead_current_speed / (lead_phi ** 2) if lead_phi > 0 else 0
calc_K_follow = follow_current_speed / (follow_phi ** 2) if follow_phi > 0 else 0

st.markdown(f"📐 **선행 출선구 환산계수 K**: {calc_K_lead:.5f} ton/min·mm²")
st.markdown(f"📐 **후행 출선구 환산계수 K**: {calc_K_follow:.5f} ton/min·mm²")

# --- ⑤ 출선속도 및 시간 예측 ---
lead_speed_est = calc_K_lead * lead_phi ** 2
follow_speed_est = calc_K_follow * follow_phi ** 2
dual_speed_est = lead_speed_est + follow_speed_est

lead_time_est = tap_amount / lead_speed_est if lead_speed_est > 0 else 0
follow_time_est = tap_amount / follow_speed_est if follow_speed_est > 0 else 0
dual_time_est = tap_amount / dual_speed_est if dual_speed_est > 0 else 0

# --- ⑤-1 적정 출선 전략 계산 ---
ideal_delay_after_lead = max(3.0, (follow_time_est - lead_time_est) / 2) if follow_time_est > lead_time_est else 3.0

# --- ⑤ 결과 출력 ---
st.header("⑤ 예측 출선시간 결과")
st.write(f"● 선행 출선속도: {lead_speed_est:.2f} ton/min → 출선시간: {lead_time_est:.1f} 분")
st.write(f"● 후행 출선속도: {follow_speed_est:.2f} ton/min → 출선시간: {follow_time_est:.1f} 분")
st.success(f"▶ 2공 동시 출선 예상시간: {dual_time_est:.2f} 분 (출선량 {tap_amount:.0f} ton 기준)")
st.info(f"⏱ **후행 출선은 선행 출선 종료 후 약 {ideal_delay_after_lead:.1f}분 후 시작하는 것이 적정합니다.**")

# --- ⑥ 비트경별 출선시간 시뮬레이션 ---
st.header("⑥ Φ 비트경 변화 시 출선시간 예측")
for phi in [43, 45, 48]:
    speed_lead = calc_K_lead * phi ** 2
    speed_follow = calc_K_follow * phi ** 2
    total_speed = speed_lead + speed_follow
    total_time = tap_amount / total_speed if total_speed > 0 else 0
    st.write(f"● Φ{phi} → 총 출선속도: {total_speed:.2f} ton/min → 출선시간: {total_time:.1f} 분")

# --- ⑦ 고로 조업 입력 ---
st.header("⑦ 고로 조업 입력")
ore_charge = st.number_input("1회 Ore 장입량 (ton)", value=165.0)
coke_charge = st.number_input("1회 Coke 장입량 (ton)", value=33.0)
daily_charge = st.number_input("일일 Charge 수", value=126)
ore_coke_ratio = ore_charge / coke_charge if coke_charge else 0

air_flow = st.number_input("풍량 (Nm³/min)", min_value=0.0)
air_pressure = st.number_input("풍압 (kg/cm²)", min_value=0.0)
furnace_pressure = st.number_input("노정압 (kg/cm²)", min_value=0.0)
furnace_temperature = st.number_input("용선온도 (°C)", min_value=0.0)
oxygen_injection = st.number_input("산소부화량 (Nm³/hr)", min_value=0.0)
moisture_content = st.number_input("조습량 (g/Nm³)", value=0.0)
tfe_percent = st.number_input("T.Fe (%)", min_value=0.0)
daily_production = st.number_input("일일생산량 (ton)", min_value=0.0)
raw_material_granulation = st.number_input("원료 입도 (mm)", min_value=0.0)
furnace_lifetime = st.number_input("고로 수명 (년)", min_value=0, value=0, step=1)
iron_speed = st.number_input("선철 생성속도 (ton/min)", value=9.0)
slag_ratio = st.number_input("출선비 (용선:슬래그)", value=2.25)

# --- ⑦-1 고로 세부 조업지표 입력 ---
st.header("⑦-1 고로 세부 조업지표 입력")
planned_charge = st.number_input("계획 Charge 수 (회/일)", value=130)
current_charge = st.number_input("현재 Charge 수 (회)", value=60)
pcr = st.number_input("PCR (kg/ton)", value=150)
reduction_ratio = st.number_input("환원도 R.R (FeO/Fe)", value=0.85)
carbon_rate = st.number_input("C.R (kgC/ton)", value=480)
iron_output_rate = st.number_input("용선 생산속도 (ton/min)", value=9.0)
total_output_rate = st.number_input("슬래그 포함 생산속도 (ton/min)", value=11.2)

# --- ⑧ 자동 계산 결과 ---
daily_ore = ore_charge * daily_charge
daily_coke = coke_charge * daily_charge
hourly_charge = daily_charge / 24
daily_iron = iron_speed * 1440
daily_slag = daily_iron / slag_ratio if slag_ratio else 0
total_radiation = (daily_iron + daily_slag) * 0.05

st.header("⑧ 자동 계산 결과")
st.markdown(f"📊 **Ore/Coke 비율**: {ore_coke_ratio:.2f}")
st.markdown(f"📊 **시간당 Charge 수**: {hourly_charge:.2f} 회/hr")
st.markdown(f"📊 **하루 출선량**: {daily_iron:.0f} ton")
st.markdown(f"📊 **슬래그량 추정**: {daily_slag:.0f} ton")
st.markdown(f"📊 **현재 노내 저선량 예측**: {total_radiation:.1f} ton/day")

# --- ⑨ 장입 + 환원제비 기반 출선 예측 ---
st.header("⑨ 장입 + 환원제비 기반 출선 예측")

def estimate_recovery_rate(ratio):
    if ratio < 4.0:
        return 0.93
    elif ratio < 5.0:
        return 0.90
    elif ratio < 6.0:
        return 0.87
    else:
        return 0.83

recovery_rate = estimate_recovery_rate(ore_coke_ratio)
# 환원도 반영 보정
if reduction_ratio > 0:
    recovery_rate *= (1 + (1 - reduction_ratio))

estimated_iron = ore_charge * recovery_rate
predicted_speed = calc_K_lead * lead_phi ** 2
predicted_tap_time = estimated_iron / predicted_speed if predicted_speed > 0 else 0

# 누적 생산량 및 잔류량
real_time_iron = iron_output_rate * current_charge * (ore_charge / planned_charge)
real_time_slag = real_time_iron / slag_ratio if slag_ratio else 0
real_time_total_output = real_time_iron + real_time_slag
real_time_residual = real_time_total_output * 0.05

st.markdown(f"🧮 ORE/COKE 비율: **{ore_coke_ratio:.2f}**")
st.markdown(f"📈 회수율 추정: **{recovery_rate*100:.1f}%**")
st.markdown(f"📦 예상 출선량: **{estimated_iron:.1f} ton**")
st.markdown(f"⏱ 예상 출선시간(선행 기준): **{predicted_tap_time:.1f} 분**")
st.markdown(f"📦 누적 용선 생산량(현재 Charge 기준): **{real_time_iron:.1f} ton**")
st.markdown(f"📦 누적 슬래그 포함 생산량: **{real_time_total_output:.1f} ton**")
st.markdown(f"📦 현재 노내 잔류량(5%): **{real_time_residual:.1f} ton**")

# --- 추천 비트경 ---
def recommend_phi(radiation):
    if radiation > 8:
        return "Φ48 (강제 배출 목적)"
    elif radiation > 5:
        return "Φ45 (유동성 확보)"
    else:
        return "Φ43 (정상 운전 유지)"

rec_phi = recommend_phi(total_radiation)
st.markdown(f"✅ **추천 비트경:** {rec_phi}")
