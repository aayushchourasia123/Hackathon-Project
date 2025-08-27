import streamlit as st
import pickle
import pandas as pd

# Load the trained model pipeline
with open("UPI Fraud Detection updated.pkl", "rb") as f:
    model = pickle.load(f)

st.title("💳 UPI Fraud Detection App")

st.write("Predict whether a transaction is **Fraudulent** or **Genuine**.")

# --- Single Transaction Input ---
st.header("🔹 Predict for a Single Transaction")

transaction_type = st.selectbox(
    "Transaction Type",
    ["Bill Payment", "Investment", "Purchase", "Refund", "Subscription", "Bank Transfer", "Other"]
)

payment_gateway = st.selectbox(
    "Payment Gateway",
    ["Google Pay", "HDFC", "ICICI UPI", "IDFC UPI", "CRED", "Paytm", "PhonePe", "Razor Pay", "Other"]
)

transaction_state = st.selectbox(
    "Transaction State",
    [
        'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
        'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
        'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim',
        'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
    ]
)

merchant_category = st.selectbox(
    "Merchant Category",
    [
        'Donations and Devotion', 'Financial services and Taxes', 'Home delivery',
        'Investment', 'More Services', 'Brand Vouchers and OTT', 'Purchases',
        'Travel bookings', 'Utilities', 'Other'
    ]
)

transaction_date = st.date_input("Transaction Date")
year = str(transaction_date.year)  # model expects object/string
month = transaction_date.strftime("%b")  # 'Jan', 'Feb', ... 'Dec'

amount = st.number_input("Transaction Amount", min_value=1.0, step=1.0)

# Create DataFrame for prediction
input_data = pd.DataFrame([{
    "Transaction_Type": transaction_type,
    "Payment_Gateway": payment_gateway,
    "Transaction_State": transaction_state,
    "Merchant_Category": merchant_category,
    "Year": year,
    "Month": month,
    "amount": amount
}])

if st.button("Predict Fraud (Single Transaction)"):
    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]

    if prediction == 1:
        st.error(f"🚨 Fraudulent Transaction (Probability: {prob:.2f})")
    else:
        st.success(f"✅ Genuine Transaction (Probability: {1-prob:.2f})")

# --- Batch Prediction with CSV Upload ---
st.header("📂 Predict for Multiple Transactions (Upload CSV)")

uploaded_file = st.file_uploader("Upload a CSV file with transactions", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    # --- Fix 1: Clean column names ---
    data.columns = data.columns.str.strip()

    # --- Fix 2: Ensure Year is string (categorical, not int) ---
    data["Year"] = data["Year"].astype(str)

    # --- Fix 3: Ensure numeric column is float ---
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce")

    # --- Fix 4: Strip spaces from categorical columns ---
    cat_cols = ["Transaction_Type", "Payment_Gateway", "Transaction_State", "Merchant_Category", "Month"]
    for col in cat_cols:
        data[col] = data[col].astype(str).str.strip()

    st.write("📊 Cleaned Uploaded Data:")
    st.dataframe(data.head())

    # --- Prediction ---
    try:
        predictions = model.predict(data)
        probs = model.predict_proba(data)[:, 1]

        data["Fraud_Prediction"] = predictions
        data["Fraud_Probability"] = probs

        st.success("✅ Predictions completed")
        st.dataframe(data)

        # Download option
        csv_output = data.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Predictions as CSV",
            data=csv_output,
            file_name="fraud_predictions.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"⚠️ Error: {e}")


