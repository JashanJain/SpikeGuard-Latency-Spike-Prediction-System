import streamlit as st
import joblib
import pandas as pd

model = joblib.load("latency_model.pkl")
threshold = joblib.load("threshold.pkl")
demo_threshold = 0.3  # lower for demo visibility

st.title("Latency Spike Predictor")

# Inputs
cpu = st.slider("CPU Usage", 0.0, 100.0, 50.0)
mem = st.slider("Memory Usage", 0.0, 100.0, 50.0)
net = st.number_input("Network Traffic", 0.0, 10000.0, 100.0)
power = st.number_input("Power Consumption", 0.0, 10000.0, 500.0)
instr = st.number_input("Executed Instructions", 0.0, 1e9, 1e6)
eff = st.slider("Energy Efficiency", 0.0, 1.0, 0.5)
exec_lag = st.number_input("Previous Execution Time", 0.0, 10000.0, 200.0)
exec_roll = st.number_input("Rolling Execution Time (5)", 0.0, 10000.0, 200.0)
cpu_lag = st.slider("Previous CPU Usage", 0.0, 100.0, 50.0)
cpu_roll = st.slider("Rolling CPU Usage (5)", 0.0, 100.0, 50.0)
mem_lag = st.slider("Previous Memory Usage", 0.0, 100.0, 50.0)
priority = st.selectbox("Task Priority", ["high", "medium", "low"])

# Encode priority
task_priority_low = 1 if priority == "low" else 0
task_priority_medium = 1 if priority == "medium" else 0

# Build input
input_df = pd.DataFrame([{
    "cpu_usage": cpu,
    "memory_usage": mem,
    "network_traffic": net,
    "power_consumption": power,
    "num_executed_instructions": instr,
    "energy_efficiency": eff,
    "exec_time_lag1": exec_lag,
    "exec_time_roll5": exec_roll,
    "cpu_lag1": cpu_lag,
    "cpu_roll5": cpu_roll,
    "mem_lag1": mem_lag,
    "task_priority_low": task_priority_low,
    "task_priority_medium": task_priority_medium
}])

# Ensure correct order
expected_cols = model.get_booster().feature_names
input_df = input_df[expected_cols]

# Predict
prob = model.predict_proba(input_df)[0, 1]

# Display
st.metric("Spike Probability", f"{prob:.3f}")
st.caption(f"Model threshold = {threshold:.3f} | Demo threshold = {demo_threshold}")

st.write("Model input:")
st.dataframe(input_df)

# Alert
if prob >= demo_threshold:
    st.error("⚠ High risk of latency spike")
else:
    st.success("System stable")