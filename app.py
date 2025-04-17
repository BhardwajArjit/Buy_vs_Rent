import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="🏠 Buy vs Rent Calculator", layout="wide")

st.title("🏠 Buy vs Rent Analysis Tool")
st.markdown("Analyze your net worth over time when choosing to **buy** or **rent** a home.")

# ----------------------- Sidebar Inputs ----------------------- #
st.sidebar.header("🏗️ Property Details")
home_value = st.sidebar.number_input("Home Value (₹)", value=1_00_00_000, step=1_00_000)
down_payment = st.sidebar.number_input("Down Payment (₹)", value=20_00_000, step=1_00_000)
interest_rate = st.sidebar.slider("Interest Rate (%)", 6.0, 12.0, 8.5) / 100
loan_tenure_years = st.sidebar.slider("Loan Tenure (Years)", 10, 30, 20)
property_appreciation = st.sidebar.slider("Property Appreciation (%)", 1.0, 10.0, 4.0) / 100

st.sidebar.header("💰 Rent and Investment")
starting_rent = st.sidebar.number_input("Initial Monthly Rent (₹)", value=20_000, step=1_000)
rent_escalation = st.sidebar.slider("Annual Rent Increase (%)", 0.0, 10.0, 5.0) / 100
equity_return = st.sidebar.slider("Equity Return Rate (%)", 5.0, 20.0, 12.0) / 100

st.sidebar.header("📜 Assumptions")
stamp_duty_percent = st.sidebar.slider("Stamp Duty (%)", 4.0, 10.0, 6.0) / 100
registration_fee = st.sidebar.number_input("Registration Fee (₹)", value=50_000, step=10_000)
processing_insurance_percent = st.sidebar.slider("Processing + Insurance (%)", 0.0, 2.0, 0.5) / 100
capital_gains_tax = st.sidebar.slider("Capital Gains Tax (%)", 0.0, 30.0, 20.0) / 100
indexation_rate = st.sidebar.slider("Indexation Rate (%)", 0.0, 10.0, 6.0) / 100

# ----------------------- Fixed Values ----------------------- #
monthly_maintenance = 5000
monthly_property_tax = 2500
tax_bracket = 0.30
max_tax_deduction = 2_00_000

stamp_duty = stamp_duty_percent * home_value
processing_insurance = processing_insurance_percent * (home_value - down_payment)
initial_expenses = stamp_duty + registration_fee + processing_insurance

loan_amount = home_value - down_payment
monthly_interest_rate = interest_rate / 12
total_months = loan_tenure_years * 12
emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** total_months / \
      ((1 + monthly_interest_rate) ** total_months - 1)

# ------------------------ Simulation ------------------------ #
years = list(range(1, loan_tenure_years + 1))
property_values = []
total_emis_paid = []
total_rents_paid = []
investment_corpus_values = []
annual_tax_savings = []
net_worth_buy = []
net_worth_rent = []

rent = starting_rent
investment_balance = down_payment
remaining_loan = loan_amount
cumulative_emi = 0
cumulative_rent = 0

for year in years:
    property_price = home_value * (1 + property_appreciation) ** year
    property_values.append(property_price)

    interest_paid = 0
    for month in range(12):
        interest_component = remaining_loan * monthly_interest_rate
        principal_component = emi - interest_component
        remaining_loan -= principal_component
        interest_paid += interest_component

    cumulative_emi += emi * 12
    total_emis_paid.append(cumulative_emi)

    cumulative_rent += rent * 12
    total_rents_paid.append(cumulative_rent)

    tax_saved = min(max_tax_deduction, interest_paid) * tax_bracket
    annual_tax_savings.append(tax_saved)

    monthly_investment = max(0, emi - rent)
    for _ in range(12):
        investment_balance = investment_balance * (1 + equity_return / 12) + monthly_investment

    investment_corpus_values.append(investment_balance)

    ownership_net_worth = property_price - remaining_loan
    net_worth_buy.append(ownership_net_worth)
    net_worth_rent.append(investment_balance)

    rent *= (1 + rent_escalation)

# ------------------ Final Adjustments ------------------ #
final_property_value = property_values[-1]
indexed_cost = home_value * (1 + indexation_rate) ** loan_tenure_years
capital_gain = final_property_value - indexed_cost
capital_gains_tax_paid = max(0, capital_gain * capital_gains_tax)

final_net_buy = final_property_value - remaining_loan - capital_gains_tax_paid - initial_expenses
final_net_rent = investment_balance

# ------------------ DataFrame ------------------ #
df = pd.DataFrame({
    "Year": years,
    "Property Value (₹)": property_values,
    "Total EMI Paid (₹)": total_emis_paid,
    "Total Rent Paid (₹)": total_rents_paid,
    "Investment Corpus (₹)": investment_corpus_values,
    "Tax Savings (₹)": annual_tax_savings,
    "Net Worth - Buy (₹)": net_worth_buy,
    "Net Worth - Rent (₹)": net_worth_rent
})

# ------------------ Layout: Results ------------------ #
col1, col2 = st.columns(2)
col1.metric("🏠 Final Net Worth (Buy)", f"₹{final_net_buy:,.0f}")
col2.metric("🏡 Final Net Worth (Rent)", f"₹{final_net_rent:,.0f}")

# ------------------ Chart ------------------ #
st.subheader("📈 Net Worth Over Time")
st.line_chart(df.set_index("Year")[["Net Worth - Buy (₹)", "Net Worth - Rent (₹)"]])

# ------------------ Details ------------------ #
with st.expander("📊 Show Detailed Table"):
    st.dataframe(df, use_container_width=True)

with st.expander("ℹ️ Assumptions & Notes"):
    st.markdown(f"""
    - **Stamp Duty**: {stamp_duty_percent * 100:.1f}% → ₹{stamp_duty:,.0f}  
    - **Registration Fee**: ₹{registration_fee:,.0f}  
    - **Processing + Insurance**: {processing_insurance_percent * 100:.1f}% → ₹{processing_insurance:,.0f}  
    - **Indexation Rate**: {indexation_rate * 100:.1f}%  
    - **Capital Gains Tax**: {capital_gains_tax * 100:.1f}%  
    - **Equity Return on Investment**: {equity_return * 100:.1f}%  
    - **Maintenance & Property Tax**: Not factored into Net Worth  
    """)
