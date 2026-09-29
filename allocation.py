"""원 단위 자금 배분 원장. UI/AI와 무관하며 모든 목표의 배분을 함께 검증한다."""
import math

SAVINGS_ITEMS = {"deposit": "적금", "etf": "ETF", "subscription": "주택청약"}
ASSET_SOURCES = ("cash", "etf", "reserve", "subscription")
LINKED_GOALS = {"wedding_lease": ("wedding", "lease")}


def default_allocations(case=True):
    """사례 배분은 편집 가능한 시연 가정이며 원래 사례의 확정 사실이 아니다."""
    assets = {s: {} for s in ASSET_SOURCES}
    monthly = {s: {} for s in SAVINGS_ITEMS}
    if case:
        assets.update(cash={"wedding": 6_000_000, "lease": 12_000_000},
                      etf={"wedding": 4_000_000, "lease": 6_000_000},
                      reserve={"reserve": 10_000_000}, subscription={"hold": 9_500_000})
        monthly.update(deposit={"wedding": 50, "lease": 50},
                       etf={"wedding": 50, "lease": 50}, subscription={"hold": 100})
    return assets, monthly


def validate_allocations(balances, allocations, goals, percentages=False):
    """자산은 잔액, 월 납입 배분율은 100%를 한도로 검증. 오류 시 계산 금지."""
    for source, balance in balances.items():
        if not math.isfinite(balance) or balance < 0:
            raise ValueError(f"{source}: 잔액은 0 이상의 유한한 숫자여야 합니다.")
    for source, entries in allocations.items():
        if source not in balances:
            raise ValueError(f"알 수 없는 자금 항목: {source}")
        for goal, value in entries.items():
            if goal not in goals or not math.isfinite(value) or value < 0:
                raise ValueError(f"{source}: 목표 또는 배분값이 올바르지 않습니다.")
        limit = 100 if percentages else balances[source]
        if sum(entries.values()) > limit + 1e-7:
            raise ValueError(f"{source}: 전체 배분이 {'100%' if percentages else '자산 잔액'}을 초과했습니다.")


def allocated_resources(chosen, balances, monthly_items, asset_book, monthly_book, goals):
    validate_allocations(balances, asset_book, goals)
    validate_allocations(monthly_items, monthly_book, goals, percentages=True)
    members = LINKED_GOALS.get(chosen, (chosen,))
    if any(g not in goals for g in members):
        raise ValueError("알 수 없는 분석 목표입니다.")
    assets = {s: sum(asset_book.get(s, {}).get(g, 0) for g in members) for s in balances}
    savings = {s: monthly_items[s] * sum(monthly_book.get(s, {}).get(g, 0) for g in members) / 100
               for s in monthly_items}
    return assets, savings


def funding_structure(total, own, spouse, loan):
    values = (total, own, spouse, loan)
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError("조달 금액은 0 이상의 유한한 숫자여야 합니다.")
    return {"총 필요자금": total, "본인 부담": own, "배우자 부담": spouse,
            "대출 조달": loan, "본인 분석 대상 금액": own,
            "조달 차액 (합계 − 총액)": own + spouse + loan - total}
