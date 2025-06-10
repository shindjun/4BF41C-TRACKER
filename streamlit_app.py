import streamlit as st

st.set_page_config(page_title="고로 출선작업 계산기", layout="centered")
st.title("고로 출선작업 계산기 🔥")

# --- 출선 조건 입력 ---
st.header("① 출선 조건 입력")
tap_amount = st.number_input("1회 출선량 (ton)", min_value=0.0, value=1358.0, step=1.0)
wait_time = st.number_input("차기 출선까지 대기 시간 (분)", min_value=0.0, value=15.0, step=1.0)

# --- 출선구 설정 ---
st.header("② 출선구 설정")
lead_phi = st.number_input("선행 출선구 비트경 (Φ, mm)", min_value=30.0, value=45.0, step=1.0)
follow_phi = st.number_input("후행 출선구 비트경 (Φ, mm)", min_value=30.0, value=45.0, step=1.0)

# --- 현재 출선속도 입력 ---
st.header("③ 현재 출선속도 입력")
lead_current_speed = st.number_input("선행 출선속도 (ton/min)", min_value=0.0, value=8.0)
follow_current_speed = st.number_input("후행 출선속도 (ton/min)", min_value=0.0, value=8.0)

# --- 누락된 조업 입력 항목 추가 ---
st.header("④ 고로 장입 조건 입력")
ore_charge = st.number_input("1회 Ore 장입량 (ton)", value=165.0)
coke_charge = st.number_input("1회 Coke 장입량 (ton)", value=33.0)
daily_charge = st.number_input("일일 Charge 수", value=126)
ore_coke_ratio = ore_charge / coke_charge if coke_charge else 0

# --- 환산계수 계산 ---
calc_K_lead = lead_current_speed / (lead_phi ** 2) if lead_phi > 0 else 0
calc_K_follow = follow_current_speed / (follow_phi ** 2) if follow_phi > 0 else 0

st.markdown(f"📐 **선행 출선구 환산계수 K**: {calc_K_lead:.5f} ton/min·mm²")
st.markdown(f"📐 **후행 출선구 환산계수 K**: {calc_K_follow:.5f} ton/min·mm²")

# --- 출선속도/시간 계산 ---
lead_speed_est = calc_K_lead * lead_phi ** 2
follow_speed_est = calc_K_follow * follow_phi ** 2
dual_speed_est = lead_speed_est + follow_speed_est

lead_time_est = tap_amount / lead_speed_est if lead_speed_est > 0 else 0
follow_time_est = tap_amount / follow_speed_est if follow_speed_est > 0 else 0
dual_time_est = tap_amount / dual_speed_est if dual_speed_est > 0 else 0
ideal_delay_after_lead = max(3.0, (follow_time_est - lead_time_est) / 2) if follow_time_est > lead_time_est else 3.0

# --- 결과 출력 ---
st.header("⑤ 계산 결과 요약")
st.write(f"● 선행 출선속도: {lead_speed_est:.2f} ton/min → 출선시간: {lead_time_est:.1f} 분")
st.write(f"● 후행 출선속도: {follow_speed_est:.2f} ton/min → 출선시간: {follow_time_est:.1f} 분")
st.success(f"▶ 2공 동시 출선 예상시간: {dual_time_est:.2f} 분 (출선량 {tap_amount:.0f} ton 기준)")
st.info(f"⏱ **후행 출선은 선행 출선 종료 후 약 {ideal_delay_after_lead:.1f}분 후 시작이 적정합니다.**")

# --- 비트경 변화 시뮬레이션 ---
st.header("⑥ Φ 변화 시 출선속도 및 시간 예측")
for phi in [43, 45, 48]:
    speed = calc_K_lead * phi**2
    time = tap_amount / speed if speed > 0 else 0
    st.write(f"● Φ{phi} → 속도: {speed:.2f} ton/min → 출선시간: {time:.1f} 분")
