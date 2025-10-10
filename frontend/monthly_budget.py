import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"

def monthly_budget_tab():
    st.subheader("Monthly Budget Tracker")
    selected_date = st.date_input("Selected month", datetime(2024, 8, 1), label_visibility="collapsed")
    month_year = selected_date.strftime("%Y-%m")

    # Initialize a session_state key to force refresh
    if "refresh_budget" not in st.session_state:
        st.session_state.refresh_budget = 0

    # Fetch current budget and spending
    @st.cache_data
    def fetch_budget(month_year):
        response = requests.get(f"{API_URL}/budget/{month_year}")
        if response.status_code == 200:
            return response.json()
        return None

    # Clear cached API call if budget was updated
    if st.session_state.refresh_budget > 0:
        fetch_budget.clear()
        st.session_state.refresh_budget = 0

    data = fetch_budget(month_year)
    if data:
        budget_amount = data["budget"]
        spent_amount = data["spent"]
        remaining = data["remaining"]
        st.success(f"Budget for {month_year}: ₹{budget_amount}")
        st.info(f"Spent: ₹{spent_amount} | Remaining: ₹{remaining}")
        # Calculate spending ratio
        ratio = spent_amount / budget_amount if budget_amount > 0 else 0

        # Determine color based on usage level
        if ratio < 0.5:
            bar_color = "green"
        elif ratio < 0.9:
            bar_color = "orange"
        else:
            bar_color = "red"

        # Display progress visually using st.markdown (custom color)
        progress_html = f"""
            <div style='background-color:#ddd; border-radius:10px; height:25px;'>
                <div style='width:{min(ratio * 100, 100)}%;
                            background-color:{bar_color};
                            height:25px;
                            border-radius:10px;
                            text-align:center;
                            color:white;
                            font-weight:bold;'>
                    {min(ratio * 100, 100):.1f}%
                </div>
            </div>
            """
        st.markdown(progress_html, unsafe_allow_html=True)

        # Out of budget alert
        if remaining < 0:
            st.error("🚨 You’ve exceeded your monthly budget!")
        elif remaining == 0:
            st.warning("⚠️ Budget limit reached — spend wisely!")
    else:
        st.warning("No budget set for this month")


    # Set/Update budget
    st.divider()
    st.write("### ✏️ Set or Update Budget")
    new_budget = st.number_input("Enter monthly budget", min_value=0.0, step=100.0)
    if st.button("Save Budget"):
        input_data = {"month_year": month_year, "budget_amount": new_budget}
        response = requests.post(f"{API_URL}/budget", json=input_data)

        if response.status_code == 200:
            st.toast("✅ Budget updated successfully!")
            # Increment session_state to trigger refresh
            st.session_state.refresh_budget += 1
            st.rerun()  # 🔥 This forces Streamlit to rerun and show updated values
        else:
            st.error("❌ Failed to update budget.")
