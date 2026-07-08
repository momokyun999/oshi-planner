"""
割り勘計算ロジック。
支払い記録から、1人あたりの負担額・各メンバーの収支・
最小送金回数になる精算方法を計算する。
"""


def calculate_split(members, payments):
    """
    members: メンバー名のリスト
    payments: [{"payer": 支払者, "item": 項目名, "amount": 金額}, ...]
    """
    total = sum(p["amount"] for p in payments)
    num_members = len(members)
    per_person = total / num_members if num_members else 0

    paid_by = {m: 0 for m in members}
    for p in payments:
        if p["payer"] in paid_by:
            paid_by[p["payer"]] += p["amount"]

    balance = {m: paid_by[m] - per_person for m in members}
    settlement = _settle_balances(balance)

    return {
        "total": total,
        "per_person": per_person,
        "paid_by": paid_by,
        "balance": balance,
        "settlement": settlement,
    }


def _settle_balances(balance):
    """
    収支（プラス：もらう側／マイナス：払う側）から、
    負債が多い人から債権が多い人へ順に精算する
    （最小送金回数になる貪欲法）。
    """
    creditors = sorted(
        ([m, b] for m, b in balance.items() if b > 0.5),
        key=lambda x: -x[1],
    )
    debtors = sorted(
        ([m, -b] for m, b in balance.items() if b < -0.5),
        key=lambda x: -x[1],
    )

    settlement = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor_name, debt = debtors[i]
        creditor_name, credit = creditors[j]
        amount = min(debt, credit)

        if amount > 0.5:
            settlement.append({
                "from": debtor_name,
                "to": creditor_name,
                "amount": round(amount),
            })

        debtors[i][1] -= amount
        creditors[j][1] -= amount

        if debtors[i][1] <= 0.5:
            i += 1
        if creditors[j][1] <= 0.5:
            j += 1

    return settlement
