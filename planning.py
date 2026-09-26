"""AFPK 프로세스 데모 확장. 미래가치는 app.py의 기존 함수를 주입받아 재사용한다."""

import math


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
    st.title("AFPK Young Planner")
    st.caption("V0.2 · 고객 이해 → 재무상태 파악 → 목표 설정 → 분석 → 대안 비교 → 인간 검토")
    st.info("공모전용 가상 사례·재무설계 시뮬레이터입니다. 실제 개인정보를 입력하지 마세요. AI API를 사용하지 않습니다.")
    st.caption("금액 단위: 원 · 입력 변경 즉시 Python 함수로 재계산 · 수익률은 연 실효수익률")

    def seed():
        case = st.session_state.get("start_mode", "김참직 사례로 시작하기") == "김참직 사례로 시작하기"
        # 다른 입력모드의 목표 배분 및 대안 설정이 섞이지 않게 초기화합니다.
        for k in list(st.session_state):
            if k.startswith(("p_", "f_", "g_", "a_")):
                del st.session_state[k]
        for k, (_, v) in ASSETS.items():
            st.session_state["f_" + k] = v if case else 0
        for k, (_, v) in FLOW.items():
            st.session_state["f_" + k] = v if case else 0
        st.session_state["f_debt"] = 3_600_000 if case else 0
        profile = dict(name="김참직(가명)", age=32, job="국가직 7급 세무공무원", region="광주",
                       tenure=5, marital="미혼", marriage_age=35, children="결혼 후 1~2년 내 자녀 1명 계획",
                       risk="안정형/위험회피형", investment="개별주식·가상자산 투자 없음 / ETF를 통한 분산투자")
        for k, v in profile.items():
            st.session_state["p_" + k] = v if case else (30 if k == "age" else 35 if k == "marriage_age" else 0 if k == "tenure" else "")

    st.header("STEP 1. 고객 프로필")
    st.radio("시작 방식", ["김참직 사례로 시작하기", "직접 입력하기"], key="start_mode", on_change=seed)
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

    st.divider()
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
    for col, (k, (label, _)) in zip(st.columns(4), FLOW.items()):
        with col:
            flow_inputs[k] = st.number_input(label + " (원/월)", 0, 10_000_000_000, step=10_000, key="f_" + k)
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

    st.divider()
    st.header("STEP 3. 재무목표")
    st.caption("김참직 사례의 목표 템플릿입니다. 직접 입력 모드에서도 참고용으로 제공하며, 아래에서 선택한 목표의 금액·기간을 수정할 수 있습니다. "
               "단기: 2028–2029년 · 중기: 2030–2033년 · 장기: 2037년 이후 · 상시: 유지 목표")
    for k, (name, category, date, amount, _) in GOALS.items():
        detail = won(amount)
        if k == "debt":
            detail = f"현재 할부잔액 {won(debt)} · 이자 별도 검토"
        elif k == "lease":
            detail = "전세보증금 가정 2억 원 = 본인 4,000만 원 + 배우자 4,000만 원 + 전세대출 1억 2,000만 원"
        elif k == "home":
            detail = "현재가치 매입가격 4억 원 + 취득·수리·이사비 2,000만 원"
        elif k == "retirement":
            detail = "현재가치 월 300만 원 생활비 확보"
        elif k == "suv":
            detail += " 이내 · 차량 매각대금을 별도로 더하지 않는 추가현금 목표"
        st.markdown(f"**● {date} · {category} | {name}**  \n{detail}")
    chosen = st.selectbox("분석할 목표", list(GOALS), index=2, format_func=lambda k: GOALS[k][0], key="g_choice")
    name, category, date, default_target, goal_year = GOALS[chosen]
    base_year = st.number_input("분석 기준연도", 2020, 2100, 2026, key="g_base_year")
    prefix = "g_" + chosen + "_"
    default_years = max(1, min(50, (goal_year or base_year + 1) - base_year))
    if goal_year and goal_year <= base_year:
        st.warning("선택한 템플릿 목표연도가 기준연도 이전 또는 같은 해입니다. 기간을 다시 정하세요. 계산 함수의 최소기간은 1년입니다.")

    if chosen == "lease":
        x, y = st.columns(2)
        lease_total = x.number_input("전세보증금 가정 (원)", 1, 1_000_000_000_000, 200_000_000, step=1_000_000, key=prefix + "lease")
        own = y.number_input("본인 준비금 목표 (원)", 1, 1_000_000_000_000, 40_000_000, step=1_000_000, key=prefix + "own")
        spouse = x.number_input("배우자 준비금 가정 (원)", 0, 1_000_000_000_000, 40_000_000, step=1_000_000, key=prefix + "spouse")
        loan = y.number_input("전세대출 가정 (원)", 0, 1_000_000_000_000, 120_000_000, step=1_000_000, key=prefix + "loan")
        target = own
        funding_gap = own + spouse + loan - lease_total
        st.metric("전세 조달계획 차액 (합계 − 보증금)", won(funding_gap))
        if funding_gap != 0:
            st.warning("조달계획 합계와 전세보증금이 일치하지 않습니다. 본인 목표달성 여부와 별도로 검토하세요.")
        st.caption("STEP 4는 본인 준비금만 분석합니다. 배우자 자금·대출은 본인 금융자산에 더하지 않으며 대출 승인·한도·상환능력을 판단하지 않습니다.")
    elif chosen == "home":
        x, y = st.columns(2)
        price = x.number_input("현재가치 주택 매입가격 (원)", 1, 1_000_000_000_000, 400_000_000, step=1_000_000, key=prefix + "price")
        cost = y.number_input("취득·수리·이사비 가정 (원)", 0, 1_000_000_000_000, 20_000_000, step=1_000_000, key=prefix + "cost")
        target = price + cost
        st.caption("매입가격과 부대비용을 단순 합산한 목표입니다. 물가·주택가격 상승·대출은 미반영입니다.")
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
        else:
            target = st.number_input("선택 목표금액 (원)", 1, 1_000_000_000_000, default_target, step=100_000, key=prefix + "target")
    if chosen == "reserve":
        reserve_gap = assets["reserve"] - target
        st.metric("현재 비상예비자금 유지 목표 대비 차액", won(reserve_gap))
        st.info("상시 유지 목표는 현재 잔액과 먼저 비교합니다. 아래 미래가치는 추가 적립 시뮬레이션이며, 기간 중 인출에 따른 유지 여부는 판정하지 않습니다.")

    st.divider()
    st.header("STEP 4. 목표 달성 가능성 분석")
    st.caption(f"선택 목표: {name} · {date} · 목표들을 각각 독립적으로 분석합니다. 여러 목표에 같은 자금을 쓸 수 없으므로 결과를 합산하지 마세요.")
    st.write("**이 목표에 활용할 자산 선택**")
    selected = []
    for col, k in zip(st.columns(4), ["cash", "reserve", "etf", "subscription"]):
        default = (k == "reserve") if chosen == "reserve" else k in ("cash", "etf")
        if col.checkbox(ASSETS[k][0], value=default, key=prefix + k):
            selected.append(k)
    st.caption("보증금·차량은 활용 금융자산에서 제외합니다. 비상자금은 비상자금 목표 외에는 기본 제외합니다. 주택청약 등은 실제 인출 조건을 별도 검토하세요.")
    x, y = st.columns(2)
    asset_pct = x.number_input("선택 자산 중 이 목표 배분율 (%)", 0.0, 100.0, 100.0, step=5.0, key=prefix + "asset_pct")
    savings_pct = y.number_input("월 저축·투자 중 이 목표 배분율 (%)", 0.0, 100.0, 100.0, step=5.0, key=prefix + "savings_pct")
    available = sum(assets[k] for k in selected) * asset_pct / 100
    savings = flow_inputs["savings"] * savings_pct / 100
    x.metric("현재 활용 가능한 금융자산", won(available))
    y.metric("현재 월 저축액 (목표 배분)", won(savings))
    years = x.number_input("목표기간 (년, 분석용)", 1, 50, default_years, key=prefix + f"years_{base_year}")
    rate = y.number_input("예상 연수익률 (%, 분석용)", -99.0, 100.0, 3.0, step=0.1, key=prefix + "rate")
    st.caption(f"계산상 목표시점: {base_year + years}년 · {age + years}세. 날짜 범위 목표는 기본적으로 마지막 연도를 사용합니다.")
    if target > 0:
        result = project(available, savings, years, rate, target)
        for col, label, value in zip(st.columns(3), ["목표시점 예상자산", "선택 목표금액", "초과금액" if result.gap >= 0 else "부족금액"], [result.total, target, abs(result.gap)]):
            col.metric(label, won(value))
        st.metric("목표달성률", f"{result.total / target * 100:,.1f}%")
        (st.success if result.gap >= 0 else st.warning)("단순 계산상 목표달성 가능" if result.gap >= 0 else "단순 계산상 목표달성 어려움")
        x, y = st.columns(2)
        x.metric("기존 자산 미래가치", won(result.assets_fv))
        y.metric("적립 저축 미래가치", won(result.savings_fv))
    else:
        st.success("자동차 할부잔액이 0원이므로 현재 상환 목표가 완료된 상태입니다. 추가 적립 분석은 필요하지 않습니다.")
    st.warning("단순 모델: 세금·물가·수수료·소득변화·수익률 변동·부채 이자와 상환은 미반영입니다. "
               "미래 금융자산에서 부채를 자동 차감하지 않습니다. 달성률은 확률이나 수익 보장이 아닙니다.")
    with st.expander("기존 미래가치 계산식"):
        st.markdown("`n = 기간 × 12`, `i = (1 + 연수익률/100)^(1/12) − 1`\n\n"
                    "- 현재 자산 미래가치 = 자산 × `(1+i)^n`\n"
                    "- 월말 저축 미래가치 = 월 저축액 × `((1+i)^n−1)/i`\n"
                    "- 수익률 0%이면 월 저축액 × `n`\n"
                    "- 예상자산 = 두 미래가치의 합계\n"
                    "- 차액 = 예상자산 − 목표금액\n\nV0.1의 Python 계산 함수를 변경 없이 재사용합니다.")
    with st.expander("주택목표 상세분석 · 기존 V0.1 계산기"):
        st.info("기존 계산 화면을 보존한 별도 시나리오입니다. 주택에 쓸 자산·월 저축·목표금액을 아래에서 직접 입력하세요. "
                "STEP 3의 전세 조달계획 및 자가 비용 분해는 위 분석에 반영됩니다.")
        legacy()

    st.divider()
    st.header("STEP 5. 대안 비교")
    if target > 0:
        st.caption("각 단독 대안은 해당 조건만 바꿉니다. 마지막 행은 네 조건을 함께 적용합니다. 값 변경 시 즉시 재계산됩니다.")
        x, y = st.columns(2)
        extra = x.number_input("추가 월 저축액 (원)", 0, 10_000_000_000, 100_000, step=10_000, key="a_extra")
        more_years = y.number_input("목표기간 추가 (년)", 0, 49, 1, key="a_years")
        pct = x.number_input("조정 목표금액 (기준 목표의 %)", 1.0, 200.0, 90.0, step=5.0, key="a_pct")
        delta_rate = y.number_input("기대수익률 변경폭 (%p)", -199.0, 199.0, 1.0, step=0.1, key="a_rate")
        st.warning("기대수익률 상승에는 위험 증가와 손실 가능성이 따릅니다. 높은 수익률이 더 좋은 대안이라는 뜻은 아닙니다. 투자성향과 목표시점을 함께 검토하세요.")
        st.caption("기간은 최대 50년, 변경 후 수익률은 -99~100%로 제한됩니다. 표에 실제 적용값을 표시합니다.")
        rows = compare_alternatives(project, available, savings, years, rate, target, extra, more_years, pct, delta_rate)
        table = []
        for row in rows:
            r = row["result"]
            table.append({"대안": row["name"], "월 저축": won(row["savings"]), "기간": f'{row["years"]}년',
                          "연수익률": f'{row["rate"]:.2f}%', "목표금액": won(row["target"]),
                          "예상자산": won(r.total), "부족/초과": ("초과 " if r.gap >= 0 else "부족 ") + won(abs(r.gap)),
                          "달성률": f'{r.total / row["target"] * 100:.1f}%', "판정": "가능" if r.gap >= 0 else "어려움"})
        st.dataframe(table, hide_index=True)
        remaining = flow["surplus"] - extra
        st.metric("저축 증액 후 월 잉여현금흐름", won(remaining))
        st.caption("기존 전체 저축·투자는 유지하고 추가 월 저축액을 더 납입한다고 가정합니다. 목표 연장은 결혼·진학 등 일정상 제약을 따로 검토해야 합니다.")
        if remaining < 0:
            st.warning("이 저축 증액안은 현재 현금흐름으로 충당하기 어렵습니다. 지출 조정이나 추가 소득을 검토하세요.")
    else:
        st.info("상환할 잔액이 없습니다. 다른 목표를 선택하면 대안을 비교할 수 있습니다.")

    st.divider()
    st.header("STEP 6. 인간 검토")
    st.info("계산 결과는 참고자료이며 최종 재무설계 판단은 사용자가 검토해야 합니다.")
    st.text_area("인간 검토 메모", key="review_notes", height=160,
                 placeholder="가정의 한계, 자금 중복배분, 부채 상환, 목표 우선순위, 투자위험 및 최종 판단을 기록하세요.")
    st.caption("메모는 현재 접속 세션에서만 유지되며 영구 저장되지 않습니다. 새로고침·연결 종료 시 사라질 수 있습니다. 입력이나 사례 변경 후 기존 메모를 다시 검토하세요.")
