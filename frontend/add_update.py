import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"

def add_update_tab():
    # --- Select date ---
    selected_date = st.date_input("Enter Date", datetime(2024, 8, 1), label_visibility="collapsed")

    # --- Debug: verify selected date and request URL ---
    formatted_date = selected_date.strftime("%Y-%m-%d")


    # --- Fetch existing expenses from API ---
    response = requests.get(f"{API_URL}/expenses/{formatted_date}")
    if response.status_code == 200:
        existing_expenses = response.json()

    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    # --- Category options ---
    categories = ["Rent", "Food", "Shopping", "Entertainment", "Other"]

    # --- Unique prefix to force widget refresh per date ---
    key_prefix = selected_date.strftime("%Y%m%d")

    # --- Expense form ---
    with st.form(key=f"expense_form_{key_prefix}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text("Amount")
        with col2:
            st.text("Category")
        with col3:
            st.text("Notes")

        expenses = []

        # Allow 5 entries (prepopulate with existing)
        for i in range(5):
            if i < len(existing_expenses):
                amount = existing_expenses[i]['amount']
                category = existing_expenses[i]["category"]
                notes = existing_expenses[i]["notes"]
            else:
                amount = 0.0
                category = "Shopping"
                notes = ""

            # --- Inputs with date-specific keys ---
            col1, col2, col3 = st.columns(3)
            with col1:
                amount_input = st.number_input(
                    label="Amount",
                    min_value=0.0,
                    step=1.0,
                    value=amount,
                    key=f"{key_prefix}_amount_{i}",
                    label_visibility="collapsed"
                )
            with col2:
                category_input = st.selectbox(
                    label="Category",
                    options=categories,
                    index=categories.index(category),
                    key=f"{key_prefix}_category_{i}",
                    label_visibility="collapsed"
                )
            with col3:
                notes_input = st.text_input(
                    label="Notes",
                    value=notes,
                    key=f"{key_prefix}_notes_{i}",
                    label_visibility="collapsed"
                )

            expenses.append({
                'amount': amount_input,
                'category': category_input,
                'notes': notes_input
            })

        # --- Submit button ---
        submit_button = st.form_submit_button("💾 Save / Update Expenses")

        if submit_button:
            filtered_expenses = [expense for expense in expenses if expense['amount'] > 0]

            post_response = requests.post(f"{API_URL}/expenses/{formatted_date}", json=filtered_expenses)
            if post_response.status_code == 200:
                st.success("✅ Expenses updated successfully!")

            else:
                st.error("❌ Failed to update expenses.")
