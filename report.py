"""세션의 계산 결과를 독립 HTML 문서로 변환. 디스크·DB·외부 API 사용 없음."""
from html import escape
from datetime import datetime, timezone, timedelta


def build_report(sections, note):
    """sections: (제목, 열 이름 목록, 행 목록). 모든 사용자 문자열을 escape한다."""
    timestamp = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST")
    content = []
    for title, columns, rows in sections:
        header = ''.join(f'<th>{escape(str(c))}</th>' for c in columns)
        body = ''.join('<tr>' + ''.join(f'<td>{escape(str(v))}</td>' for v in row) + '</tr>' for row in rows)
        content.append(f'<section><h2>{escape(title)}</h2><div class="table"><table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table></div></section>')
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Young Planner 재무설계 리포트</title><style>
*{{box-sizing:border-box}}body{{font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;background:#f4f6fa;color:#263445;margin:0;line-height:1.65}}
main{{max-width:1020px;margin:32px auto;background:white;padding:48px;border-radius:24px}}header{{border-bottom:3px solid #367bf5;padding-bottom:24px}}
.brand{{color:#367bf5;letter-spacing:.12em;font-size:12px;font-weight:bold}}h1{{font-size:30px;letter-spacing:-1px;margin:12px 0}}h2{{font-size:19px;margin:30px 0 12px}}
.muted,footer{{color:#65758a;font-size:12px}}.notice{{background:#edf4ff;border-radius:12px;padding:16px;font-size:13px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}th{{background:#f1f5fb;text-align:left;color:#526680}}td,th{{padding:10px;border-bottom:1px solid #e6ebf2;vertical-align:top;overflow-wrap:anywhere}}
.table{{overflow-x:auto}}.note{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f7f9fc;padding:20px;border-radius:12px;min-height:80px}}
button{{background:#367bf5;color:white;border:0;border-radius:10px;padding:12px 18px;cursor:pointer}}footer{{margin-top:30px}}
@media(max-width:640px){{main{{margin:0;padding:22px;border-radius:0}}h1{{font-size:25px}}}}
@media print{{@page{{size:A4 landscape;margin:14mm}}body{{background:white}}main{{margin:0;padding:0;max-width:none}}button,.print-help{{display:none}}thead{{display:table-header-group}}tr{{break-inside:avoid}}h2{{break-after:avoid}}.table{{overflow:visible}}.note{{white-space:pre-wrap}}}}
</style></head><body><main><header><div class="brand">AFPK · YOUNG PLANNER</div><h1>나의 재무설계 리포트</h1>
<p class="muted">작성 시각 {timestamp} · 다운로드 시점의 입력·계산 결과</p>
<button onclick="window.print()">인쇄 / PDF로 저장</button><p class="print-help muted">PDF가 필요하면 인쇄 창의 대상에서 ‘PDF로 저장’을 선택하세요.</p></header>
<p class="notice">공모전용 가상 사례입니다. 계산 결과는 참고자료이며 최종 재무설계 판단은 사용자가 검토해야 합니다.</p>
{''.join(content)}<section><h2>인간 검토 메모</h2><div class="note">{escape(note or '작성된 검토 메모가 없습니다.')}</div></section>
<section><h2>계산 가정과 한계</h2><p class="muted">연 실효수익률을 월 수익률로 환산하고 매월 말 납입하며, 할부 종료 전환을 선택한 경우 보고된 개월 수 이후부터 추가 납입을 반영합니다. 현재 자산 미래가치 = A × (1+i)^n, 저축 미래가치 = P × ((1+i)^n−1)/i (0%이면 P×n). 세금·물가·수수료·소득변화·수익률 변동·부채 이자 및 잔액의 상환 스케줄은 미반영입니다. 선택한 할부 종료에 따른 고정지출 절감·저축 전환 시나리오만 별도로 반영합니다. 부채를 미래자산에서 자동 차감하지 않습니다. 목표별 자산·월 납입 배분을 검증합니다. 결혼·주거 통합목표는 두 개별 목표 배분의 합이며 개별 결과와 다시 합산하지 않습니다. 배분 원장은 현재 재원을 예약하는 모델이며, 미래 목표 지출 후 잔액·재사용은 아직 추적하지 않습니다. 높은 기대수익률은 위험 증가를 동반합니다. 현재가치 목표와 명목 미래자산 비교에는 한계가 있습니다. 주택 상세분석의 별도 V0.1 시나리오는 이 리포트에 포함되지 않습니다.</p></section>
<footer>앱은 리포트를 DB나 파일로 영구 저장하지 않습니다. 내려받은 파일은 기기에 남습니다. 새 입력은 이미 내려받은 문서에 반영되지 않으므로 다시 다운로드하세요.</footer>
</main></body></html>'''.encode('utf-8')
