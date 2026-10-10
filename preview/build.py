"""skin.html 의 티스토리 치환자를 더미 데이터로 채워 로컬 미리보기를 만든다.

    python3 preview/build.py   →  preview/index.html, preview/post.html
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent

BLOCK = re.compile(r"<(s_[a-z0-9_-]+)>(.*?)</\1>", re.S)
VAR = re.compile(r"\[##_([a-z0-9_-]+)_##\]")


def render(tpl, ctx):
    def block(m):
        val = ctx.get(m.group(1), False)
        if isinstance(val, list):
            return "".join(render(m.group(2), {**ctx, **item}) for item in val)
        if isinstance(val, dict):
            return render(m.group(2), {**ctx, **val})
        return render(m.group(2), ctx) if val else ""

    out = BLOCK.sub(block, tpl)
    return VAR.sub(lambda m: str(ctx.get(m.group(1), "")), out)


def thumb(hue):
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='240' height='168'>"
           f"<rect width='100%' height='100%' fill='hsl({hue},45%,62%)'/>"
           f"<circle cx='170' cy='60' r='36' fill='hsl({hue},55%,78%)'/></svg>")
    return "data:image/svg+xml;utf8," + svg.replace("<", "%3C").replace(">", "%3E").replace("#", "%23")


POSTS = [
    ("Spring 트랜잭션 전파 속성, 실제로 언제 문제가 될까", "Backend", "2026. 10. 8. 21:14", 4, 210,
     "REQUIRES_NEW를 쓰면 안전할 거라고 생각했지만, 커넥션 풀이 고갈되는 상황을 만났다. 전파 속성별로 커넥션을 몇 개 잡는지 직접 측정해 본 기록."),
    ("Redis 분산 락 vs DB 비관적 락 — 재고 차감에서의 선택", "Backend", "2026. 10. 2. 10:03", 12, 15,
     "동시 주문 1,000건 부하 테스트로 두 방식의 처리량과 실패율을 비교했다. 정답은 없고 트레이드오프만 있었다."),
    ("Kafka Consumer Lag 모니터링 대시보드 만들기", "Infra", "2026. 9. 24. 18:40", 0, None,
     "Burrow 대신 Prometheus exporter와 Grafana로 컨슈머 그룹별 lag를 시각화한 과정을 정리한다."),
    ("JPA N+1, fetch join과 EntityGraph 그리고 BatchSize", "Backend", "2026. 9. 11. 09:12", 2, 280,
     "세 가지 해법이 각각 어떤 SQL을 만들어내는지 로그로 확인하고, 페이징과 함께 쓸 때 주의할 점을 짚어본다."),
    ("TIL — git rebase --onto 로 브랜치 옮겨 심기", "TIL", "2026. 9. 3. 23:55", 1, None,
     "잘못된 base에서 딴 브랜치를 rebase --onto 한 줄로 옮기는 방법."),
]

POST_BODY = """
<p>트랜잭션 전파 속성은 문서로 읽을 때는 단순해 보이지만, 커넥션 풀과 엮이면 이야기가 달라진다. 이 글에서는 <code>REQUIRES_NEW</code>가 실제로 몇 개의 커넥션을 점유하는지 측정해 본다.</p>
<h2>문제 상황</h2>
<p>주문 처리 중 이력 저장을 별도 트랜잭션으로 분리하려고 <code>@Transactional(propagation = REQUIRES_NEW)</code>를 붙였다. 트래픽이 몰리자 <a href="#">HikariCP</a>에서 타임아웃이 터지기 시작했다.</p>
<pre id="code_1" class="java" data-ke-language="java" data-ke-type="codeblock"><code>@Service
@RequiredArgsConstructor
public class OrderService {
    private final HistoryService historyService;

    @Transactional
    public void order(Long itemId) {
        // 외부 트랜잭션이 커넥션 1개 점유
        stockRepository.decrease(itemId, 1);
        historyService.save(itemId); // REQUIRES_NEW → 커넥션 1개 추가
    }
}</code></pre>
<h3>왜 커넥션이 2개 필요한가</h3>
<p>외부 트랜잭션은 커밋 전까지 커넥션을 반납하지 않는다. 내부의 새 트랜잭션은 별도 커넥션을 요구하므로, 풀 크기가 <b>10</b>이고 동시 요청이 10개면 모두가 두 번째 커넥션을 기다리며 교착 상태가 된다.</p>
<blockquote data-ke-style="style1">풀 크기 ≥ 스레드 수 × (중첩 트랜잭션 깊이 + 1) 이어야 안전하다.</blockquote>
<h3>측정</h3>
<table style="border-collapse: collapse; width: 100%; height: 76px;" border="1" data-ke-align="alignLeft" data-ke-style="style12"><tbody>
<tr style="height: 19px;"><td style="width: 30%; height: 19px;"><b>전파 속성</b></td><td style="width: 30%; height: 19px;"><b>점유 커넥션</b></td><td style="width: 40%; height: 19px;"><b>p99 (ms)</b></td></tr>
<tr style="height: 19px;"><td style="height: 19px;">REQUIRED</td><td style="height: 19px;">1</td><td style="height: 19px;">42</td></tr>
<tr style="height: 19px;"><td style="height: 19px;">REQUIRES_NEW</td><td style="height: 19px;">2</td><td style="height: 19px;">1,820</td></tr>
<tr style="height: 19px;"><td style="height: 19px;">이벤트 + AFTER_COMMIT</td><td style="height: 19px;">1 → 1</td><td style="height: 19px;">47</td></tr>
</tbody></table>
<h2>해결 방안</h2>
<p>세 가지 선택지가 있었다.</p>
<ul><li>풀 크기를 늘린다 — 근본 해결은 아니다.</li><li>이력 저장을 <code>@TransactionalEventListener(phase = AFTER_COMMIT)</code>로 분리한다.</li><li>이력은 메시지 큐로 비동기 처리한다.</li></ul>
<pre id="code_2" class="yaml" data-ke-language="yaml" data-ke-type="codeblock"><code>spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      connection-timeout: 3000</code></pre>
<h3>최종 선택</h3>
<p>이력 유실을 일부 허용할 수 있는 도메인이라 이벤트 방식을 택했다.</p>
<pre id="code_3" class="bash" data-ke-language="bash" data-ke-type="codeblock"><code># 부하 테스트
k6 run --vus 100 --duration 30s order-test.js</code></pre>
<h2>정리</h2>
<p>전파 속성을 고를 때는 트랜잭션 경계뿐 아니라 <b>리소스 점유</b>까지 같이 봐야 한다.</p>
<div class="another_category another_category_color_gray"><h4>'<a href="#">Backend</a>' 카테고리의 다른 글</h4>
<table><tr><th><a href="#">Redis 분산 락 vs DB 비관적 락 — 재고 차감에서의 선택</a>&nbsp;&nbsp;<span>(12)</span></th><td>2026.10.02</td></tr>
<tr><th><a href="#">JPA N+1, fetch join과 EntityGraph 그리고 BatchSize</a>&nbsp;&nbsp;<span>(2)</span></th><td>2026.09.11</td></tr></table></div>
"""


def page(body_id, articles, extra):
    ctx = {
        "s_t3": True, "s_sidebar": True, "s_sidebar_element": True, "s_search": True,
        "body_id": body_id,
        "title": "hyeonjin.log", "page_title": "hyeonjin.log", "blog_link": "index.html",
        "blogger": "hyeonjin", "desc": "백엔드 개발을 하며 배운 것들을 기록합니다.",
        "image": thumb(220),
        "blog_menu": '<ul><li><a href="index.html">Home</a></li><li><a href="#">Tags</a></li><li><a href="#">Guestbook</a></li></ul>',
        "category_list": (
            '<ul class="tt_category"><li><a href="#" class="link_tit">분류 전체보기 <span class="c_cnt">(42)</span></a>'
            '<ul class="category_list">'
            '<li><a href="#" class="link_item">Backend <span class="c_cnt">(21)</span></a>'
            '<ul class="sub_category_list"><li><a href="#" class="link_sub_item">Spring <span class="c_cnt">(12)</span></a></li>'
            '<li><a href="#" class="link_sub_item">JPA <span class="c_cnt">(9)</span></a></li></ul></li>'
            '<li><a href="#" class="link_item">Infra <span class="c_cnt">(8)</span></a></li>'
            '<li><a href="#" class="link_item">TIL <span class="c_cnt">(13)</span></a></li>'
            '</ul></li></ul>'),
        "s_rctps_rep": [{"rctps_rep_link": "post.html", "rctps_rep_title": p[0]} for p in POSTS],
        "s_random_tags": [{"tag_link": "#", "tag_name": t} for t in
                          ["spring", "jpa", "redis", "kafka", "transaction", "git", "til", "mysql"]],
        "count_today": 128, "count_yesterday": 341, "count_total": "48,210",
        "var_accent-color": "#3d63dd", "var_default-theme": "system", "s_if_var_show-thumbnail": True,
        "s_article_rep": articles, "rss_url": "#",
        "comment_group": '<p style="color:var(--text-3);font-size:14px">(티스토리 댓글 영역)</p>',
    }
    ctx.update(extra)
    html = render((ROOT / "skin.html").read_text(encoding="utf-8"), ctx)
    return html.replace('href="./style.css"', 'href="../style.css"').replace('src="./images/script.js"', 'src="../images/script.js"')


def main():
    items = [{
        "s_index_article_rep": True,
        "article_rep_link": "post.html", "article_rep_title": t, "article_rep_category": c,
        "article_rep_date": d, "article_rep_summary": s,
        "s_rp_count": n > 0, "article_rep_rp_cnt": n,
        "s_article_rep_thumbnail": h is not None, "article_rep_thumbnail_url": thumb(h or 0),
    } for t, c, d, n, h, s in POSTS]
    paging = {
        "s_paging": True, "prev_page": 'href="#"', "next_page": 'href="#"', "no_more_prev": "no-more-prev",
        "s_paging_rep": [{"paging_rep_link": 'href="#"',
                          "paging_rep_link_num": f'<span class="{"selected" if i == 1 else ""}">{i}</span>'} for i in range(1, 5)],
    }
    (OUT / "index.html").write_text(page("tt-body-index", items, paging), encoding="utf-8")

    t, c, d, n, h, s = POSTS[0]
    post = [{
        "s_permalink_article_rep": True,
        "article_rep_title": t, "article_rep_category": c, "article_rep_category_link": "#",
        "article_rep_date": d, "article_rep_author": "hyeonjin", "article_rep_desc": POST_BODY,
        "s_tag_label": True,
        "tag_label_rep": ", ".join(f'<a href="#" rel="tag">{x}</a>' for x in ["spring", "transaction", "hikaricp"]),
        "s_article_prev": True, "article_prev_link": "#", "article_prev_title": POSTS[1][0],
        "s_article_next": True, "article_next_link": "#", "article_next_title": "[루프팩] volume 3. 낙관적 락과 비관적 락, 정말 시간 차이가 별로 안 날까? 직접 측정해 본 결과",
        "s_article_related": True,
        "s_article_related_rep": [{"article_related_rep_link": "#", "article_related_rep_title": p[0],
                                   "article_related_rep_date": p[2].split(" ")[0] + " " + p[2].split(" ")[1] + " " + p[2].split(" ")[2]}
                                  for p in POSTS[1:4]],
        "s_rp": True,
    }]
    (OUT / "post.html").write_text(page("tt-body-page", post, {"page_title": t}), encoding="utf-8")
    print("built:", OUT / "index.html", OUT / "post.html")


if __name__ == "__main__":
    main()
