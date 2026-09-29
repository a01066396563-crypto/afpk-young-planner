"""선택한 목표 시나리오에만 적용되는 할부 종료 후 월말 적립. 금액 단위: 원."""
from dataclasses import dataclass, replace
import math


@dataclass(frozen=True)
class SavingsTransition:
    enabled: bool = False
    payment: int = 162_000
    remaining_months: int = 24
    percent: float = 100.0

    def __post_init__(self):
        if not isinstance(self.enabled, bool):
            raise ValueError("전환 여부는 참/거짓이어야 합니다.")
        if not math.isfinite(self.payment) or self.payment < 0:
            raise ValueError("할부 납입액은 0 이상의 유한한 금액이어야 합니다.")
        if not math.isfinite(self.remaining_months) or int(self.remaining_months) != self.remaining_months or not 0 <= self.remaining_months <= 600:
            raise ValueError("잔존기간은 0~600개월 정수여야 합니다.")
        if not math.isfinite(self.percent) or not 0 <= self.percent <= 100:
            raise ValueError("전환 비율은 0~100%이어야 합니다.")

    @property
    def increase(self):
        # 목표 배분금은 원 단위 정수. 소수 원은 절사하고 현금 여유에 남긴다.
        return math.floor(self.payment * self.percent / 100) if self.enabled else 0


def build_monthly_schedule(monthly, months, transition):
    if not math.isfinite(monthly) or monthly < 0 or not isinstance(months, int) or months < 1:
        raise ValueError("월 저축액과 개월 수가 올바르지 않습니다.")
    return [monthly + (transition.increase if index >= transition.remaining_months else 0)
            for index in range(months)]


def project_with_transition(project, assets, monthly, years, rate, target, transition):
    """기존 미래가치를 보존하고 종료 후 추가 납입의 미래가치만 더한다."""
    base = project(assets, monthly, years, rate, target)
    months = int(years) * 12
    extra_months = max(0, months - transition.remaining_months)
    if transition.increase == 0 or extra_months == 0:
        return base
    log_growth = math.log1p(rate / 100) / 12
    factor = extra_months if rate == 0 else math.expm1(extra_months * log_growth) / math.expm1(log_growth)
    savings_fv = base.savings_fv + transition.increase * factor
    total = base.assets_fv + savings_fv
    gap = 0.0 if math.isclose(total, target, rel_tol=1e-12, abs_tol=1e-7) else total - target
    return replace(base, savings_fv=savings_fv, total=total, gap=gap)


def surplus_after_transition(current_surplus, extra_savings, months, transition):
    now = current_surplus - extra_savings
    if not transition.enabled or months <= transition.remaining_months:
        return now, None
    return now, now + transition.payment - transition.increase


def schedule_description(monthly, months, transition, won):
    if not transition.enabled:
        return [f"할부 종료 저축 전환 미선택: 전 기간 월 {won(monthly)}"]
    cutoff = min(months, transition.remaining_months)
    lines = [f"할부 월 납입액 {won(transition.payment)} · 잔존 {transition.remaining_months}개월 · 전환 {transition.percent:g}%"]
    if cutoff:
        lines.append(f"1~{cutoff}개월: 월 {won(monthly)}")
    if months > cutoff:
        lines.append(f"{cutoff + 1}~{months}개월: 월 {won(monthly + transition.increase)} (추가 {won(transition.increase)})")
    else:
        lines.append("목표기간 안에 할부 종료 후 추가 납입 없음")
    return lines
