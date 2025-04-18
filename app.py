import streamlit as st
import pandas as pd
import numpy as np

# Config
st.set_page_config(page_title="Buy vs Rent Simulator", layout="wide")
st.title("🏙️ Buy vs Rent")

# --------------------- User Inputs ---------------------
st.sidebar.header("🏠 Property Details")
property_price = st.sidebar.number_input("Property Price (₹)", value=1_00_00_000, step=1_00_000)
down_payment = st.sidebar.number_input("Down Payment (₹)", value=20_00_000, step=1_00_000)
holding_period = st.sidebar.selectbox("Property Holding Period (Years)", [5, 10, 15, 20], index=3)
interest_rate = st.sidebar.slider("Loan Interest Rate (%)", 6.0, 10.0, 8.5) / 100
property_appreciation = st.sidebar.slider("Annual Property Appreciation (%)", 2.0, 10.0, 5.0) / 100

# New Maintenance Settings
st.sidebar.subheader("🧾 Upkeep Details")
annual_upkeep = st.sidebar.number_input("Annual Maintenance + Society + Tax (₹)", value=70_000, step=5_000)
upkeep_escalation = st.sidebar.slider("Upkeep Escalation Rate (%)", 0.0, 10.0, 5.0) / 100

# Renting
st.sidebar.header("💸 Renting Details")
initial_rent = st.sidebar.number_input("Initial Monthly Rent (₹)", value=25_000, step=1_000)
rent_increase = st.sidebar.slider("Annual Rent Increase (%)", 2.0, 10.0, 5.0) / 100
equity_return = st.sidebar.slider("Investment Return (%)", 8.0, 15.0, 12.0) / 100

# --------------------- Constants ---------------------
loan_tenure_years = 20
loan_amount = property_price - down_payment
monthly_interest_rate = interest_rate / 12
months = loan_tenure_years * 12

# EMI Calculation
emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**months / ((1 + monthly_interest_rate)**months - 1)

# Stamp duty, registration, etc.
stamp_duty = 0.06 * property_price
registration_fee = min(0.01 * property_price, 30_000)
interior_cost = 8_00_000
brokerage_fee = 0.02  # 2% on sale

# --------------------- Loan Amortization ---------------------
principal_outstanding = loan_amount
remaining_principal = []

for m in range(1, months + 1):
    interest = principal_outstanding * monthly_interest_rate
    principal = emi - interest
    principal_outstanding -= principal
    remaining_principal.append(principal_outstanding)

# --------------------- Net Worth Over Time ---------------------
property_value = property_price
buy_net_worth = []
rent_net_worth = []

rent = initial_rent
investment = down_payment
upkeep = annual_upkeep

for year in range(1, holding_period + 1):
    # Property appreciation
    property_value *= (1 + property_appreciation)

    # Loan remaining
    months_elapsed = year * 12
    loan_remaining = remaining_principal[months_elapsed - 1] if months_elapsed < months else 0

    # Sale proceeds
    sale_price = property_value
    sale_cost = sale_price * brokerage_fee
    capital_gain = sale_price - property_price
    capital_gains_tax = 0.2 * capital_gain if year >= 2 else 0
    buy_equity = sale_price - loan_remaining - capital_gains_tax - sale_cost - upkeep - interior_cost  # <- updated
    buy_net_worth.append(buy_equity)

    # Rent + Invest path
    monthly_investment = max(0, emi - rent)
    for _ in range(12):
        investment = investment * (1 + equity_return / 12) + monthly_investment
    rent_net_worth.append(investment)
    rent *= (1 + rent_increase)

    # Escalate upkeep
    upkeep *= (1 + upkeep_escalation)

# Final values
net_worth_buy = buy_net_worth[-1]
net_worth_rent = rent_net_worth[-1]

# --------------------- Results ---------------------
col1, col2 = st.columns(2)
col1.metric("🏠 Net Worth from Buying", f"₹{net_worth_buy:,.0f}")
col2.metric("🏡 Net Worth from Renting + Investing", f"₹{net_worth_rent:,.0f}")

# --------------------- Chart ---------------------
st.subheader("📈 Net Worth Growth Over Time")
df_growth = pd.DataFrame({
    "Buy Net Worth": buy_net_worth,
    "Rent + Invest": rent_net_worth
}, index=range(1, holding_period + 1))
st.line_chart(df_growth)

# --------------------- Detailed Yearly Comparison ---------------------
years = list(range(1, holding_period + 1))
property_values = []
interest_paid_list = []
principal_paid_list = []
total_emis_paid = []
annual_tax_savings = []
total_rents_paid = []
investment_corpus_values = []
net_worth_buy = []
net_worth_rent = []

property_value = property_price
principal_outstanding = loan_amount
rent = initial_rent
investment = down_payment
upkeep = annual_upkeep

for year in years:
    # Property Value
    property_value *= (1 + property_appreciation)
    property_values.append(property_value)

    # EMI Breakdown
    interest_paid = 0
    principal_paid = 0
    for _ in range(12):
        interest = principal_outstanding * monthly_interest_rate
        principal = emi - interest
        interest_paid += interest
        principal_paid += principal
        principal_outstanding -= principal
    total_emis_paid.append(interest_paid + principal_paid)
    interest_paid_list.append(interest_paid)
    principal_paid_list.append(principal_paid)

    # Tax Savings (assume 30% tax benefit on interest paid up to ₹2L)
    tax_saving = min(interest_paid, 2_00_000) * 0.30
    annual_tax_savings.append(tax_saving)

    # Net Worth from Buying
    loan_remaining = principal_outstanding
    sale_cost = property_value * brokerage_fee
    capital_gain = property_value - property_price
    capital_gains_tax = 0.2 * capital_gain if year >= 2 else 0
    equity = property_value - loan_remaining - capital_gains_tax - sale_cost - upkeep - interior_cost  # <- updated
    net_worth_buy.append(equity)

    # Rent Paid
    annual_rent = rent * 12
    total_rents_paid.append(annual_rent)

    # Rent + Invest Corpus
    monthly_investment = max(0, emi - rent)
    for _ in range(12):
        investment = investment * (1 + equity_return / 12) + monthly_investment
    investment_corpus_values.append(investment)
    net_worth_rent.append(investment)

    # Escalations
    rent *= (1 + rent_increase)
    upkeep *= (1 + upkeep_escalation)

# --------------------- Final Table ---------------------
df = pd.DataFrame({
    "Year": years,
    "Property Value (₹)": property_values,
    "Interest Paid (₹)": interest_paid_list,
    "Principal Paid (₹)": principal_paid_list,
    "Total EMI Paid (₹)": total_emis_paid,
    "Tax Savings (₹)": annual_tax_savings,
    "Total Rent Paid (₹)": total_rents_paid,
    "Investment Corpus (₹)": investment_corpus_values,
    "Net Worth - Buy (₹)": net_worth_buy,
    "Net Worth - Rent (₹)": net_worth_rent
})

st.subheader("📊 Detailed Year-by-Year Comparison")
st.dataframe(df.style.format({
    "Property Value (₹)": "₹{:,.0f}",
    "Interest Paid (₹)": "₹{:,.0f}",
    "Principal Paid (₹)": "₹{:,.0f}",
    "Total EMI Paid (₹)": "₹{:,.0f}",
    "Tax Savings (₹)": "₹{:,.0f}",
    "Total Rent Paid (₹)": "₹{:,.0f}",
    "Investment Corpus (₹)": "₹{:,.0f}",
    "Net Worth - Buy (₹)": "₹{:,.0f}",
    "Net Worth - Rent (₹)": "₹{:,.0f}",
}), use_container_width=True)

# --------------------- Assumptions ---------------------
with st.expander("📋 Mumbai Assumptions Used"):
    st.markdown(f"""
    - **Stamp Duty**: ₹{stamp_duty:,.0f}
    - **Registration Fee**: ₹{registration_fee:,.0f}
    - **Interior Cost**: ₹{interior_cost:,.0f} (deducted from buy-side equity)
    - **EMI**: ₹{emi:,.0f}/month
    - **Loan Tenure**: 20 years
    - **Annual Upkeep (Maintenance + Society + Tax)**: ₹{annual_upkeep:,.0f}, escalating at {int(upkeep_escalation * 100)}%/year
    - **Brokerage on Sale**: 2%
    - **Capital Gains Tax**: 20% on gains after 2 years
    - **Loan Remaining at Sale**: ₹{loan_remaining:,.0f}
    """)

# --------------------- Disclaimer ---------------------
st.markdown("---")
st.markdown("#### ⚠️ Disclaimer")
st.markdown("""
This simulator uses **simplified assumptions and calculations** to keep the concept easy to understand for the general audience.  
It is **not intended to provide precise financial advice or forecasts**. Please consult a qualified financial advisor before making any real estate decisions.
""")
