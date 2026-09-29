"""배분 편집 UI. 별도 세션 원장으로 목표 전환 시 숨겨진 위젯 값도 보존한다."""
from allocation import ASSET_SOURCES, SAVINGS_ITEMS, allocated_resources


def persistent_amount(container, label, key, default, minimum=0):
    import streamlit as st
    values = st.session_state.setdefault("g_funding_values", {})
    widget = "g_input_" + key
    def save():
        values[key] = st.session_state[widget]
    amount = container.number_input(label, minimum, 1_000_000_000_000,
                           value=values.get(key, default), step=100_000,
                           key=widget, on_change=save)
    container.caption(f"입력 금액: {amount:,.0f}원")
    return amount


def render_allocations(st, chosen, assets, monthly_items, goals, labels, won):
    names = {k: v[0] for k, v in goals.items() if k != "wedding_lease"}
    names["hold"] = "청약 유지 / 다른 용도로 보류"
    book = st.session_state["g_asset_book"]
    monthly = st.session_state["g_monthly_book"]
    st.caption("보유자산과 매달 저축하는 돈을 목표별로 나눕니다. 통합목표는 결혼·전세 배분을 합쳐 계산합니다.")
    editor = st.selectbox("배분을 수정할 목표", list(names), index=list(names).index("wedding"),
                          format_func=names.get, key="g_edit_goal")
    st.subheader(f"지금 수정 중: {names[editor]}")
    if chosen == "wedding_lease" and editor in ("wedding", "lease"):
        st.info("이 목표는 결혼·주거 통합목표의 일부입니다. 수정한 금액은 아래 통합목표 분석에도 반영됩니다.")
    elif editor != chosen:
        st.warning(f"수정 중인 목표와 분석 대상이 다릅니다. 지금은 ‘{names[editor]}’ 배분을 수정하고, 아래 결과는 ‘{goals[chosen][0]}’를 분석합니다. 분석 대상은 STEP 3에서 바꿀 수 있습니다.")
    total_assets = sum(entries.get(editor, 0) for entries in book.values())
    total_monthly = sum(monthly_items[source] * entries.get(editor, 0) / 100 for source, entries in monthly.items())
    a, b = st.columns(2)
    a.metric("이 목표에 쓸 보유자산", won(total_assets))
    b.metric("이 목표에 매달 모을 돈", won(total_monthly) + " / 월")
    def save(kind, source, goal, key):
        st.session_state[kind].setdefault(source, {})[goal] = st.session_state[key]
    with st.container(border=True):
        st.subheader("1. 지금 가진 돈에서 얼마를 쓸까요?")
        st.caption("현재 보유한 금액 중 이 목표에 한 번 배정할 돈입니다. 매달 납입하는 금액이 아닙니다.")
        for source in ASSET_SOURCES:
            key = f"g_alloc_{source}_{editor}"
            other = sum(v for g, v in book.get(source, {}).items() if g != editor)
            amount_col, context_col = st.columns([3, 2])
            amount = amount_col.number_input(f"{labels[source][0]}에서 이 목표에 쓸 돈 (원)", 0, 1_000_000_000_000,
                            value=int(book.get(source, {}).get(editor, 0)), step=100_000,
                            key=key, on_change=save, args=("g_asset_book", source, editor, key))
            amount_col.caption(f"입력 금액: {amount:,.0f}원")
            context_col.write(f"보유액 **{won(assets[source])}**")
            context_col.caption(f"다른 목표·보류에 {won(other)} 배정 중")
            room = assets[source] - other
            context_col.caption(f"이 목표에 배정 가능한 한도: {won(max(0, room))}")
            if amount > room:
                context_col.error(f"잔액 대비 {won(amount - room)} 초과 · 다른 목표 배분을 줄이거나 입력액을 수정하세요.")
    with st.container(border=True):
        st.subheader("2. 매달 모으는 돈에서 얼마를 나눌까요?")
        st.caption("STEP 2에 입력한 월 납입액을 나눕니다. 50%라면 매달 넣는 돈의 절반을 이 목표에 사용합니다.")
        for source, label in SAVINGS_ITEMS.items():
            key = f"g_monthly_{source}_{editor}"
            other_pct = sum(v for g, v in monthly.get(source, {}).items() if g != editor)
            amount_col, context_col = st.columns([3, 2])
            percent = amount_col.number_input(f"매달 {label} 중 이 목표에 넣을 비율 (%)", 0.0, 100.0,
                            value=float(monthly.get(source, {}).get(editor, 0)), step=5.0,
                            key=key, on_change=save, args=("g_monthly_book", source, editor, key))
            amount_col.write(f"월 {won(monthly_items[source])} × {percent:g}% = **월 {won(monthly_items[source] * percent / 100)}**")
            context_col.caption(f"다른 목표·보류에 {other_pct:g}% 배정 중")
            context_col.caption(f"이 목표에 배정 가능한 한도: {max(0, 100 - other_pct):g}%")
            if percent + other_pct > 100:
                context_col.error(f"전체 배분율 {percent + other_pct:g}% · 다른 목표 배분을 줄이거나 비율을 수정하세요.")
        st.caption("입력액은 Enter 또는 다른 칸 클릭 후 반영됩니다. 다른 목표의 돈을 자동으로 가져오지 않습니다.")
    asset_rows, monthly_rows = [], []
    for source in ASSET_SOURCES:
        assigned = sum(book.get(source, {}).values())
        asset_rows.append({"자산": labels[source][0], "잔액": won(assets[source]),
                           "전체 배분": won(assigned), "미배분": won(assets[source] - assigned)})
    for source, label in SAVINGS_ITEMS.items():
        percent = sum(monthly.get(source, {}).values())
        monthly_rows.append({"항목": label, "월 납입액": won(monthly_items[source]), "전체 배분율": f"{percent:g}%"})
    with st.expander("전체 재원의 잔액·배분 현황 확인"):
        st.write("현재 보유자산")
        st.dataframe(asset_rows, hide_index=True)
        st.write("월 납입액")
        st.dataframe(monthly_rows, hide_index=True)
    ledger_rows = []
    for kind, source_book in (("자산", book), ("월 납입", monthly)):
        for source, entries in source_book.items():
            for goal, value in entries.items():
                if value:
                    amount = value if kind == "자산" else monthly_items[source] * value / 100
                    ledger_rows.append([kind, labels[source][0] if kind == "자산" else SAVINGS_ITEMS[source],
                                        names[goal], won(amount), "—" if kind == "자산" else f"{value:g}%"])
    with st.expander("전체 목표 배분 원장 보기"):
        st.table([dict(zip(["구분", "재원", "목표", "배분액", "배분율"], row)) for row in ledger_rows])
    try:
        allocated, payments = allocated_resources(chosen, {s: assets[s] for s in ASSET_SOURCES},
                                                  monthly_items, book, monthly, names)
    except ValueError as error:
        message = str(error)
        message = message.replace("deposit:", "적금:")
        for source in ASSET_SOURCES:
            message = message.replace(source + ":", labels[source][0] + ":")
        st.error(message + " 배분을 수정할 때까지 목표 분석·대안 비교·리포트 다운로드를 중단합니다.")
        st.stop()
    st.caption("보증금·차량은 금융자산 배분에서 제외합니다. 비상예비자금과 청약의 인출 조건은 별도로 검토하세요.")
    return sum(allocated.values()), sum(payments.values()), allocated, payments, ledger_rows
