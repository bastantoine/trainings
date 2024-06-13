import datetime as dt

from marshmallow import Schema, fields

from accounting.model.transaction_type import TransactionType


class Transaction(object):
    def __init__(
        self,
        description: str,
        amount: int,
        transaction_type: TransactionType,
    ):
        self.description = description
        self.amount = amount
        self.created_at = dt.datetime.now()
        self.type = transaction_type

    def __repr__(self):
        return "<Transaction (name={self.description!r})>".format(self=self)


class TransactionSchema(Schema):
    description = fields.Str()
    amount = fields.Number()
    created_at = fields.Date()
    type = fields.Enum(TransactionType, by_value=True)
