from flask import Blueprint, jsonify, request

from accounting.data import transactions
from accounting.model.income import IncomeSchema
from accounting.model.transaction_type import TransactionType

incomes_blueprint = Blueprint("incomes", __name__, url_prefix="/incomes")


@incomes_blueprint.route("/")
def get_incomes():
    """Get all the incomes
    ---
    get:
      summary: Get all the incomes
      description: Get all the incomes
      responses:
        200:
          content:
            application/json:
              description: A list of incomes
              schema:
                type: array
                items: IncomeSchema
    """
    schema = IncomeSchema(many=True)
    incomes = schema.dump(
        filter(lambda t: t.type == TransactionType.INCOME, transactions)
    )
    return jsonify(incomes)


@incomes_blueprint.route("/", methods=["POST"])
def add_income():
    """Add a new income
    ---
    post:
      summary: Add a new income
      description: Add a new income
      requestBody:
        content:
          application/json:
            schema: IncomeSchema
      responses:
        201:
          description: Income sucessfully created
    """
    income = IncomeSchema().load(request.get_json())
    transactions.append(income)
    return "", 201
