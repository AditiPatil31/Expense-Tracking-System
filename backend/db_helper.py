import mysql.connector
from contextlib import contextmanager
from logging_setup import setup_logger


logger = setup_logger('db_helper')


@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="3112",
        database="expense_manager"
    )

    cursor = connection.cursor(dictionary=True)
    yield cursor
    if commit:
        connection.commit()
    cursor.close()
    connection.close()


def fetch_expenses_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called with {expense_date}")

    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE DATE(expense_date) = %s", (expense_date,))
        expenses = cursor.fetchall()
        return expenses


def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expenses_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))


def insert_expense(expense_date, amount, category, notes):
    logger.info(f"insert_expense called with date: {expense_date}, amount: {amount}, category: {category}, notes: {notes}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes)
        )


def fetch_expense_summary(start_date, end_date):
    logger.info(f"fetch_expense_summary called with start: {start_date} end: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT category, SUM(amount) as total 
               FROM expenses WHERE expense_date
               BETWEEN %s and %s  
               GROUP BY category;''',
            (start_date, end_date)
        )
        data = cursor.fetchall()
        return data


def fetch_monthly_expense_summary():
    logger.info(f"fetch_expense_summary_by_months")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT month(expense_date) as expense_month, 
               monthname(expense_date) as month_name,
               sum(amount) as total FROM expenses
               GROUP BY expense_month, month_name;
            '''
        )
        data = cursor.fetchall()
        return data
def set_budget(month_year,budget_amount):
    logger.info(f"set budget for month_year: {month_year}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
        INSERT INTO budget (month_year, budget_amount)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE budget_amount = VALUES(budget_amount)
    """, (month_year, budget_amount)
                       )


def get_budget(month_year):
    logger.info(f"Get budget for month_year: {month_year}")
    with get_db_cursor() as cursor:
        cursor.execute("""SELECT budget_amount FROM  budget
                        WHERE month_year = %s""", (month_year,))

        result=cursor.fetchone()
        return result

def get_total_spent_in_month(month_year):
    logger.info(f"Total amount spent for month_year: {month_year}")
    with get_db_cursor() as cursor:
        cursor.execute("""SELECT SUM(amount) as total_spent FROM expenses 
                       WHERE DATE_FORMAT(expense_date,"%Y-%m")=%s""",
                       (month_year,))
        result=cursor.fetchone()
        return result


if __name__ == "__main__":
    # expenses = fetch_expenses_for_date("2024-09-30")
    # print(expenses)
    # # delete_expenses_for_date("2024-08-25")
    # summary = fetch_expense_summary("2024-08-01", "2024-08-05")
    # for record in summary:
    #     print(record)
    print(fetch_monthly_expense_summary())
