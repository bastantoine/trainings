import typing as t

from marshmallow import post_load

from accounting.model.transaction import Transaction, TransactionSchema
from accounting.model.transaction_type import TransactionType


class Expense(Transaction):
    def __init__(self, description: str, amount: str):
        super(Expense, self).__init__(
            description, -abs(amount), TransactionType.EXPENSE
        )

    def __repr__(self):
        return "<Expense (name={self.description!r})>".format(self=self)


class ExpenseSchema(TransactionSchema):
    @post_load
    def make_expense(self, data: t.Dict[str, str], **_):
        return Expense(**data)
