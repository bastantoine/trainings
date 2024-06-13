import typing as t

from marshmallow import post_load

from accounting.model.transaction import Transaction, TransactionSchema
from accounting.model.transaction_type import TransactionType


class Income(Transaction):
    def __init__(self, description: str, amount: str):
        super(Income, self).__init__(
            description,
            amount,
            TransactionType.INCOME,
        )

    def __repr__(self):
        return "<Income (name={self.description!r})>".format(self=self)


class IncomeSchema(TransactionSchema):
    @post_load
    def make_income(self, data: t.Dict[str, str], **_):
        return Income(**data)
