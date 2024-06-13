import datetime as dt

from accounting.model.transaction_type import TransactionType


def test_get_expenses(client):
    resp = client.get("/expenses/")
    now = dt.date.today().isoformat()
    assert resp.json == [
        {
            "amount": -50.0,
            "created_at": now,
            "description": "pizza",
            "type": "EXPENSE",
        },
        {
            "amount": -100.0,
            "created_at": now,
            "description": "Rock Concert",
            "type": "EXPENSE",
        },
    ]


def test_add_expense(client):
    new_expense = {
        "amount": 2000.0,
        "description": "Taxes",
    }
    resp = client.post("/expenses/", json=new_expense)
    assert resp.status_code == 201
    assert resp.text == ""

    resp = client.get("/expenses/")
    now = dt.date.today().isoformat()
    assert resp.json == [
        {
            "amount": -50.0,
            "created_at": now,
            "description": "pizza",
            "type": "EXPENSE",
        },
        {
            "amount": -100.0,
            "created_at": now,
            "description": "Rock Concert",
            "type": "EXPENSE",
        },
        {
            "amount": -2000.0,
            "created_at": now,
            "description": "Taxes",
            "type": TransactionType.EXPENSE.value,
        },
    ]
