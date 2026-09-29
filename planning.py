"""AFPK 프로세스 데모 확장. 미래가치는 app.py의 기존 함수를 주입받아 재사용한다."""

import math
from cashflow_schedule import SavingsTransition, project_with_transition, surplus_after_transition, schedule_description
from allocation import SAVINGS_ITEMS, default_allocations, funding_structure
from alternatives import (adjust_components, describe_components, action_names, cashflow_interpretation, assess_alternative, RATE_WARNING)


ASSETS = {
    "deposit": ("오피스텔 보증금", 5_000_000),
    "cash": ("예·적금", 20_500_000),
    "reserve": ("비상예비자금", 10_000_000),
    "etf": ("ETF", 10_000_000),
    "subscription": ("주택청약", 9_500_000),
    "car": ("차량", 8_600_000),
}
FLOW = {
    "income": ("월평균 가처분소득", 2_994_000),
    "fixed": ("고정지출", 1_813_000),
    "variable": ("변동지출", 450_000),
    "savings": ("저축·투자", 600_000),
}
GOALS = {
    "wedding_lease": ("2029 결혼·주거 통합목표", "단기", "2029년", 60_000_000, 2029),
    "reserve": ("비상예비자금 유지", "상시", "상시", 10_000_000, None),
    "debt": ("자동차 할부 상환 완료", "단기", "2028년", 3_600_000, 2028),
    "wedding": ("결혼자금", "단기", "2029년", 20_000_000, 2029),
    "lease": ("봉선동 구축 아파트 전세입주", "단기", "2029년", 40_000_000, 2029),
    "child": ("출산·육아 초기자금", "중기", "2030~2031년", 15_000_000, 2031),
    "suv": ("SUV 교체 추가현금", "중기", "2031~2033년", 20_000_000, 2033),
    "home": ("실거주 자가 마련", "장기", "2037~2038년", 420_000_000, 2038),
    "education": ("자녀 대학 교육자금", "장기", "2048~2049년", 40_000_000, 2049),
    "retirement": ("은퇴 생활비", "장기", "은퇴 시점", 3_000_000, None),
}


def safe_ratio(numerator, denominator):
    """분모 0은 0%가 아닌 계산 불가(None)로 반환."""
    return numerator / denominator if denominator != 0 else None


def _validate_amounts(values):
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError("금액은 0 이상의 유한한 숫자여야 합니다.")


def calculate_balance_sheet(assets, debts):
    _validate_amounts([*assets.values(), *debts.values()])
    total_assets, total_debt = sum(assets.values()), sum(debts.values())
    net = total_assets - total_debt
    return dict(total_assets=total_assets, total_debt=total_debt, net_assets=net,
                debt_ratio=safe_ratio(total_debt, total_assets),
                net_ratio=safe_ratio(net, total_assets))


def calculate_cash_flow(income, fixed, variable, savings, reserve):
    _validate_amounts((income, fixed, variable, savings, reserve))
    spending = fixed + variable
    surplus = income - spending - savings
    return dict(spending=spending, surplus=surplus,
                fixed_ratio=safe_ratio(fixed, income),
                variable_ratio=safe_ratio(variable, income),
                spending_ratio=safe_ratio(spending, income),
                savings_ratio=safe_ratio(savings, income),
                surplus_ratio=safe_ratio(surplus, income),
                reserve_months=safe_ratio(reserve, spending))


def compare_alternatives(project, assets, savings, years, rate, target,
                         extra_savings, extra_years, target_pct, rate_change):
    """기준안, 네 개의 단독 대안, 조합을 동일한 미래가치 함수로 비교."""
    adjusted_target = max(1.0, target * target_pct / 100)
    adjusted_rate = max(-99.0, min(100.0, rate + rate_change))
    adjusted_years = min(50, years + extra_years)
    specs = [
        ("기준안", savings, years, rate, target),
        ("월 저축액 증가", savings + extra_savings, years, rate, target),
        ("목표기간 연장", savings, adjusted_years, rate, target),
        ("목표금액 조정", savings, years, rate, adjusted_target),
        ("기대수익률 변경", savings, years, adjusted_rate, target),
        ("대안 조합", savings + extra_savings, adjusted_years, adjusted_rate, adjusted_target),
    ]
    return [dict(name=name, savings=s, years=y, rate=r, target=t,
                 result=project(assets, s, y, r, t)) for name, s, y, r, t in specs]


def render_app(project, won, legacy):
    import streamlit as st

    st.set_page_config(page_title="AFPK Young Planner", page_icon="📊", layout="wide")
    from design import apply_design, render_overview
    apply_design(st)

    def seed():
        case = st.session_state.get("start_mode", "김참직 사례로 시작하기") == "김참직 사례로 시작하기"
        st.session_state.pop("alt_base", None)
        # 다른 입력모드의 목표 배분 및 대안 설정이 섞이지 않게 초기화합니다.
        for k in list(st.session_state):
            if k.startswith(("p_", "f_", "g_", "a_")):
                del st.session_state[k]
        for k, (_, v) in ASSETS.items():
            st.session_state["f_" + k] = v if case else 0
        for k, (_, v) in FLOW.items():
            st.session_state["f_" + k] = v if case else 0
        st.session_state["g_asset_book"], st.session_state["g_monthly_book"] = default_allocations(case)
        for item in SAVINGS_ITEMS:
            st.session_state["f_monthly_" + item] = 200_000 if case else 0
        st.session_state["f_debt"] = 3_600_000 if case else 0
        profile = dict(name="김참직(가명)", age=32, job="국가직 7급 세무공무원", region="광주",
                       tenure=5, marital="미혼", marriage_age=35, children="결혼 후 1~2년 내 자녀 1명 계획",
                       risk="안정형/위험회피형", investment="개별주식·가상자산 투자 없음 / ETF를 통한 분산투자")
        for k, v in profile.items():
            st.session_state["p_" + k] = v if case else (30 if k == "age" else 35 if k == "marriage_age" else 0 if k == "tenure" else "")

    if "p_age" not in st.session_state:
        seed()
    if "g_asset_book" not in st.session_state:
        case = st.session_state.get("start_mode", "김참직 사례로 시작하기") == "김참직 사례로 시작하기"
        st.session_state["g_asset_book"], st.session_state["g_monthly_book"] = default_allocations(case)
        for item in SAVINGS_ITEMS:
            st.session_state.setdefault("f_monthly_" + item, 200_000 if case else 0)
    st.session_state["f_savings"] = sum(st.session_state["f_monthly_" + item] for item in SAVINGS_ITEMS)
    overview_assets = {k: st.session_state["f_" + k] for k in ASSETS}
    overview_balance = calculate_balance_sheet(overview_assets, {"loan": st.session_state["f_debt"]})
    overview_flow = calculate_cash_flow(**{k: st.session_state["f_" + k] for k in FLOW}, reserve=overview_assets["reserve"])
    render_overview(st, overview_balance, overview_flow)
    st.caption("공모전용 가상 사례 전용 · 실제 개인정보 입력 금지 · AI API 미사용 · 금액 단위: 원")
    tabs = st.tabs(["01 프로필", "02 재무상태", "03 재무목표", "04 목표 분석", "05 대안 비교", "06 인간 검토"])
    with tabs[0]:
        st.header("STEP 1. 고객 프로필")
        st.radio("시작 방식", ["김참직 사례로 시작하기", "직접 입력하기"], key="start_mode", on_change=seed, horizontal=True)
        if "p_age" not in st.session_state:
            seed()
        st.caption("시작 방식을 바꾸면 프로필·재무상태·목표별 설정이 초기화됩니다. 검토 메모는 유지되므로 다시 확인하세요.")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("이름 (가명만)", key="p_name")
            age = st.number_input("나이", 0, 120, key="p_age")
            st.text_input("직업", key="p_job")
            st.text_input("근무지역", key="p_region")
            st.number_input("재직기간 (약, 년)", 0, 80, key="p_tenure")
        with c2:
            st.text_input("혼인상태", key="p_marital")
            st.number_input("결혼 예정 나이 (세)", 0, 120, key="p_marriage_age")
            st.text_input("자녀 계획", key="p_children")
            st.text_input("투자성향", key="p_risk")
            st.text_input("투자 경험 및 방식", key="p_investment")

    with tabs[1]:
        st.header("STEP 2. 현재 재무상태")
        left, right = st.columns(2)
        assets = {}
        with left:
            st.subheader("자산")
            for k, (label, _) in ASSETS.items():
                assets[k] = st.number_input(label + " (원)", 0, 1_000_000_000_000, step=100_000, key="f_" + k)
        with right:
            st.subheader("부채")
            debt = st.number_input("자동차 할부잔액 (원)", 0, 1_000_000_000_000, step=100_000, key="f_debt")
            st.caption("부채비율 = 총부채 ÷ 총자산 · 순자산비율 = 순자산 ÷ 총자산")
        balance = calculate_balance_sheet(assets, {"car_loan": debt})
        for col, label, key in zip(st.columns(3), ["총자산", "총부채", "순자산"], ["total_assets", "total_debt", "net_assets"]):
            col.metric(label, won(balance[key]))
        st.subheader("월 현금흐름")
        flow_inputs = {}
        for col, (k, (label, _)) in zip(st.columns(3), list(FLOW.items())[:3]):
            with col:
                flow_inputs[k] = st.number_input(label + " (원/월)", 0, 10_000_000_000, step=10_000, key="f_" + k)
        monthly_items = {}
        for col, (item, label) in zip(st.columns(3), SAVINGS_ITEMS.items()):
            monthly_items[item] = col.number_input(label + " 납입액 (원/월)", 0, 10_000_000_000,
                                                  step=10_000, key="f_monthly_" + item)
        flow_inputs["savings"] = sum(monthly_items.values())
        st.metric("전체 월 저축·투자", won(flow_inputs["savings"]))
        flow = calculate_cash_flow(**flow_inputs, reserve=assets["reserve"])
        st.caption("가처분소득 → 고정·변동 소비지출 → 저축·투자 → 잉여현금흐름")
        st.metric("월 잉여현금흐름", won(flow["surplus"]))
        if flow["surplus"] < 0:
            st.warning("월 현금흐름이 적자입니다. 지출·저축 계획을 검토하세요.")
        if flow_inputs["savings"] > flow_inputs["income"]:
            st.warning("월 저축액이 월 소득을 초과합니다. 추가 재원이나 입력 오류를 검토하세요.")
        ratios = [("고정지출률", flow["fixed_ratio"]), ("변동지출률", flow["variable_ratio"]),
                  ("총소비지출률", flow["spending_ratio"]), ("저축·투자율", flow["savings_ratio"]),
                  ("잉여현금흐름률", flow["surplus_ratio"]), ("부채비율", balance["debt_ratio"]),
                  ("순자산비율", balance["net_ratio"])]
        for start in range(0, len(ratios), 3):
            for col, (label, value) in zip(st.columns(3), ratios[start:start + 3]):
                col.metric(label, "계산 불가" if value is None else f"{value * 100:,.1f}%")
        months = flow["reserve_months"]
        st.metric("비상예비자금 개월 수", "계산 불가" if months is None else f"{months:,.2f}개월")
        st.caption("지출·저축·잉여 비율의 분모는 가처분소득입니다. 월 소비지출 = 고정지출 + 변동지출. "
                   "비상예비자금 개월 수 = 비상예비자금 ÷ 월 소비지출. 분모가 0이면 계산 불가로 표시합니다.")

    with tabs[2]:
        st.header("STEP 3. 재무목표")
        st.caption("김참직 사례의 목표 템플릿입니다. 직접 입력 모드에서도 참고용으로 제공하며, 아래에서 선택한 목표의 금액·기간을 수정할 수 있습니다. "
                   "단기: 2028–2029년 · 중기: 2030–2033년 · 장기: 2037년 이후 · 상시: 유지 목표")
        for k, (name, category, date, amount, _) in GOALS.items():
            if k in ("wedding", "lease"):
                continue
            detail = won(amount)
            if k == "wedding_lease":
                st.markdown("**● 2029년 · 단기 | 2029 결혼·주거 통합목표**  \n총 본인 필요자금 **60,000,000원**  \n└ 결혼자금 20,000,000원  \n└ 전세 본인 자기자금 40,000,000원")
                continue
            if k == "debt":
                detail = f"현재 할부잔액 {won(debt)} · 이자 별도 검토"
            elif k == "lease":
                detail = "전세보증금 가정 2억 원 = 본인 4,000만 원 + 배우자 4,000만 원 + 전세대출 1억 2,000만 원"
            elif k == "home":
                detail = "총 매입·부대비용 4억 2,000만 원 = 부부 자기자금 2억 2,000만 원 + 대출 2억 원"
            elif k == "retirement":
                detail = "현재가치 월 300만 원 생활비 확보"
            elif k == "suv":
                detail += " 이내 · 차량 매각대금을 별도로 더하지 않는 추가현금 목표"
            st.markdown(f"**● {date} · {category} | {name}**  \n{detail}")
        chosen = st.selectbox("분석할 목표", list(GOALS), index=0, format_func=lambda k: ("└ 개별 분석: " if k in ("wedding", "lease") else "") + GOALS[k][0], key="g_choice")
        st.caption("분석 대상은 한 번에 하나만 선택합니다. 통합목표와 하위 목표를 동시 계산하거나 결과를 다시 합산하지 않습니다.")
        if chosen in ("wedding", "lease"):
            st.warning("통합목표의 하위 목표만 따로 보는 분석입니다. 통합목표 결과와 합산하지 마세요.")
        name, category, date, default_target, goal_year = GOALS[chosen]
        base_year = st.number_input("분석 기준연도", 2020, 2100, 2026, key="g_base_year")
        prefix = "g_" + chosen + "_"
        default_years = max(1, min(50, (goal_year or base_year + 1) - base_year))
        if goal_year and goal_year <= base_year:
            st.warning("선택한 템플릿 목표연도가 기준연도 이전 또는 같은 해입니다. 기간을 다시 정하세요. 계산 함수의 최소기간은 1년입니다.")

        from allocation_ui import persistent_amount
        funding = None
        if chosen in ("lease", "wedding_lease"):
            st.subheader("전세 조달 구조")
            x, y = st.columns(2)
            lease_total = persistent_amount(x, "전세보증금 총액 (원)", "lease_total", 200_000_000, 1)
            own = persistent_amount(y, "전세 본인 부담 (원)", "lease_own", 40_000_000, 1)
            spouse = persistent_amount(x, "전세 배우자 부담 (원)", "lease_spouse", 40_000_000)
            loan = persistent_amount(y, "전세대출 (원)", "lease_loan", 120_000_000)
            funding = funding_structure(lease_total, own, spouse, loan)
            target = own
            if chosen == "wedding_lease":
                wedding = persistent_amount(st, "결혼자금 본인 부담 (원)", "wedding_target", 20_000_000, 1)
                target += wedding
                st.metric("통합 본인 필요자금", won(target))
                st.caption("2029년 결혼자금 + 전세 본인 부담을 함께 준비합니다. 같은 재원은 한 번만 반영합니다.")
        elif chosen == "home":
            x, y = st.columns(2)
            price = persistent_amount(x, "현재가치 주택 매입가격 (원)", "home_price", 400_000_000, 1)
            cost = persistent_amount(y, "취득·수리·이사비 가정 (원)", "home_cost", 20_000_000)
            equity = persistent_amount(x, "부부 자기자금 (원)", "home_equity", 220_000_000)
            own = persistent_amount(y, "자가 본인 부담 (원, 편집 가능한 가정)", "home_own", 110_000_000, 1)
            loan = persistent_amount(x, "주택대출 (원)", "home_loan", 200_000_000)
            if own > equity:
                st.error("자가 본인 부담은 부부 자기자금보다 클 수 없습니다. 금액을 수정해 주세요.")
                st.stop()
            funding = funding_structure(price + cost, own, equity - own, loan)
            target = own
            st.caption("본인 1억 1,000만 원은 부부 자기자금의 50%로 설정한 시연 가정입니다. 확정된 사례 정보가 아니므로 수정하세요. 물가·주택가격 상승은 미반영입니다.")
        elif chosen == "retirement":
            x, y = st.columns(2)
            monthly = x.number_input("현재가치 은퇴 월 생활비 목표 (원)", 1, 10_000_000_000, 3_000_000, step=100_000, key=prefix + "monthly")
            duration = y.number_input("은퇴 생활비 준비기간 (년, 가정)", 1, 50, 25, key=prefix + "duration")
            target = monthly * 12 * duration
            default_years = max(1, min(50, 60 - age))
            st.info("월 생활비를 일시금 목표와 직접 비교하지 않습니다. 월 생활비 × 12 × 준비기간으로 단순 환산합니다. "
                    "준비기간 25년·은퇴시점 60세는 편집 가능한 시뮬레이션 가정입니다. 연금·물가·은퇴 후 운용수익·인출위험은 반영하지 않습니다.")
        else:
            if chosen == "debt":
                target = debt
                st.metric("상환 준비금 목표 (현재 할부잔액 연동)", won(target))
                st.caption("현재 잔액을 준비하는 계산이며, 기간 중 할부 납부·이자·잔액 감소를 예측하지 않습니다.")
            elif chosen == "wedding":
                target = persistent_amount(st, "결혼자금 본인 부담 (원)", "wedding_target", 20_000_000, 1)
            else:
                target = st.number_input("선택 목표금액 (원)", 1, 1_000_000_000_000, default_target, step=100_000, key=prefix + "target")
        if funding is not None:
            st.table([{"조달 항목": k, "금액": won(v)} for k, v in funding.items()])
            if funding["조달 차액 (합계 − 총액)"] != 0:
                st.warning("조달계획 합계와 총 필요자금이 일치하지 않습니다. 본인 부담 분석과 별도로 검토하세요.")
            st.caption("배우자 부담·대출은 본인 분석 재원에 더하지 않습니다. 대출 승인·한도·상환능력은 별도 검토가 필요합니다.")

        components = {"결혼예산": wedding, "전세 본인 자기자금": own} if chosen == "wedding_lease" else {name: target}
        if chosen == "wedding_lease":
            st.markdown(f"**현재 통합목표 · 총 본인 필요자금 {won(target)}**  \n└ 결혼자금 {won(wedding)}  \n└ 전세 본인 자기자금 {won(own)}")
        if chosen == "reserve":
            reserve_gap = assets["reserve"] - target
            st.metric("현재 비상예비자금 유지 목표 대비 차액", won(reserve_gap))
            st.info("상시 유지 목표는 현재 잔액과 먼저 비교합니다. 아래 미래가치는 추가 적립 시뮬레이션이며, 기간 중 인출에 따른 유지 여부는 판정하지 않습니다.")

    with tabs[3]:
        st.header("STEP 4. 목표 달성 가능성 분석")
        st.caption(f"선택 목표: {name} · {date}")
        from allocation_ui import render_allocations
        available, savings, allocated, payments, ledger_rows = render_allocations(
            st, chosen, assets, monthly_items, GOALS, ASSETS, won)
        st.write("**선택 목표에 실제 반영되는 재원**")
        st.table([{"항목": ASSETS[k][0], "현재 자산": won(v)} for k, v in allocated.items()])
        st.table([{"월 납입 항목": SAVINGS_ITEMS[k], "반영액": won(v)} for k, v in payments.items()])
        x, y = st.columns(2)
        x.metric("현재 활용 가능한 금융자산", won(available))
        y.metric("현재 월 저축액 (목표 배분)", won(savings))
        years = x.number_input("목표기간 (년, 분석용)", 1, 50, default_years, key=prefix + f"years_{base_year}")
        rate = y.number_input("예상 연수익률 (%, 분석용)", -99.0, 100.0, 3.0, step=0.1, key=prefix + "rate")
        st.caption(f"계산상 목표시점: {base_year + years}년 · {age + years}세. 날짜 범위 목표는 기본적으로 마지막 연도를 사용합니다.")
        st.subheader("시점별 저축 시나리오")
        transition_enabled = st.checkbox("차량할부 종료 후 절감액을 목표저축으로 전환", value=False, key="g_transition_enabled")
        sx, sy, sz = st.columns(3)
        payment = sx.number_input("현재 자동차 할부 월 납입액 (원)", 0, 10_000_000_000, 162_000,
                                  step=1_000, key="g_transition_payment")
        sx.caption(f"입력 금액: {won(payment)}")
        residual = sy.number_input("할부 잔존기간 (개월)", 1, 600, 24, key="g_transition_months")
        transfer_pct = sz.number_input("종료 후 목표저축 전환율 (%)", 0.0, 100.0, 100.0, step=50.0, key="g_transition_pct")
        st.caption("현재 고정지출에 이 할부 납입액이 포함되어 있다고 가정합니다. 마지막 할부를 낸 다음 달부터 전환합니다. 선택한 분석에만 적용하는 시나리오이며 다른 목표에 중복 적용해 합산하지 마세요.")
        if transition_enabled and (debt <= 0 or payment > flow_inputs["fixed"]):
            st.error("할부 잔액이 있어야 하며 월 납입액은 현재 고정지출 이하여야 합니다. 입력값 또는 전환 옵션을 수정하세요.")
            st.stop()
        transition = SavingsTransition(transition_enabled, payment, residual, transfer_pct)
        schedule_notes = schedule_description(savings, years * 12, transition, won)
        for line in schedule_notes:
            st.write(line)
        def scenario_project(a, s, y, r, t):
            return project_with_transition(project, a, s, y, r, t, transition)
        if target > 0:
            result = scenario_project(available, savings, years, rate, target)
            for col, label, value in zip(st.columns(3), ["목표시점 예상자산", "선택 목표금액", "초과금액" if result.gap >= 0 else "부족금액"], [result.total, target, abs(result.gap)]):
                col.metric(label, won(value))
            st.metric("목표달성률", f"{result.total / target * 100:,.1f}%")
            st.progress(min(1.0, max(0.0, result.total / target)), text="목표금액 대비 예상자산 · 막대는 100%까지 표시")
            (st.success if result.gap >= 0 else st.warning)("단순 계산상 목표달성 가능" if result.gap >= 0 else "단순 계산상 목표달성 어려움")
            x, y = st.columns(2)
            x.metric("기존 자산 미래가치", won(result.assets_fv))
            y.metric("적립 저축 미래가치", won(result.savings_fv))
        else:
            st.success("자동차 할부잔액이 0원이므로 현재 상환 목표가 완료된 상태입니다. 추가 적립 분석은 필요하지 않습니다.")
        st.warning("단순 모델: 세금·물가·수수료·소득변화·수익률 변동·부채 이자와 상환은 미반영입니다. "
                   "선택한 할부 종료 시나리오 외의 부채 현금흐름은 미반영입니다. 미래 금융자산에서 부채를 자동 차감하지 않습니다. 달성률은 확률이나 수익 보장이 아닙니다.")
        with st.expander("기존 미래가치 계산식"):
            st.markdown("`n = 기간 × 12`, `i = (1 + 연수익률/100)^(1/12) − 1`\n\n"
                        "- 현재 자산 미래가치 = 자산 × `(1+i)^n`\n"
                        "- 월말 저축 미래가치 = 월 저축액 × `((1+i)^n−1)/i`\n"
                        "- 수익률 0%이면 월 저축액 × `n`\n"
                        "- 예상자산 = 두 미래가치의 합계\n"
                        "- 차액 = 예상자산 − 목표금액\n\nV0.1의 Python 계산 함수를 변경 없이 재사용합니다.")
        with st.expander("주택목표 상세분석 · 기존 V0.1 계산기"):
            st.info("기존 계산 화면을 보존한 별도 시나리오입니다. 주택에 쓸 자산·월 저축·목표금액을 아래에서 직접 입력하세요. "
                    "이 독립 계산기는 배분 원장·본 분석·다운로드 리포트에 합산되지 않습니다. STEP 3의 조달 구조는 위 분석에 반영됩니다.")
            legacy()

    rows, table = [], []
    with tabs[4]:
        st.header("STEP 5. 대안 비교")
        if target > 0:
            st.info("수정할 값은 아래 입력란에 넣으세요. 숫자를 입력한 뒤 Enter를 누르거나 다른 칸을 선택하면 결과가 바뀝니다. 아래 결과 표는 읽기 전용입니다.")
            mode = st.radio("대안 입력 방식", ["최종 값 직접 입력", "증감으로 조정"], horizontal=True, key="alt_mode")
            base_signature = (chosen, savings, years, rate, target)
            if st.session_state.get("alt_base") != base_signature or any(k not in st.session_state for k in ("a_direct_savings", "a_direct_years", "a_direct_target", "a_direct_rate")):
                st.session_state["alt_base"] = base_signature
                st.session_state.update(a_direct_savings=float(savings + 100_000), a_direct_years=min(50, years + 1),
                                        a_direct_target=float(max(1, target * .9)), a_direct_rate=min(100.0, rate + 1))
            x, y = st.columns(2)
            if mode == "최종 값 직접 입력":
                direct_savings = x.number_input("대안 월 저축액 (원)", 0.0, 20_000_000_000.0, step=10000.0, format="%.0f", key="a_direct_savings")
                direct_years = y.number_input("대안 목표기간 (년)", 1, 50, key="a_direct_years")
                direct_target = x.number_input("대안 목표금액 (원)", 1.0, 20_000_000_000_000.0, step=100000.0, format="%.0f", key="a_direct_target")
                direct_rate = y.number_input("대안 연수익률 (%)", -99.0, 100.0, step=.1, key="a_direct_rate")
                extra, more_years = direct_savings - savings, direct_years - years
                pct, delta_rate = direct_target / target * 100, direct_rate - rate
                st.caption("목표 또는 기준 분석값을 바꾸면 직접 입력 대안도 새 기준으로 초기화됩니다. 월 저축 감소·기간 단축도 비교할 수 있습니다.")
            else:
                extra = x.number_input("추가 월 저축액 (원)", 0, 10_000_000_000, 100_000, step=10_000, key="a_extra")
                more_years = y.number_input("목표기간 추가 (년)", 0, 49, 1, key="a_years")
                pct = x.number_input("조정 목표금액 (기준 목표의 %)", 1.0, 200.0, 90.0, step=5.0, key="a_pct")
                delta_rate = y.number_input("기대수익률 변경폭 (%p)", -199.0, 199.0, 1.0, step=0.1, key="a_rate")
            selected_component = st.selectbox("예산 조정 대상", list(components), key="a_component")
            adjusted_total = max(1.0, target * pct / 100)
            try:
                adjusted_components = adjust_components(components, adjusted_total, selected_component)
            except ValueError as error:
                st.error(str(error))
                st.stop()
            component_explanation = describe_components(components, adjusted_components, won)
            for line in component_explanation:
                st.write(line)
            housing_reduction = (components[selected_component] - adjusted_components[selected_component]
                                 if chosen in ("lease", "home") or selected_component == "전세 본인 자기자금" else 0)
            funding_note = (f"주거 자기자금 {won(housing_reduction)} 감소: 배우자 부담·대출 증가 또는 주거비 축소 등 별도 조달계획 검토 필요. 대출이나 배우자 자금이 자동으로 늘어나지는 않습니다."
                            if housing_reduction > 0 else "")
            if funding_note:
                st.warning(funding_note)
            st.button("대안 다시 계산", key="recalculate_alternatives", type="primary")
            risk_note = RATE_WARNING if min(100, max(-99, rate + delta_rate)) > rate else "기대수익률은 보장되지 않으며 손실 가능성이 있습니다."
            st.warning(risk_note)
            st.caption("입력 투자성향: " + st.session_state.get("p_risk", "미입력") + " · 수익률 상승만으로 대안의 우열을 판단하지 않습니다.")
            st.caption("기간은 최대 50년, 변경 후 수익률은 -99~100%로 제한됩니다. 표에 실제 적용값을 표시합니다.")
            rows = compare_alternatives(scenario_project, available, savings, years, rate, target, extra, more_years, pct, delta_rate)
            names = action_names(rows, savings, years, rate, components, adjusted_components, selected_component, won)
            for row, action in zip(rows, names):
                row["name"] = action
            combined = rows[-1]["result"]
            cards = st.columns(3)
            cards[0].metric("대안 조합 예상자산", won(combined.total), delta=won(combined.total - rows[0]["result"].total))
            cards[1].metric("대안 조합 목표달성률", f"{combined.total / rows[-1]['target'] * 100:.1f}%")
            cards[2].metric("대안 조합 부족/초과", ("초과 " if combined.gap >= 0 else "부족 ") + won(abs(combined.gap)))
            st.subheader("복합 조정안의 변경 조건")
            combo = rows[-1]
            combo_explanation = [f"월 저축: {won(savings)} → {won(combo['savings'])}",
                                 f"목표기간: {years}년 → {combo['years']}년",
                                 f"목표금액: {won(target)} → {won(combo['target'])}",
                                 f"기대수익률: {rate:g}% → {combo['rate']:g}%"]
            for line in combo_explanation:
                st.write(line)
            st.info("모든 조건 변경을 동시에 적용한 결과입니다. 각 단독 대안의 결과를 합산한 값이 아닙니다.")
            table = []
            for index, row in enumerate(rows):
                r = row["result"]
                row_remaining, cautions, verdict = assess_alternative(row, flow["surplus"], savings, years, rate,
                                      "주거 조달계획 재검토" if index in (3, 5) and funding_note else "")
                now_surplus, later_surplus = surplus_after_transition(flow["surplus"], row['savings'] - savings, row['years'] * 12, transition)
                stages = schedule_description(row['savings'], row['years'] * 12, transition, won)
                row['schedule_notes'] = stages
                row['now_surplus'], row['later_surplus'] = now_surplus, later_surplus
                row['verdict'] = verdict
                table.append({"대안": row["name"], "월 저축": won(row["savings"]), "기간": f'{row["years"]}년',
                              "연수익률": f'{row["rate"]:.2f}%', "목표금액": won(row["target"]),
                              "예상자산": won(r.total), "부족/초과": ("초과 " if r.gap >= 0 else "부족 ") + won(abs(r.gap)),
                              "달성률": f'{r.total / row["target"] * 100:.1f}%',
                              "변경 후 잉여현금흐름": won(now_surplus),
                              "할부 종료 후 잉여": won(later_surplus) if later_surplus is not None else "기간 내 전환 없음",
                              "목표 지연 여부": f"{row['years'] - years}년 연기" if row['years'] > years else "없음",
                              "위험/주의사항": " · ".join(cautions) or "실행조건 검토 필요",
                              "저축 시점별 내역": " / ".join(stages),
                              "하위 목표 변경": " / ".join(component_explanation) if index in (3, 5) else "기준 목표 유지",
                              "판정": verdict})
            st.dataframe(table, hide_index=True)
            st.caption("‘계산상 가능’은 수학적 목표 충족일 뿐 실행 추천이 아닙니다. 월 잉여 5만 원 미만을 유동성 주의로 표시하는 것은 단순 시연 기준이며 공인 재무진단 기준이 아닙니다.")
            if transition.enabled:
                st.write("복합 조정안의 시점별 저축: " + " / ".join(rows[-1]['schedule_notes']))
            remaining, later_remaining = surplus_after_transition(flow["surplus"], extra, rows[-1]['years'] * 12, transition)
            if later_remaining is not None:
                st.metric("복합안 할부 종료 후 월 잉여현금흐름", won(later_remaining))
            st.metric("저축 증액 후 월 잉여현금흐름", won(remaining))
            st.caption("기존 전체 저축·투자는 유지하고 추가 월 저축액을 더 납입한다고 가정합니다. 목표 연장은 결혼·진학 등 일정상 제약을 따로 검토해야 합니다.")
            cash_note = cashflow_interpretation(flow["surplus"], remaining, extra, won)
            (st.error if remaining <= 0 else st.warning if extra > 0 and remaining < 50_000 else st.info)(cash_note)
        else:
            st.info("상환할 잔액이 없습니다. 다른 목표를 선택하면 대안을 비교할 수 있습니다.")

    with tabs[5]:
        st.header("STEP 6. 인간 검토")
        st.info("계산 결과는 참고자료이며 최종 재무설계 판단은 사용자가 검토해야 합니다.")
        st.text_area("인간 검토 메모", key="review_notes", height=160,
                     placeholder="가정의 한계, 자금 중복배분, 부채 상환, 목표 우선순위, 투자위험 및 최종 판단을 기록하세요.")
        st.caption("메모는 현재 접속 세션에서만 유지되며 영구 저장되지 않습니다. 새로고침·연결 종료 시 사라질 수 있습니다. 입력이나 사례 변경 후 기존 메모를 다시 검토하세요.")

        st.subheader("나의 재무설계 리포트")
        st.write("현재 고객정보, 재무상태, 선택 목표, 대안 비교와 검토 메모를 한 문서로 받아보세요.")
        st.caption("입력과 메모를 수정한 뒤 Enter 또는 다른 칸 클릭으로 반영해 주세요. HTML 파일은 인터넷 없이 열 수 있고, 브라우저 인쇄에서 PDF로 저장할 수 있습니다.")
        from report import build_report
        profile_labels = {"name":"가명", "age":"나이", "job":"직업", "region":"근무지역", "tenure":"재직기간(년)", "marital":"혼인상태", "marriage_age":"결혼 예정 나이", "children":"자녀 계획", "risk":"투자성향", "investment":"투자 방식"}
        sections = [
            ("01 고객 프로필", ["항목", "입력값"], [[label, st.session_state.get("p_" + k, "")] for k, label in profile_labels.items()]),
            ("02 재무상태", ["항목", "금액"], [[ASSETS[k][0], won(v)] for k, v in assets.items()] + [["총자산",won(balance["total_assets"])],["총부채",won(debt)],["순자산",won(balance["net_assets"])]]),
            ("월 현금흐름", ["항목", "금액"], [[FLOW[k][0],won(v)] for k,v in flow_inputs.items()] + [["월 잉여현금흐름",won(flow["surplus"])]]),
            ("재무비율", ["지표", "값"], [[label, "계산 불가" if v is None else f"{v*100:.1f}%"] for label,v in ratios] + [["비상자금 개월 수", "계산 불가" if months is None else f"{months:.2f}개월"]]),
            ("03 목표 타임라인 (사례 템플릿)", ["목표", "분류", "시점", "기본 목표"], [[v[0],v[1],v[2],won(v[3]) + ("/월" if k=="retirement" else "")] for k,v in GOALS.items() if k not in ("wedding", "lease")] + [["└ 통합목표 구성", "하위 목표", "2029년", "결혼 20,000,000원 + 전세 본인 40,000,000원 (중복 합산 금지)"]]),
            ("04 선택 목표 분석", ["조건", "현재 값"], [["목표",name],["분석 기준연도",base_year],["본인 목표금액",won(target)],["기간",f"{years}년"],["연수익률",f"{rate:.2f}%"],["활용 자산",won(available)],["월 저축 배분액",won(savings)]]),
        ]
        sections.extend([
            ("배분 해석", ["항목", "설명"], [["초기 배분", "자산·월 납입의 결혼/전세 분할은 편집 가능한 시연 가정입니다."],
             ["중복 합산 금지", "통합목표는 결혼과 전세 개별 배분의 합입니다. 통합 결과에 개별 결과를 다시 더하지 않습니다."]]),
            ("전체 목표 배분 원장", ["구분", "재원", "목표", "배분액", "배분율"], ledger_rows),
            ("선택 목표 반영 자산", ["항목", "금액"], [[ASSETS[k][0], won(v)] for k, v in allocated.items()]),
            ("월 저축 항목 및 선택 목표 반영액", ["항목", "전체 납입액", "반영액"],
             [[SAVINGS_ITEMS[k], won(monthly_items[k]), won(v)] for k, v in payments.items()]),
        ])
        if funding is not None:
            sections.append(("주택 조달 구조", ["항목", "금액"], [[k, won(v)] for k, v in funding.items()]))
            if chosen == "home":
                sections.append(("자가 분담 가정", ["항목", "값"], [["부부 자기자금", won(equity)],
                    ["본인 분담", "초기값 50%는 시연 가정이며 편집 가능"]]))
            if chosen == "wedding_lease":
                sections.append(("통합목표 구성", ["항목", "본인 필요자금"],
                                 [["결혼", won(wedding)], ["전세", won(own)], ["합계", won(target)]]))
        elif chosen == "retirement":
            sections.append(("은퇴 가정", ["항목","값"], [["현재가치 월 생활비",won(monthly)],["생활비 준비기간",f"{duration}년"],["환산 방식","월 생활비 × 12 × 준비기간; 연금·은퇴 후 운용 미반영"]]))
        if target > 0:
            sections.append(("기준안 계산 결과", ["지표","값"], [["예상자산",won(result.total)],["기존 자산 미래가치",won(result.assets_fv)],["적립 미래가치",won(result.savings_fv)],["차액 (예상−목표)",won(result.gap)],["달성률",f"{result.total/target*100:.1f}%"]]))
            sections.append(("05 대안 비교", list(table[0]), [list(r.values()) for r in table]))
            sections.extend([
                ("목표금액 조정 내역", ["설명"], [[line] for line in component_explanation] + ([[funding_note]] if funding_note else [])),
                ("복합 조정안 변경 조건", ["설명"], [[line] for line in combo_explanation] + [["모든 조건 변경을 동시에 적용한 결과입니다."]]),
                ("대안 해석 및 위험", ["설명"], [[cash_note], [risk_note], ["월 잉여 5만 원 미만은 시연용 유동성 주의 기준이며 공인 재무진단 기준이 아닙니다."]]),
                ("기준안 시점별 저축", ["설명"], [[line] for line in schedule_notes]),
                ("복합안 시점별 저축", ["설명"], [[line] for line in rows[-1]['schedule_notes']]),
            ])
            sections.append(("대안 현금흐름 검토", ["항목","값"], [["월 저축 변경액",won(extra)],["변경 후 잉여현금흐름",won(remaining)]]))
        else:
            sections.append(("계산 결과",["상태"],[["자동차 할부잔액 0원: 상환 목표 완료. 대안 분석 없음."]]))
        report_bytes = build_report(sections, st.session_state.get("review_notes", ""))
        st.download_button("재무설계 리포트 다운로드 (.html)", report_bytes, file_name="young-planner-report.html", mime="text/html", key="download_report", type="primary")
        st.caption("서버 파일·DB에 영구 저장하지 않습니다. 내려받은 파일은 내 기기에 남으며, 입력 변경 후 다시 다운로드해야 합니다.")
