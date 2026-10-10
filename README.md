# Mono

개발/기술 블로그용 미니멀 티스토리 스킨.

- 1단 레이아웃 + 오른쪽 서랍 사이드바 (프로필 · 검색 · 메뉴 · 카테고리 · 최근 글 · 태그 · 방문자)
- 라이트/다크 전환 (OS 설정 감지, 선택값 저장, 깜빡임 없음)
- 코드블록: highlight.js 하이라이팅(테마 색은 CSS 변수) + 언어 라벨 + Copy 버튼
- 글 상세: 목차(h2~h4, 현재 섹션 하이라이트, 1200px 이상에서 표시), 읽기 진행바, 읽기 시간
- 단축키: `/` 검색, `Esc` 서랍 닫기

## 파일 구조

```
skin.html          HTML 템플릿
style.css          스타일 (색상 토큰은 상단 :root / [data-theme="dark"])
index.xml          스킨 정보 + 스킨 옵션(강조 색상, 기본 테마, 썸네일 표시)
images/script.js   테마 · 서랍 · 코드블록 · 목차 · 진행바
preview/build.py   로컬 미리보기 생성기 (티스토리 업로드 대상 아님)
```

## 적용

1. 티스토리 관리자 → **꾸미기 > 스킨 편집 > HTML 편집**
2. HTML 탭에 `skin.html`, CSS 탭에 `style.css` 전체 붙여넣기
3. 파일업로드 탭에 `index.xml`, `images/script.js` 업로드 (`script.js`는 `images/` 경로로 올라감)
4. 적용 후 **꾸미기 > 사이드바**에서 모듈 순서 정리
5. **스킨 편집 > 스킨 옵션**에서 강조 색상 · 기본 테마 지정

> 티스토리 메뉴바(구독/알림) 위치를 **오른쪽 상단**으로 두면 헤더 버튼과 겹칠 수 있어요. 다른 위치를 권장합니다.

## 로컬 미리보기

```bash
python3 preview/build.py && python3 -m http.server 4173
```

`http://localhost:4173/preview/index.html`, `.../preview/post.html` 에서 확인. `skin.html`을 고치면 build만 다시 돌리면 됩니다. 치환자는 더미 값이라 실제 티스토리 출력(댓글, 카테고리 마크업 등)과 차이가 있을 수 있어요.

## 남은 일

- `preview256.jpg` / `preview560.jpg` / `preview1600.jpg` / `preview.gif` (스킨 등록 방식으로 올릴 때만 필요)
- `index.xml`의 author / license 채우기
