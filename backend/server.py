from fastapi import FastAPI, HTTPException
from datetime import date
import db_helper
from typing import List
from pydantic import BaseModel

app = FastAPI()


class Expense(BaseModel):
    amount: float
    category: str
    notes: str


class DateRange(BaseModel):
    start_date: date
    end_date: date

class Budget(BaseModel):
    month_year:str
    budget_amount:float


@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expenses(expense_date: date):
    expenses = db_helper.fetch_expenses_for_date(expense_date)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")

    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses:List[Expense]):
    db_helper.delete_expenses_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes)

    return {"message": "Expenses updated successfully"}


@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database.")

    total = sum([row['total'] for row in data])

    breakdown = {}
    for row in data:
        percentage = (row['total']/total)*100 if total != 0 else 0
        breakdown[row['category']] = {
            "total": row['total'],
            "percentage": percentage
        }

    return breakdown


@app.get("/monthly_summary/")
def get_analytics():
    monthly_summary = db_helper.fetch_monthly_expense_summary()
    if monthly_summary is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve monthly expense summary from the database.")

    return monthly_summary

@app.post("/budget")
def set_monthly_budget(budget: Budget):
    db_helper.set_budget(budget.month_year,budget.budget_amount)
    return {"message": f"Budget for {budget.month_year} set to {budget.budget_amount}"}

@app.get("/budget/{month_year}")

def get_monthly_budget(month_year: str):
    budget_dict=db_helper.get_budget(month_year)
    spent_dict=db_helper.get_total_spent_in_month(month_year)
    if budget_dict is None:
        raise HTTPException(status_code=404, detail="Budget is not set for this month")

    budget_amount=list(budget_dict.values())[0]
    spent_amount=list(spent_dict.values())[0]
    remaining = budget_amount - spent_amount

    # Check if overspent
    if remaining < 0:
        return {
            "budget": budget_amount,
            "spent": spent_amount,
            "remaining": 0,
            "status": "over_budget",
            "message": f"You exceeded your budget by ₹{abs(remaining)}!"
        }

    # Normal case
    return {
        "budget": budget_amount,
        "spent": spent_amount,
        "remaining": remaining,
        "status": "within_budget"
    }