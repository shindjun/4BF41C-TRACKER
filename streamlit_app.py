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

st.set_page_config(page_title="고로 출선 작업 계산기", layout="centered")
st.title("고로 출선작업 계산기 🔥")

st.header("출선구별 비트경 입력")
tap_diameter_lead = st.number_input("선행 출선구 비트경 (mm)", min_value=30.0, max_value=80.0, value=45.0, step=1.0)
tap_diameter_follow = st.number_input("후행 출선구 비트경 (mm)", min_value=30.0, max_value=80.0, value=45.0, step=1.0)
K = st.number_input("출선속도 환산계수(K, ton/min·mm²)", min_value=0.0001, value=default_K, step=0.0001)

# 출선구별 출선속도 계산
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

# 계산 함수 정의
def predict_slag_amount():
    return daily_production * (1 - (tfe_percent / 100))

def predict_blast_furnace_output():
    return daily_production * ore_coke_ratio * 0.8

def calculate_blast_furnace_radiation(output):
    return output * 0.05

def calculate_slag_radiation(slag):
    return slag * 0.02

def calc_tap_time(amount, speed):
    return amount / speed if speed > 0 else 0

def calc_dual_taphole_time():
    total_output = tap_amount * avg_casts_per_day
    total_speed = tap_speed_lead + tap_speed_follow
    return total_output / total_speed if total_speed > 0 else 0

def predict_casting_time():
    k = 0.1
    return (air_flow + oxygen_injection + furnace_pressure + raw_material_granulation + furnace_lifetime) / (ore_coke_ratio + 1 + k)

def recommend_adjustments(casting_time):
    if casting_time > 300:
        return {
            "비트경 추천": "50mm 이상으로 확장 고려",
            "동시출선시간 조정": "30분 이상 확보 필요",
            "차기출선시간 조정": "대기시간을 10분 이내로 단축"
        }
    elif casting_time < 200:
        return {
            "비트경 추천": "현재 유지 가능 (예: 45mm)",
            "동시출선시간 조정": "기존 유지 또는 일부 단축 가능",
            "차기출선시간 조정": "기존 대기시간 유지"
        }
    else:
        return {
            "비트경 추천": "47~48mm로 미세 조정 고려",
            "동시출선시간 조정": "20~30분 확보",
            "차기출선시간 조정": "12분 수준 권장"
        }

if st.button("계산하기"):
    # 조업량 및 저선량 계산
    slag_amount = predict_slag_amount()
    output_amount = predict_blast_furnace_output()
    slag_radiation = calculate_slag_radiation(slag_amount)
    output_radiation = calculate_blast_furnace_radiation(output_amount)
    total_radiation = slag_radiation + output_radiation

    tap_time_lead = calc_tap_time(tap_amount, tap_speed_lead)
    tap_time_follow = calc_tap_time(tap_amount, tap_speed_follow)
    dual_time = calc_dual_taphole_time()
    casting_time = predict_casting_time()
    total_output = tap_amount * avg_casts_per_day

    adjustments = recommend_adjustments(casting_time)

    # 출선 순환 시뮬레이션
    start_time = 0
    taphole_labels = ['A', 'B'] * (avg_casts_per_day // 2) + ['A'] * (avg_casts_per_day % 2)
    timeline = []
    current_time = start_time
    for idx, taphole in enumerate(taphole_labels):
        timeline.append({
            "출선차수": idx + 1,
            "출선구": taphole,
            "출선시작": current_time,
            "출선종료": current_time + cast_duration
        })
        current_time += cast_duration + switch_gap
    df_timeline = pd.DataFrame(timeline)

    # 선행 출선구 예상 종료시점 계산
    first_lead = df_timeline[df_timeline['출선구'] == 'A'].iloc[0]
    lead_end_time = first_lead['출선종료']

    # 결과 출력
    st.header("예상 결과")
    st.write(f"■ 선행 출선구 속도: {tap_speed_lead:.2f} ton/min, 출선시간: {tap_time_lead:.1f} 분")
    st.write(f"■ 후행 출선구 속도: {tap_speed_follow:.2f} ton/min, 출선시간: {tap_time_follow:.1f} 분")
    st.success(f"2공 동시운전시 하루 소요시간: {dual_time:.1f} 분")
    st.write(f"▶ 선행 출선구 예상 종료시점: {lead_end_time:.1f} 분")
    st.write("---")
    st.write(f"용선 저선량: {output_radiation:.2f} ton")
    st.write(f"슬래그 저선량: {slag_radiation:.2f} ton")
    st.write(f"총 저선량: {total_radiation:.2f} ton")
    st.write(f"출선 작업 시간 예측(조업지수 기반): {casting_time:.2f} 분")
    st.write(f"하루 총 출선량: {total_output:.2f} ton")
    st.write(f"차기 출선까지 평균 대기시간: {wait_time:.0f} 분")

    st.subheader("🔧 조업지수 기반 출선 조건 추천")
    st.write(f"✅ 추천 비트경 조정: {adjustments['비트경 추천']}")
    st.write(f"✅ 동시 출선시간 조정: {adjustments['동시출선시간 조정']}")
    st.write(f"✅ 차기 출선시간 조정: {adjustments['차기출선시간 조정']}")

    # 출선 순환 타임라인 시각화
    st.subheader("출선 순환 시뮬레이션 (A↔B)")
    fig, ax = plt.subplots(figsize=(10, 4))
    for i, row in df_timeline.iterrows():
        ax.barh(row["출선구"], row["출선종료"] - row["출선시작"],
                left=row["출선시작"], height=0.4,
                color="tab:blue" if row["출선구"] == "A" else "tab:orange")
        ax.text(row["출선시작"] + 5, row["출선구"], f"{int(row['출선차수'])}", va='center', color="white", fontsize=8)
    ax.set_xlabel("시간 (분)")
    ax.set_title("고로 출선 순환 시뮬레이션 (A↔B)")
    ax.set_yticks(['A', 'B'])
    ax.set_xlim(0, df_timeline["출선종료"].max() + 30)
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    st.pyplot(fig)
    st.dataframe(df_timeline)