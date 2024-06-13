import datetime as dt

from accounting.model.transaction_type import TransactionType


def test_get_incomes(client):
    resp = client.get("/incomes/")
    now = dt.date.today().isoformat()
    assert resp.json == [
        {
            "amount": 5000.0,
            "created_at": now,
            "description": "Salary",
            "type": TransactionType.INCOME.value,
        },
        {
            "amount": 200.0,
            "created_at": now,
            "description": "Dividends",
            "type": TransactionType.INCOME.value,
        },
    ]


def test_add_income(client):
    new_income = {
        "amount": 2000.0,
        "description": "Gift",
    }
    resp = client.post("/incomes/", json=new_income)
    assert resp.status_code == 201
    assert resp.text == ""

    resp = client.get("/incomes/")
    now = dt.date.today().isoformat()
    assert resp.json == [
        {
            "amount": 5000.0,
            "created_at": now,
            "description": "Salary",
            "type": TransactionType.INCOME.value,
        },
        {
            "amount": 200.0,
            "created_at": now,
            "description": "Dividends",
            "type": TransactionType.INCOME.value,
        },
        {
            "amount": 2000.0,
            "created_at": now,
            "description": "Gift",
            "type": TransactionType.INCOME.value,
        },
    ]
