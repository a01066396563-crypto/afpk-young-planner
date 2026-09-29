"""KODEX 레퍼런스의 블루와 라운드 카드 구성을 적용한 AFPK UI."""

def apply_design(st):
    st.markdown('''
<style>
:root{color-scheme:light}
.stApp,[data-testid="stAppViewContainer"]{background:white;color:#151a2d}
[data-testid="stHeader"]{background:rgba(255,255,255,.96)}
.block-container{max-width:1280px;padding:3rem 2.5rem 5rem}
h1,h2,h3,h4,p,label{color:#151a2d}
h2{font-size:1.65rem!important;letter-spacing:-.045em;font-weight:750!important}h3{font-size:1.15rem!important}
[data-testid="stCaptionContainer"] p{color:#657084!important;line-height:1.7}
[data-testid="stWidgetLabel"] p{font-weight:600;font-size:.9rem}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea{background:#f7f8fb!important;color:#151a2d!important;caret-color:#1746f5}
[data-testid="stTextInput"] > div,[data-testid="stNumberInput"] > div,[data-testid="stTextArea"] > div{background:#f7f8fb!important;border:1px solid #e2e6ef;border-radius:12px!important}
[data-testid="stNumberInput"] button{background:#edf1fa!important;color:#33415a!important}
[data-baseweb="select"] > div{background:#f7f8fb!important;color:#151a2d!important;border-color:#e2e6ef!important;border-radius:12px}
[data-baseweb="popover"],[role="listbox"],[role="option"]{background:white!important;color:#151a2d!important}
[data-testid="stTabs"] [role="tablist"]{gap:0;border-bottom:2px solid #e9ecf3;background:white;overflow-x:auto;padding:0}
[data-testid="stTabs"] [role="tab"]{flex:1 0 auto;min-height:64px;padding:14px 24px;border-radius:0;color:#71798a;white-space:nowrap;font-weight:650}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{color:#1746f5!important;border-bottom:3px solid #1746f5;background:#f5f7ff}
[data-testid="stTabs"] [role="tabpanel"]{padding-top:28px}
[data-testid="stMetric"]{background:#f6f8fc;border:1px solid #e9edf6;border-radius:20px;padding:22px;min-height:122px;box-shadow:none}
[data-testid="stMetricLabel"] p{font-size:.88rem;color:#5c677d!important}
[data-testid="stMetricValue"]{font-size:clamp(1.3rem,2.3vw,2rem)!important;font-weight:750;color:#14255d;letter-spacing:-.04em;font-variant-numeric:tabular-nums}
[data-testid="stExpander"]{background:white;border:1px solid #dfe5ef;border-radius:16px}
[data-testid="stAlert"]{border-radius:14px}[data-testid="stAlert"] p{color:inherit!important}
[data-testid="stDataFrame"],[data-testid="stTable"]{border-radius:14px;overflow:hidden;border:1px solid #e4e8f0}
[data-testid="stButton"] button,[data-testid="stDownloadButton"] button{min-height:48px;border-radius:28px;font-weight:650;padding:10px 24px}
button[kind="primary"]{background:#1746f5!important;border-color:#1746f5!important;color:white!important}button[kind="primary"] p{color:white!important}
button:focus-visible,a:focus-visible{outline:3px solid #6889ff!important;outline-offset:3px}
.yp-masthead{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:4px 0 28px;border-bottom:1px solid #edf0f5;margin-bottom:30px}
.yp-logo{font-size:28px;line-height:1.15;font-weight:850;letter-spacing:-1.3px;color:#1746f5}.yp-logo small{display:block;font-size:10px;font-weight:700;letter-spacing:2px;margin-top:7px;color:#68748b}
.yp-topline{font-size:12px;font-weight:650;color:#6d7586}.yp-edition{background:#1746f5;color:white;border-radius:30px;padding:9px 17px;font-size:12px;font-weight:700}
.yp-hero{display:grid;grid-template-columns:1.5fr 1fr;align-items:center;gap:28px;position:relative;overflow:hidden;border-radius:28px;background:#eaf0ff;padding:42px 46px;margin-bottom:24px}
.yp-eyebrow{color:#1746f5;font-size:12px;font-weight:750;letter-spacing:.09em;margin:0 0 18px}
.yp-hero h1{font-size:clamp(2rem,3.8vw,3.5rem);line-height:1.22;letter-spacing:-.065em;font-weight:800;padding:0;margin:0 0 18px;color:#111d42}.yp-hero h1 em{font-style:normal;color:#1746f5}
.yp-hero p{font-size:14px;line-height:1.75;color:#596781;margin:0}.yp-tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:24px}.yp-tags span{background:white;border-radius:20px;padding:7px 12px;color:#3e537f;font-size:12px;font-weight:600}
.yp-art{position:relative;min-height:236px;display:flex;align-items:center;justify-content:center}.yp-orbit{width:230px;height:230px;border-radius:50%;background:#d3dfff;position:absolute;right:0;top:5px}
.yp-plan{z-index:1;position:relative;width:260px;border-radius:22px;background:#1746f5;padding:24px;box-shadow:12px 16px 0 #bed0ff;transform:rotate(-5deg);color:white}.yp-plan small{font-size:11px;color:#cbd8ff;letter-spacing:1px}.yp-plan strong{display:block;font-size:24px;font-weight:750;line-height:1.4;margin:9px 0 20px;color:white;letter-spacing:-1px}
.yp-bars{display:flex;align-items:flex-end;gap:10px;height:62px;border-bottom:1px solid #6083ff;padding-bottom:8px}.yp-bars i{display:block;background:#88a6ff;border-radius:6px 6px 0 0;width:36px;height:24px}.yp-bars i:nth-child(2){height:35px;background:#a8bdff}.yp-bars i:nth-child(3){height:45px;background:#c6d4ff}.yp-bars i:nth-child(4){height:55px;background:white}.yp-plan-foot{font-size:10px;color:#dae3ff;margin-top:10px}
.yp-summary-title{display:flex;justify-content:space-between;align-items:center;margin:26px 0 14px}.yp-summary-title strong{font-size:20px;letter-spacing:-.6px}.yp-summary-title span{font-size:12px;color:#7c8494}
.yp-summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-bottom:22px}.yp-card{background:#f5f6f9;border-radius:20px;padding:24px 26px}.yp-card:nth-child(2){background:#eef0ff}.yp-card:nth-child(3){background:#eaf6f4}.yp-card span{display:block;font-size:13px;font-weight:600;color:#536079;margin-bottom:14px}.yp-card strong{display:block;font-size:clamp(1.3rem,2.35vw,2rem);font-weight:800;letter-spacing:-.055em;color:#162446;font-variant-numeric:tabular-nums}.yp-card small{display:block;font-size:11px;color:#67758d;margin-top:12px}
@media(max-width:760px){.block-container{padding:2rem 1rem 3rem}.yp-masthead{gap:10px;padding-bottom:20px;margin-bottom:20px}.yp-logo{font-size:23px}.yp-topline{display:none}.yp-edition{font-size:10px;padding:7px 10px}.yp-hero{padding:28px 24px;grid-template-columns:1fr;gap:8px;border-radius:22px}.yp-hero h1{font-size:2.3rem}.yp-art{min-height:175px}.yp-plan{width:215px;padding:17px;transform:rotate(-4deg)}.yp-plan strong{font-size:19px;margin:6px 0 10px}.yp-orbit{width:160px;height:160px;right:15%}.yp-bars{height:48px}.yp-bars i:nth-child(4){height:43px}.yp-plan-foot{display:none}.yp-summary{gap:8px}.yp-card{padding:17px 12px;border-radius:15px}.yp-card span{font-size:11px;margin-bottom:10px}.yp-card strong{font-size:clamp(.85rem,3.3vw,1.4rem)}.yp-card small{font-size:10px;line-height:1.5;margin-top:9px}[data-testid="stTabs"] [role="tab"]{padding:12px 17px;font-size:13px;min-height:54px}[data-testid="stMetric"]{padding:18px;min-height:105px}}
</style>
''', unsafe_allow_html=True)


def render_overview(st, balance, flow):
    # 정적 문구와 계산 숫자만 HTML에 삽입한다.
    st.markdown(f'''
<div class="yp-masthead"><div class="yp-logo">Young Planner<small>AFPK FINANCIAL PLANNING</small></div><span class="yp-topline">나의 오늘을 이해하고, 내일을 준비하다</span><span class="yp-edition">CHALLENGE DEMO</span></div>
<div class="yp-hero"><div><div class="yp-eyebrow">MY FINANCIAL PLAN</div><h1>꿈꾸는 내일,<br><em>계획은 오늘부터.</em></h1><p>결혼부터 주거, 그리고 은퇴까지.<br>나의 자산과 저축으로 목표에 얼마나 가까워졌는지 확인해 보세요.</p><div class="yp-tags"><span>목표별 자금 배분</span><span>대안 비교</span><span>나만의 리포트</span></div></div><div class="yp-art" aria-hidden="true"><div class="yp-orbit"></div><div class="yp-plan"><small>YOUNG PLANNER</small><strong>오늘의 준비가<br>내일의 가능성으로</strong><div class="yp-bars"><i></i><i></i><i></i><i></i></div><div class="yp-plan-foot">PLAN · COMPARE · REVIEW</div></div></div></div>
<div class="yp-summary-title"><strong>나의 재무 한눈에 보기</strong><span>입력한 재무정보 기준</span></div>
<div class="yp-summary"><div class="yp-card"><span>총자산</span><strong>{balance['total_assets']:,.0f}원</strong><small>보유 자산의 합계</small></div><div class="yp-card"><span>순자산</span><strong>{balance['net_assets']:,.0f}원</strong><small>총자산 − 총부채</small></div><div class="yp-card"><span>월 잉여현금흐름</span><strong>{flow['surplus']:,.0f}원</strong><small>지출·저축 후 남는 금액</small></div></div>
''', unsafe_allow_html=True)
