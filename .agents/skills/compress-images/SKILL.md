---
name: compress-images
description: >-
  Kodeveloper 블로그 이미지 압축 및 정규화 워크플로우(sharp 기반).
  사용자가 img/struggle/N/ 등 블로그 이미지 폴더의 원본 이미지 압축·최적화·리사이즈·파일명 정규화를 요청할 때 사용한다.
---

# 블로그 이미지 압축 및 최적화 워크플로우 (`/compress-images`)

`img/struggle/<N>/` 등 대상 폴더에 배치된 원본 이미지들을 모두 **`.jpg` 포맷으로 통일**하고, `sharp`(libvips + MozJPEG) 기반으로 인플레이스(in-place) 압축한 뒤 포스트 마크다운 파일의 이미지 링크와 대조·검증하는 스킬입니다.

---

## 1. 실행 방법

사용자가 `/compress-images img/struggle/70`처럼 대상 디렉토리 경로(예: `img/struggle/70`, `/img/struggle/70`, 또는 `@[img/struggle/70]`)를 지정하거나 인자 없이 `/compress-images`를 요청하면 아래 명령을 실행합니다 (`node` 실행 시 샌드박스 에러가 나면 `BypassSandbox: true`로 `node` 명령을 그대로 실행):

```bash
node .agents/skills/compress-images/scripts/compress_images.mjs img/struggle/<N>
```

> 참고: `img/struggle/70`과 같은 상대 경로뿐만 아니라 `/img/struggle/70`(슬래시 시작), 절대 경로, 또는 다른 이미지 폴더도 그대로 전달할 수 있습니다. `img/struggle/<N>` 경로인 경우 해당 회차 포스트(`_posts/*-struggle-<N>.markdown`)와의 이미지 참조 대조 체크도 자동으로 수행됩니다.

### 옵션
- `--max-dim <px>`: 최대 가로/세로 픽셀 지정 (기본값: `1920`)
- `--quality <1-100>`: JPG 압축 품질 지정 (기본값: `80`, 슬라이드/타이틀 이미지는 최소 `85` 자동 적용)

---

## 2. 스크립트 자동 처리 내역

1. **파일명 정규화 (macOS NFD → NFC)**:
   - macOS Finder나 스크린샷에서 생성된 한글 파일명(`이대범-1.jpg`, `이대범-발표자료.jpg` 등)의 자소 분리(NFD)를 표준 NFC로 자동 변환하여 Git 및 Linux(GitHub Pages) 환경에서 이미지 경로가 깨지지 않도록 보장합니다.
2. **모든 이미지 포맷 `.jpg` 통일 및 불필요 파일 정리**:
   - `.png`, `.PNG`, `.webp`, `.HEIC`(macOS `sips` 경유), `.jpeg`, `.JPG` 등 어떤 확장자로 원본 이미지를 넣어도 **모두 `.jpg`로 자동 변환**하고 원본 비-JPG 파일은 삭제합니다 (PNG의 투명 배경은 흰색 `#ffffff`로 자동 합성).
   - 폴더 내 `.DS_Store` 파일을 자동 삭제합니다.
3. **`sharp` (libvips + MozJPEG) 기반 고효율 압축**:
   - **EXIF 처리 및 리사이즈**: `.rotate()`로 스마트폰 사진의 EXIF 방향 정보를 반영해 회전시킨 뒤 메타데이터(GPS 위치정보 등)를 제거하고, 최대 장변 `1920px`(`withoutEnlargement: true`)로 리사이즈합니다.
   - **현장 사진 (`*-1.jpg`, `all.jpg`)**: `mozjpeg: true, quality: 80, chromaSubsampling: '4:2:0'`을 적용해 수백 KB 이하로 압축합니다.
   - **발표자료/타이틀 (`title.jpg`, `*-발표자료.jpg`)**: 글자 경계가 번지지 않도록 `mozjpeg: true, quality: 85, chromaSubsampling: '4:4:4'`를 적용해 선명도를 유지하면서 용량을 줄입니다.
   - 이미 최적화된 `.jpg` 파일(리사이즈 불필요 및 압축 후 용량이 더 크거나 같은 경우)은 건너뜁니다(`[Skipped]`).
4. **포스트 마크다운(`_posts/*-struggle-<N>.markdown`) 대조 리포트**:
   - 마크다운에 선언된 이미지 중 폴더에 없는 파일은 `[MISSING]`으로 표시합니다.
   - 폴더에는 존재하지만 마크다운에 아직 연결되지 않은 파일(예: `<발표자>-2.jpg`, `all-2.jpg` 등)은 `[UNLINKED]`로 표시합니다.

---

## 3. 후속 조치 (에이전트 지침)

- 스크립트 실행 결과에서 `[UNLINKED]`로 표시된 추가 현장 사진(예: `<발표자>-2.jpg`, `all-2.jpg`)이 있다면, 해당 회차 포스트(`_posts/YYYY-MM-DD-struggle-N.markdown`)의 해당 발표자 섹션 또는 `### 사진` 섹션에 이미지 태그(`![](/img/struggle/N/파일명)`)를 자동으로 추가해 줍니다.
- `[MISSING]`으로 남아있는 파일이 있다면 사용자에게 어떤 이미지 파일이 아직 누락되어 있는지 안내합니다.
