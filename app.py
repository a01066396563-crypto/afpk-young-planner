"""AFPK 영플래너 챌린지용 재무목표 테스트 앱. 실행: streamlit run app.py"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Projection:
    assets_fv: float
    savings_fv: float
    total: float
    gap: float


def calculate_projection(assets, monthly_savings, years, annual_rate_pct, target):
    """연 실효수익률, 매월 말 납입, 금융자산(부채 차감 전) 기준 계산."""
    values = (assets, monthly_savings, years, annual_rate_pct, target)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("모든 값은 유한한 숫자여야 합니다.")
    if assets < 0 or monthly_savings < 0 or target <= 0:
        raise ValueError("자산·저축액은 0 이상, 목표금액은 0보다 커야 합니다.")
    if years < 1 or years > 50 or int(years) != years:
        raise ValueError("목표기간은 1~50년의 정수여야 합니다.")
    if not -99 <= annual_rate_pct <= 100:
        raise ValueError("예상 연수익률은 -99~100% 범위여야 합니다.")

    months = int(years) * 12
    # r: 연 실효수익률, i: 월 실효수익률 = (1+r)^(1/12)-1
    # log1p/expm1을 사용하여 0에 가까운 수익률에서도 정밀도를 유지합니다.
    log_growth = math.log1p(annual_rate_pct / 100) / 12
    monthly_rate = math.expm1(log_growth)
    assets_fv = assets * math.exp(months * log_growth)
    if annual_rate_pct == 0:
        savings_fv = monthly_savings * months
    else:
        savings_fv = monthly_savings * math.expm1(months * log_growth) / monthly_rate
    total = assets_fv + savings_fv
    # 소수점 계산 오차만 보정하며, 판정은 표시용 원 단위 반올림 전에 수행합니다.
    gap = total - target
    if math.isclose(total, target, rel_tol=1e-12, abs_tol=1e-7):
        gap = 0.0
    return Projection(assets_fv, savings_fv, total, gap)


def won(value):
    if 0 < abs(value) < 1:
        return "1원 미만"
    return f"{value:,.0f}원"


def main():
    import streamlit as st

    st.set_page_config(page_title="영플래너 | 재무목표 테스트", page_icon="📊", layout="wide")
    st.title("재무목표 테스트")
    st.caption("AFPK 영플래너 챌린지 · V0.1 프로토타입")
    st.info("가상의 고객 정보만 입력하세요. 실제 개인정보를 사용하지 않는 테스트용 앱입니다.")
    st.caption("금액 단위: 원 · 값을 변경하면 결과가 자동으로 다시 계산됩니다.")

    customer, goal = st.columns(2, gap="large")
    with customer:
        st.subheader("1. 고객 정보")
        age = st.number_input("나이 (세)", 0, 120, 30, 1)
        income = st.number_input("월 소득 (원)", 0, 10_000_000_000, 3_000_000, 100_000)
        savings = st.number_input("월 저축액 (원)", 0, 10_000_000_000, 1_000_000, 100_000)
        assets = st.number_input("현재 금융자산 (원)", 0, 1_000_000_000_000, 20_000_000, 1_000_000)
        debt = st.number_input("현재 부채 (원)", 0, 1_000_000_000_000, 5_000_000, 1_000_000)
    with goal:
        st.subheader("2. 재무목표")
        target = st.number_input("목표금액 (원)", 1, 1_000_000_000_000, 100_000_000, 1_000_000)
        years = st.number_input("목표기간 (년)", 1, 50, 5, 1)
        rate = st.number_input("예상 연수익률 (%)", -99.0, 100.0, 3.0, 0.1, format="%.2f")
        st.caption("연 실효수익률을 월 수익률로 환산하며, 매월 말 같은 금액을 저축한다고 가정합니다.")
        st.write(f"목표시점 나이: **{age + years}세**")
        st.write(f"현재 순금융자산 (금융자산 − 부채): **{won(assets - debt)}**")
        st.caption("나이와 월 소득은 참고 정보입니다. 월 소득을 자산에 별도로 더하지 않습니다.")

    if savings > income:
        st.warning("월 저축액이 월 소득을 초과합니다. 추가 재원이나 입력 오류가 있는지 인간 검토가 필요합니다.")

    result = calculate_projection(assets, savings, years, rate, target)
    st.divider()
    st.subheader("3. 목표달성 분석")
    st.caption("금융자산 기준 · 부채 차감 전 · 금액은 원 단위로 반올림해 표시합니다.")
    a, b, c = st.columns(3)
    a.metric("목표시점 예상 금융자산", won(result.total))
    b.metric("목표금액", won(target))
    label = "목표 대비 초과액" if result.gap > 0 else "목표 대비 부족액" if result.gap < 0 else "목표 대비 차액"
    c.metric(label, won(abs(result.gap)))
    if result.gap >= 0:
        st.success("단순 계산상 목표달성 가능" + (" · 목표금액과 일치합니다." if result.gap == 0 else f" · {won(result.gap)} 초과 예상"))
    else:
        st.warning(f"단순 계산상 목표달성 어려움 · {won(-result.gap)} 부족 예상")
    st.caption(f"예상 달성 비율: {result.total / target * 100:,.1f}% · 확률이나 수익 보장이 아닙니다.")
    left, right = st.columns(2)
    left.metric("현재 금융자산의 미래가치", won(result.assets_fv))
    right.metric("월 저축액의 누적 미래가치", won(result.savings_fv))

    st.warning("단순 모델 안내: 세금, 물가, 수수료, 소득변화, 수익률 변동 및 부채 이자·상환을 반영하지 않습니다. "
               "현재 부채는 참고용으로만 표시하며 예상 금융자산과 목표달성 판정에서 차감하지 않습니다.")
    with st.expander("계산식과 가정 보기"):
        st.markdown("""
`n = 목표기간 × 12`, `r = 예상 연수익률 ÷ 100`, `i = (1 + r)^(1/12) − 1`

- 현재 금융자산 미래가치 = 현재 금융자산 × `(1 + i)^n`
- 월 저축 미래가치 = 월 저축액 × `((1 + i)^n − 1) / i`
- 연수익률이 0%이면 월 저축 미래가치 = 월 저축액 × `n`
- 예상 금융자산 = 현재 금융자산 미래가치 + 월 저축 미래가치
- 목표 대비 차액 = 예상 금융자산 − 목표금액

모든 계산은 명시적인 Python 수식으로 실행합니다. 생성형 AI나 외부 AI API를 사용하지 않습니다.
""")

    st.divider()
    st.subheader("4. 인간 검토")
    st.text_area("인간 검토 메모", key="review_notes", height=160,
                 placeholder="예: 계산 가정의 한계, 부채 상환과 생활비 검토, 저축 지속 가능성, 최종 판단을 작성하세요. 실제 개인정보는 입력하지 마세요.")
    st.caption("메모는 현재 접속 세션에서만 유지되며 파일이나 데이터베이스에 저장되지 않습니다. "
               "새로고침·연결 종료 시 사라질 수 있습니다. 입력값 변경 후에는 기존 메모도 다시 검토하세요.")


if __name__ == "__main__":
    main()
