"""밝은 금융 앱 스타일. 계산·세션 데이터에는 영향을 주지 않습니다."""

def apply_design(st):
    st.markdown("""
<style>
:root { color-scheme: light; }
[data-testid="stAppViewContainer"], .stApp { background:#f4f7fb; color:#182b45; }
[data-testid="stHeader"] { background:rgba(244,247,251,.96); color:#182b45; }
.block-container { max-width:1180px; padding-top:3rem; padding-bottom:4rem; }
h1,h2,h3,h4, p, label { color:#182b45; }
h2 { font-size:1.45rem!important; letter-spacing:-.04em; padding-top:.8rem!important; }
h3 { font-size:1.12rem!important; }
[data-testid="stCaptionContainer"] p { color:#67788e!important; line-height:1.65; }
[data-testid="stWidgetLabel"] p { font-size:.87rem; font-weight:600; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea { background:#fff!important; color:#182b45!important; caret-color:#087f8c; }
[data-testid="stTextInput"] > div, [data-testid="stNumberInput"] > div,
[data-testid="stTextArea"] > div { background:#fff!important; border-color:#d8e2ed!important; border-radius:10px!important; }
[data-testid="stNumberInput"] button { background:#eef3f8!important; color:#476078!important; }
[data-baseweb="select"] > div { background:#fff!important; color:#182b45!important; border-color:#d8e2ed!important; border-radius:10px; }
[data-baseweb="select"] input { color:#182b45!important; }
[data-baseweb="popover"], [role="listbox"], [role="option"] { background:#fff!important; color:#182b45!important; }
[data-testid="stMetric"] { background:white; border:1px solid #e0e8f0; border-radius:14px; padding:18px 20px; min-height:110px; box-shadow:0 4px 16px #193b6010; }
[data-testid="stMetricLabel"] p { color:#66798d!important; font-size:.84rem; }
[data-testid="stMetricValue"] { color:#132d4d!important; font-size:clamp(1.25rem,2.3vw,1.85rem)!important; font-weight:650; letter-spacing:-.04em; }
[data-testid="stTabs"] [role="tablist"] { gap:6px; background:#e9eff6; padding:6px; border-radius:12px; border-bottom:0; overflow-x:auto; }
[data-testid="stTabs"] [role="tab"] { color:#60758c!important; padding:12px 17px; border-radius:8px; white-space:nowrap; }
[data-testid="stTabs"] [aria-selected="true"] { background:white!important; color:#087f8c!important; box-shadow:0 2px 6px #20364d12; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"], [data-testid="stTabs"] [data-baseweb="tab-border"] { background:transparent; }
[data-testid="stTabs"] [role="tabpanel"] { padding-top:14px; }
[data-testid="stExpander"] { background:white; border:1px solid #dde6ef; border-radius:12px; }
[data-testid="stExpander"] summary { color:#182b45!important; }
[data-testid="stAlert"] { border-radius:12px; }
[data-testid="stAlert"] p { color:inherit!important; }
[data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p { color:#253e58!important; }
[data-testid="stDataFrame"] { border:1px solid #dce6ef; border-radius:12px; }
hr { border-color:#dce5ee!important; }
.yp-brand { color:#087f8c; font-size:12px; font-weight:800; letter-spacing:.16em; margin:0 0 15px; }
.yp-hero { display:flex; justify-content:space-between; align-items:center; gap:20px; margin:6px 0 23px; }
.yp-hero h1 { font-size:clamp(1.9rem,4vw,2.65rem); color:#142c49; line-height:1.28; font-weight:750; letter-spacing:-.055em; margin:0 0 9px; padding:0; }
.yp-hero p { color:#667a91; font-size:14px; margin:0; line-height:1.7; }
.yp-badge { border:1px solid #bfdedb; background:#e6f4f1; color:#16756d; padding:8px 12px; border-radius:24px; font-size:12px; white-space:nowrap; }
.yp-summary { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin:16px 0 22px; }
.yp-card { background:#fff; border:1px solid #e0e8f0; border-radius:16px; padding:20px 22px; box-shadow:0 5px 20px #16365308; }
.yp-card.featured { background:#14344c; border-color:#14344c; }
.yp-card span { display:block; color:#6a7c90; font-size:13px; margin-bottom:10px; }
.yp-card strong { display:block; color:#193751; font-size:clamp(1.35rem,2.5vw,2rem); letter-spacing:-.04em; font-weight:700; }
.yp-card.featured span { color:#b9d5df; }.yp-card.featured strong { color:#fff; }
.yp-card small { display:block; color:#8393a4; font-size:11px; margin-top:9px; }
.yp-card.featured small { color:#acd0d6; }
@media(max-width:640px) {
 .block-container { padding:2rem 1rem; }.yp-hero { align-items:flex-start; }.yp-badge{display:none;}
 .yp-summary { gap:8px; grid-template-columns:1fr; }.yp-card { padding:12px 16px; border-radius:12px; display:grid; grid-template-columns:1fr auto; align-items:center; }
 .yp-card strong { font-size:1.35rem; }.yp-card span {font-size:12px; margin:0;}.yp-card small{font-size:10px; grid-column:1/-1; margin-top:3px;}
 [data-testid="stTabs"] [role="tab"] { padding:10px 12px; }
}
</style>
""", unsafe_allow_html=True)


def render_overview(st, balance, flow):
    # 숫자와 정적 텍스트만 삽입: 사용자 입력 문자열은 HTML에 넣지 않습니다.
    st.markdown(f"""
<div class="yp-brand">AFPK · YOUNG PLANNER</div>
<div class="yp-hero"><div><h1>내일을 준비하는<br>나의 재무 플랜</h1>
<p>현재를 살펴보고, 목표를 세우고, 가능한 선택을 비교하세요.</p></div>
<span class="yp-badge">가상 사례 시뮬레이터</span></div>
<div class="yp-summary">
 <div class="yp-card"><span>총자산</span><strong>{balance['total_assets']:,.0f}원</strong><small>보유 자산의 합계</small></div>
 <div class="yp-card featured"><span>순자산</span><strong>{balance['net_assets']:,.0f}원</strong><small>총자산 − 총부채</small></div>
 <div class="yp-card"><span>월 잉여현금흐름</span><strong>{flow['surplus']:,.0f}원</strong><small>지출·저축 후 남는 금액</small></div>
</div>
""", unsafe_allow_html=True)
