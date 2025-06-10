import streamlit as st

st.set_page_config(page_title="고로 출선작업 계산기", layout="centered")
st.title("고로 출선작업 계산기 🔥")

# --- 출선구 설정 ---
st.header("① 출선구 설정")
lead_phi = st.number_input("선행 출선구 비트경 (Φ, mm)", min_value=30.0, value=45.0, step=1.0)
follow_phi = st.number_input("후행 출선구 비트경 (Φ, mm)", min_value=30.0, value=45.0, step=1.0)

# --- 출선 조건 입력 ---
st.header("② 출선 조건 입력")
tap_amount = st.number_input("1회 출선량 (ton)", min_value=0.0, value=1358.0, step=1.0)
wait_time = st.number_input("차기 출선까지 대기 시간 (분)", min_value=0.0, value=15.0, step=1.0)

# --- 현재 출선속도 입력 ---
st.header("③ 현재 출선속도 입력")
lead_current_speed = st.number_input("선행 출선속도 (ton/min)", min_value=0.0, value=8.0)
follow_current_speed = st.number_input("후행 출선속도 (ton/min)", min_value=0.0, value=8.0)

# --- K 계산 ---
calc_K_lead = lead_current_speed / (lead_phi ** 2) if lead_phi > 0 else 0
calc_K_follow = follow_current_speed / (follow_phi ** 2) if follow_phi > 0 else 0

st.markdown(f"📐 **선행 출선구 환산계수 K**: {calc_K_lead:.5f} ton/min·mm²")
with st.expander("🔍 계산 근거 보기 - 선행 K"):
    st.markdown("K = V / Φ²")
    st.markdown("선행 출선속도 / 선행 비트경²")

st.markdown(f"📐 **후행 출선구 환산계수 K**: {calc_K_follow:.5f} ton/min·mm²")
with st.expander("🔍 계산 근거 보기 - 후행 K"):
    st.markdown("K = V / Φ²")
    st.markdown("후행 출선속도 / 후행 비트경²")

# --- 출선속도 및 시간 예측 ---
lead_speed_est = calc_K_lead * lead_phi ** 2
follow_speed_est = calc_K_follow * follow_phi ** 2
dual_speed_est = lead_speed_est + follow_speed_est

lead_time_est = tap_amount / lead_speed_est if lead_speed_est > 0 else 0
follow_time_est = tap_amount / follow_speed_est if follow_speed_est > 0 else 0
dual_time_est = tap_amount / dual_speed_est if dual_speed_est > 0 else 0

# --- 결과 출력 ---
st.header("④ 예측 출선시간 결과")
st.write(f"● 선행 출선속도: {lead_speed_est:.2f} ton/min → 출선시간: {lead_time_est:.1f} 분")
with st.expander("🔍 계산 근거 보기 - 선행 출선시간"):
    st.markdown("출선속도 = K × Φ²")
    st.markdown("출선시간 = 출선량 / 출선속도")

st.write(f"● 후행 출선속도: {follow_speed_est:.2f} ton/min → 출선시간: {follow_time_est:.1f} 분")
with st.expander("🔍 계산 근거 보기 - 후행 출선시간"):
    st.markdown("출선속도 = K × Φ²")
    st.markdown("출선시간 = 출선량 / 출선속도")

st.success(f"▶ 2공 동시 출선 예상시간: {dual_time_est:.2f} 분 (출선량 {tap_amount:.0f} ton 기준)")
with st.expander("🔍 계산 근거 보기 - 2공 동시 출선"):
    st.markdown("총출선속도 = 선행 + 후행 출선속도")
    st.markdown("출선시간 = 출선량 / 총출선속도")

# --- 비트경 변화 시 시뮬레이션 ---
st.header("⑤ Φ 비트경 변화 시 출선시간 예측")
for phi in [43, 45, 48]:
    speed_lead = calc_K_lead * phi ** 2
    speed_follow = calc_K_follow * phi ** 2
    total_speed = speed_lead + speed_follow
    total_time = tap_amount / total_speed if total_speed > 0 else 0
    st.write(f"● Φ{phi} → 총 출선속도: {total_speed:.2f} ton/min → 출선시간: {total_time:.1f} 분")

# --- 고로 조업 입력 ---
st.header("⑥ 고로 조업 입력")
ore_coke_ratio = st.number_input("Ore/Coke 비율", min_value=0.0, step=0.01)
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
ore_charge = st.number_input("1회 Ore 장입량 (ton)", value=165.0)
coke_charge = st.number_input("1회 Coke 장입량 (ton)", value=33.0)
daily_charge = st.number_input("일일 Charge 수", value=126)
iron_speed = st.number_input("선철 생성속도 (ton/min)", value=9.0)
slag_ratio = st.number_input("출선비 (용선:슬래그)", value=2.25)
pcr = st.number_input("PCR (분탄 주입률, kg/T-P)", value=150)
carbon_rate = st.number_input("C.R (탄소 소비율, kg/T-P)", value=480)

# --- 자동 계산 결과 ---
daily_ore = ore_charge * daily_charge
daily_coke = coke_charge * daily_charge
auto_ratio = daily_ore / daily_coke if daily_coke else 0
hourly_charge = daily_charge / 24
daily_iron = iron_speed * 1440
daily_slag = daily_iron / slag_ratio if slag_ratio else 0
total_radiation = (daily_iron + daily_slag) * 0.05

# --- 노내 저선량 계산 ---
current_iron = iron_speed * 60  # 시간당 용선
current_slag = current_iron / slag_ratio if slag_ratio else 0
furnace_hold = (current_iron + current_slag) * 0.05

st.header("⑦ 자동 계산 결과")
st.markdown(f"📊 **Ore/Coke 비율**: {auto_ratio:.2f}")
with st.expander("🔍 계산 근거 보기 - Ore/Coke"):
    st.markdown("Ore/Coke = 일일 Ore 장입량 / 일일 Coke 장입량")

st.markdown(f"📊 **시간당 Charge 수**: {hourly_charge:.2f} 회/hr")
with st.expander("🔍 계산 근거 보기 - 시간당 Charge"):
    st.markdown("시간당 Charge 수 = 일일 Charge 수 / 24")

st.markdown(f"📊 **하루 출선량**: {daily_iron:.0f} ton")
with st.expander("🔍 계산 근거 보기 - 하루 출선량"):
    st.markdown("출선량 = 출선속도 × 1440 (분/일)")

st.markdown(f"📊 **슬래그량 추정**: {daily_slag:.0f} ton")
with st.expander("🔍 계산 근거 보기 - 슬래그"):
    st.markdown("슬래그량 = 출선량 / 출선비")

st.markdown(f"📊 **총 저선량 예측**: {total_radiation:.1f} ton/day")
with st.expander("🔍 계산 근거 보기 - 저선량"):
    st.markdown("저선량 = (용선 + 슬래그) × 0.05")

st.markdown(f"📦 **현재 노내 저선량(예측): {furnace_hold:.2f} ton**")
with st.expander("🔍 계산 근거 보기 - 현재 노내 저선량"):
    st.markdown("시간당 용선 + 슬래그 기준으로 5% 저선 추정")
    st.markdown("저선량 = (용선 + 슬래그) × 0.05")

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
with st.expander("🔍 계산 근거 보기 - 추천 비트경"):
    st.markdown("저선량 기준으로 비트경 선택")
    st.markdown("Φ43: 정상 운전 / Φ45: 중간 / Φ48: 과저선")
