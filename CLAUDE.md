# CLAUDE.md

Kodeveloper 블로그 (Jekyll). 빌드·디렉토리 구조·커밋/PR 규칙은 `AGENTS.md` 참고.
이 문서는 **고군분투기 포스트 작성 방식**과 세션에서 확인한 주의점을 정리한다.

## 고군분투기 포스트 (개최 후기)

개최된 고군분투기 LT회의 **후기 포스트**. 파일: `_posts/YYYY-MM-DD-struggle-N.markdown` (`date` = 개최일).

Front matter:

```yaml
---
author: kodeveloper
date: YYYY-MM-DD
layout: post
title: 제N차 고군분투기
categories: [고군분투기]
tags: [발표 주제 키워드]   # 영문 토픽 태그
---
```

본문 섹션 순서 (64~68차 공통): **타이틀 이미지 → `### 일정` → `### 발표자` → `### 사진` → `### 후원`**

- **타이틀 이미지**: front matter 바로 아래 `![](/img/struggle/N/title.png)` (에셋이 있을 때만)
- **`### 일정`**: `제목 / 일시 / 장소 / 주소` 4줄만
- **`### 발표자`**: 발표자마다 `**n. 이름: 발표제목** - [자료](구글드라이브/슬라이드 URL)` + 발표 이미지 1~2장, 발표자 사이에 `---` 구분선. 자료 미공개 시 `- 자료 (공개 예정)`
- **`### 사진`**: 나머지 현장 사진 + 단체사진(`all.jpg`)
- **`### 후원`**: `회사/장소명(@담당자)` 형식

**후기 포스트에는 모집(사전 안내) 요소를 넣지 않는다**: 신청마감·지도·회비·`### 순서`·`### 비고`·`### 참가`·슬랙/캘린더 CTA 등. 사전 안내가 필요하면 리치 랜딩 페이지 `events/event-N.html` + `_events/YYYY-MM-DD-struggle-N.md`로 별도 작성 (65차 사례).

## 이미지 규칙

- 저장 위치: `img/struggle/N/` 한 폴더에 전부. 참조: `![](/img/struggle/N/파일명)` (사이트 루트 절대경로)
- 명명: `title.png`(타이틀), 발표자 이미지 `이름.jpg` 또는 `이름-발표자료.png`(슬라이드 캡처) 또는 `1.jpg`·`2.jpg`, 단체 `all.jpg`
- **발표자료 원본(PDF/PPT)은 저장소에 두지 않는다** — 구글 드라이브/슬라이드 링크만 사용
- 사진 원본은 용량이 크므로 추가 전 최적화 권장 (예: `sips -Z 1600 <file>`)

## 환경/주의점

- **로컬 `bundle exec jekyll` 미작동**: `Gemfile.lock`의 nokogiri가 linux 전용이라 macOS에서 실패 → 미리보기는 Docker 사용 (`AGENTS.md` 참고)
- **kramdown GFM `hard_wrap`(기본 true)**: 단일 줄바꿈이 `<br>`로 렌더링됨 → 일정 블록 등에 줄 끝 공백 2칸 불필요
- **markdown 링크 URL 안의 괄호**는 `%28`/`%29`로 인코딩 (안 하면 `](...)` 파싱이 조기 종료됨)
