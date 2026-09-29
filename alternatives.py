"""결정론적 대안 설명 및 검토 기준. AI 판단/추천을 생성하지 않는다."""
import math

RATE_WARNING = ("기대수익률 상승은 보장되지 않으며 변동성 및 손실 가능성이 증가할 수 있습니다. "
                "고객의 안정형/위험회피형 투자성향과 적합성을 별도로 검토해야 합니다.")


def adjust_components(components, adjusted_total, selected):
    """변경분을 명시적으로 선택한 하위 목표에만 반영한다. 금액은 원."""
    if selected not in components or not components:
        raise ValueError("조정할 하위 목표를 선택하세요.")
    if any(not math.isfinite(v) or v < 0 for v in components.values()):
        raise ValueError("하위 목표 금액이 올바르지 않습니다.")
    if not math.isfinite(adjusted_total) or adjusted_total <= 0:
        raise ValueError("조정 후 목표 합계는 0보다 커야 합니다.")
    updated = dict(components)
    updated[selected] += adjusted_total - sum(components.values())
    if updated[selected] < 0:
        raise ValueError("감액이 선택한 하위 목표 금액보다 큽니다. 목표금액 또는 조정 대상을 변경하세요.")
    return updated


def describe_components(before, after, won):
    return [f"{k}: {won(v)} → {won(after[k])}" + (" (유지)" if v == after[k] else "")
            for k, v in before.items()]


def action_names(rows, savings, years, rate, components, adjusted, selected, won):
    diff = rows[1]['savings'] - savings
    period = rows[2]['years'] - years
    change = adjusted[selected] - components[selected]
    return ["기준안",
            f"월 {won(abs(diff))} " + ("추가저축" if diff > 0 else "저축 감액" if diff < 0 else "저축 유지"),
            f"목표시점 {abs(period)}년 " + ("연기" if period > 0 else "앞당김" if period < 0 else "유지"),
            f"{selected} {won(abs(change))} " + ("감액" if change < 0 else "증액" if change > 0 else "유지"),
            f"기대수익률 {rows[4]['rate']:g}% 가정", "복합 조정안"]


def cashflow_interpretation(current, changed, extra, won):
    text = f"월 저축 {won(extra)} 변경 시 월 잉여현금흐름이 {won(current)}에서 {won(changed)}으로 바뀝니다. "
    if changed <= 0:
        return text + "생활비 여유가 없거나 적자이므로 현재 현금흐름으로 충당하기 어렵습니다. 지출 조정이나 추가 재원이 필요합니다."
    if extra > 0 and changed < 50_000:
        return text + "산술적으로 납입할 수 있지만 유동성 여유가 크게 줄어 단독 대안으로는 부담이 있을 수 있습니다."
    return text + "예상 밖 지출과 비상자금 유지 가능성을 함께 검토하세요."


def assess_alternative(row, current_surplus, base_savings, base_years, base_rate, funding_warning=""):
    """5만 원 미만은 시연용 유동성 주의 기준이며 공인 재무진단 기준이 아니다."""
    remaining = current_surplus - (row['savings'] - base_savings)
    cautions = []
    if remaining <= 0:
        cautions.append("현금흐름 부족")
    elif remaining < 50_000:
        cautions.append("현금흐름 부담 높음")
    if row['years'] > base_years:
        cautions.append("목표시점 지연")
    if row['rate'] > base_rate:
        cautions.append("투자위험 증가")
    if funding_warning:
        cautions.append(funding_warning)
    verdict = "계산상 가능" if row['result'].gap >= 0 else "어려움"
    if cautions:
        verdict += " / " + " · ".join(cautions)
    else:
        verdict += " / 실행조건 검토 필요"
    return remaining, cautions, verdict
