import streamlit as st

# ----------- 기본 현장 데이터 -----------
num_tapholes = 4               # 출선구 개수
active_tapholes = 2            # 상시 사용 출선구
avg_casts_per_day = 9          # 하루 평균 출선 횟수
default_tap_diameter = 45      # 출선 비트경 (mm)
default_tap_time = 274         # 1개 출선구 평균 출선시간 (min)
default_tap_speed = 4.85       # 출선 속도 (ton/min)
default_tap_amount = 1358      # 1회 출선시 배출량 (ton)
default_wait_time = 15         # 차기 출선 대기시간 (min)

st.title("고로 출선작업 고급 계산기 (현장 프로파일 반영)")
st.markdown(f"""
- 출선구 개수: **{num_tapholes}개**
- 상시 사용 출선구: **{active_tapholes}개**
- 출선 비트경: **{default_tap_diameter} mm**
- 평균 출선 시간(1개 출선구): **{default_tap_time}분**
- 출선 속도: **{default_tap_speed} ton/min**
- 1회 출선시 평균 배출량: **{default_tap_amount} ton**
- 하루 평균 출선횟수: **{avg_casts_per_day}회**
- 출선 종료~다음 출선까지 대기시간: **{default_wait_time}분**
""")

st.header("입력 항목")

# 사용자 입력 받기
ore_coke_ratio = st.number_input("Ore/Coke 비율", min_value=0.0, step=0.01)
air_flow = st.number_input("풍량 (Nm³/min)", min_value=0.0)
air_pressure = st.number_input("풍압 (kg/cm²)", min_value=0.0)
furnace_pressure = st.number_input("노정압 (kg/cm²)", min_value=0.0)
furnace_temperature = st.number_input("용선온도 (°C)", min_value=0.0)
oxygen_injection = st.number_input("산소부화량 (Nm³/hr)", min_value=0.0)
moisture_content = st.number_input("조습량 (g/Nm²)", min_value=0.0)
tfe_percent = st.number_input("T.Fe (%)", min_value=0.0)
daily_production = st.number_input("일일생산량 (ton)", min_value=0.0)

# 추가된 항목들
raw_material_granulation = st.number_input("원료 입도 (mm)", min_value=0.0)
furnace_lifetime = st.number_input("고로 수명 (년)", min_value=0, value=0, step=1)

# 출선구 관련 기본값 설정
tap_time = st.number_input("1개 출선구 평균 출선시간 (min)", min_value=0.0, value=float(default_tap_time), step=1.0)
tap_speed = st.number_input("출선 속도 (ton/min)", min_value=0.0, value=float(default_tap_speed), step=0.01)
tap_amount = st.number_input("1회 출선시 배출량 (ton)", min_value=0.0, value=float(default_tap_amount), step=1.0)
wait_time = st.number_input("차기 출선까지 대기 시간 (min)", min_value=0.0, value=float(default_wait_time), step=1.0)

# ---- 계산 공식 ----

def predict_slag_amount():
    return daily_production * (1 - (tfe_percent / 100))

def predict_blast_furnace_output():
    return daily_production * ore_coke_ratio * 0.8

def calculate_blast_furnace_radiation(blast_furnace_output):
    radiation_factor = 0.05  # 예시값
    return blast_furnace_output * radiation_factor

def calculate_slag_radiation(slag_amount):
    radiation_factor = 0.02  # 예시값
    return slag_amount * radiation_factor

def predict_casting_time():
    # 예시: 출선작업 시간 산정 (고로 조업지수 반영)
    k = 0.1
    return (air_flow + oxygen_injection + furnace_pressure + raw_material_granulation + furnace_lifetime) / (ore_coke_ratio + 1 + k)

def predict_total_tap_output():
    return tap_amount * avg_casts_per_day

# ---- 결과 계산 및 출력 ----
if st.button("계산하기"):
    slag_amount = predict_slag_amount()
    blast_furnace_output = predict_blast_furnace_output()
    slag_radiation = calculate_slag_radiation(slag_amount)
    blast_furnace_radiation = calculate_blast_furnace_radiation(blast_furnace_output)
    total_radiation = slag_radiation + blast_furnace_radiation
    casting_time = predict_casting_time()
    total_tap_output = predict_total_tap_output()
    
    st.header("예상 결과")
    st.write(f"용선 저선량: {blast_furnace_radiation:.2f} ton")
    st.write(f"슬래그 저선량: {slag_radiation:.2f} ton")
    st.write(f"노내 예상 총 저선량: {total_radiation:.2f} ton")
    st.write(f"출선 작업 시간 예측: {casting_time:.2f} 분")
    st.write(f"하루 예상 총 출선량: {total_tap_output:.2f} ton")
    st.write(f"출선구 1개당 평균 출선시간: {tap_time:.0f} 분")
    st.write(f"출선구 평균 출선속도: {tap_speed:.2f} ton/min")
    st.write(f"1회 출선당 평균 배출량: {tap_amount:.0f} ton")
    st.write(f"차기 출선까지 평균 대기시간: {wait_time:.0f} 분")