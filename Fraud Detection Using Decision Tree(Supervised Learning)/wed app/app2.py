import streamlit as st
import pandas as pd
import joblib

# Load Decision Tree pipeline
model = joblib.load("fraud_detection_decision_tree_pipeline.pkl")

st.title("Fraud Detection Prediction App (Decision Tree)")
st.markdown("Please enter the transaction details and press predict.")

st.divider()

transaction_type = st.selectbox("Transaction Type", ["PAYMENT", "TRANSFER", "CASH_OUT", "DEPOSIT"])
amount = st.number_input("Amount", min_value=0.0, value=1000.0)

oldbalanceOrg = st.number_input("Old Balance (Sender)", min_value=0.0, value=10000.0)
newbalanceOrig = st.number_input("New Balance (Sender)", min_value=0.0, value=9000.0)

oldbalanceDest = st.number_input("Old Balance (Receiver)", min_value=0.0, value=0.0)
newbalanceDest = st.number_input("New Balance (Receiver)", min_value=0.0, value=0.0)

if st.button("Predict"):
    input_data = pd.DataFrame([{
        "type": transaction_type,
        "amount": amount,
        "oldbalanceOrg": oldbalanceOrg,
        "newbalanceOrig": newbalanceOrig,
        "oldbalanceDest": oldbalanceDest,
        "newbalanceDest": newbalanceDest
    }])

    # Compute engineered features required by the pipeline
    input_data["balanceDiffOrg"] = input_data["oldbalanceOrg"] - input_data["newbalanceOrig"]
    input_data["balanceDiffDest"] = input_data["newbalanceDest"] - input_data["oldbalanceDest"]

    try:
        prediction = model.predict(input_data)[0]
        st.subheader(f"Prediction: {int(prediction)}")
        if prediction == 1:
            st.error("⚠️ This transaction may be fraud!")
        else:
            st.success("✅ This transaction looks safe.")
    except Exception as e:
        st.error(f"Error during prediction: {e}")