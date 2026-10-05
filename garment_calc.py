import streamlit as st_lit
st.title("Garment calculator")

def calculate_production_time(quantity, minutes_per_garment,workers,efficiency):
    total_work_minutes = quantity * minutes_per_garment 
    theoretical_minutes = total_work_minutes / workers
    actual_minutes = theoretical_minutes / (efficiency / 100)
    hours = actual_minutes / 60
    return hours 


st_lit.title("=== Garment Production Time Predictor ===")
quantity = st_lit.number_input("Quantity", min_value = 0 )
minutes = st_lit.number_input("Minutes per garment",min_value=0.1)
workers = st_lit.number_input("Workers", min_value=1)
efficiency = st_lit.number_input("Efficiency", min_value=0.1)

if st_lit.button ("Calculate Production Time"):
    calculated_hours = calculate_production_time(quantity, minutes, workers, efficiency)
    st_lit.write("Estimated production time" , round(calculated_hours,2))