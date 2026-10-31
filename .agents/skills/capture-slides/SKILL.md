---
name: capture-slides
description: >-
  구글 슬라이드(Google Slides) 및 구글 드라이브 발표자료 링크에서 1페이지(표지) 이미지를 캡처해
  img/struggle/N/ 폴더에 title.jpg 또는 <발표자>-발표자료.jpg로 저장하고 포스트의 자료 링크를 업데이트하는 워크플로우.
---

# 발표자료 및 타이틀 슬라이드 1페이지 캡처 워크플로우 (`/capture-slides`)

사용자가 구글 슬라이드(`docs.google.com/presentation/d/...`) 또는 구글 드라이브(`drive.google.com/file/d/...`) 링크들을 전달하면, 각 자료의 **1페이지(표지) 이미지**를 추출해 `img/struggle/<N>/`에 `.jpg`로 저장하고 해당 회차 포스트(`_posts/YYYY-MM-DD-struggle-N.markdown`)의 발표자료 링크를 업데이트합니다.
(이미지 압축은 역할을 분리하여 `/compress-images` 스킬에서 수행합니다.)

---

## 1. 실행 방법

저장할 폴더 경로(예: `img/struggle/70`)와 슬라이드 URL 목록을 전달해 스크립트를 실행합니다.
폴더 경로를 생략하면 현재 Git 브랜치(`feature/struggle-70`) 또는 최신 드래프트 포스트에서 회차를 자동 감지합니다.
(네트워크 접근이 필요하므로 샌드박스 에러 시 `BypassSandbox: true`로 실행합니다.)

```bash
python3 .agents/skills/capture-slides/scripts/capture_slides.py img/struggle/<N> "<URL_1>" "<URL_2>" ...
```

---

## 2. 자동 판별 및 폴백(Fallback) 프로세스

스크립트와 에이전트는 다음 **2단계**로 각 링크가 `title.jpg`인지, 어느 발표자의 `<발표자>-발표자료.jpg`인지 판별합니다:

1. **1단계 — HTML 메타데이터 및 본문 텍스트 자동 매칭 (`capture_slides.py`)**:
   - 링크의 HTML에서 `og:title`, `og:description`, 슬라이드 내 텍스트 조각을 추출하여 `_posts/*-struggle-<N>.markdown`에 등록된 발표자 이름(한글/영문/한자 별칭 포함) 및 발표 제목 키워드와 대조합니다.
   - 매칭이 확실한 경우 즉시 `img/struggle/<N>/<발표자>-발표자료.jpg`(또는 `title.jpg`)로 저장하고, 마크다운의 `- 자료(준비중)`을 `- [자료](URL)`로 자동 갱신합니다.

2. **2단계 — 이미지 비전(Vision) 텍스트 판독 폴백 (메타데이터로 판별 불가 시)**:
   - 구글 드라이브 권한이나 파일명(예: `발표자료.pptx`) 때문에 1단계에서 매칭되지 않은 슬라이드는 `img/struggle/<N>/unmatched-<번호>.jpg`로 저장됩니다.
   - `unmatched-<번호>.jpg`가 생성되면 에이전트는 즉시 `read_file` 툴로 해당 이미지를 직접 열어 표지에 적힌 **발표 제목 / 발표자 이름 / 제N차 고군분투기 타이틀**을 눈으로 읽고 판별합니다.
   - 판별 결과에 따라 파일을 `title.jpg` 또는 `<발표자>-발표자료.jpg`로 리네임(`mv`)하고, `_posts/YYYY-MM-DD-struggle-N.markdown`의 해당 발표자 `- 자료(준비중)`을 `- [자료](URL)`로 업데이트합니다.

---

## 3. 캡처 완료 후 안내

- 저장된 파일 목록(`title.jpg`, `<발표자>-발표자료.jpg`)과 업데이트된 마크다운 링크 결과를 사용자에게 보고합니다.
- 이미지 최적화가 필요할 때 `/compress-images img/struggle/<N>`을 실행하면 `sharp`로 압축된다는 점을 함께 안내합니다.

