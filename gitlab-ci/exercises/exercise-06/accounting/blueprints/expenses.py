from flask import Blueprint, jsonify, request

from accounting.data import transactions
from accounting.model.expense import ExpenseSchema
from accounting.model.transaction_type import TransactionType

expenses_blueprint = Blueprint("expenses", __name__, url_prefix="/expenses")


@expenses_blueprint.route("/")
def get_expenses():
    """Get all the expenses
    ---
    get:
      summary: Get all the expenses
      description: Get all the expenses
      responses:
        200:
          content:
            application/json:
              description: A list of expenses
              schema:
                type: array
                items: ExpenseSchema
    """
    schema = ExpenseSchema(many=True)
    expenses = schema.dump(
        filter(lambda t: t.type == TransactionType.EXPENSE, transactions)
    )
    return jsonify(expenses)


@expenses_blueprint.route("/", methods=["POST"])
def add_expense():
    """Add a new expense
    ---
    post:
      summary: Add a new expense
      description: Add a new expense
      requestBody:
        content:
          application/json:
            schema: ExpenseSchema
      responses:
        201:
          description: expense sucessfully created
    """
    expense = ExpenseSchema().load(request.get_json())
    transactions.append(expense)
    return "", 201
