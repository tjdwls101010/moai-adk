# Codes - Utility Scripts

## Convert_Image-Link_Wiki-to-Markdown.py

Wiki 스타일 이미지 링크를 Markdown 스타일로 변환하고, **AI로 이미지 설명을 자동 생성**하는 스크립트입니다.

### 변환 형식

Vault 전체에서 이미지 파일을 검색하여 **실제 경로**를 찾고, **AI 이미지 분석**으로 alt text를 생성합니다.

| Before (Wiki) | After (Markdown) |
|---------------|------------------|
| `![[image.png]]` | `![AI가 생성한 이미지 설명](🧷Attachments/image.png)` |
| `![[photo.jpg]]` | `![이 사진은 ...](images/photo.jpg)` |
| `![[path/to/diagram.webp]]` | `![다이어그램 설명](path/to/diagram.webp)` |

### 주요 기능

- **AI 이미지 분석**: GPT 또는 Gemini API를 사용하여 이미지 설명 자동 생성
- **컨텍스트 인식**: 이미지 주변 텍스트(앞뒤 500자)를 분석하여 맥락에 맞는 설명 생성
- **병렬 처리**: 최대 20개 이미지 동시 분석으로 빠른 처리
- **재시도 로직**: API 호출 실패 시 최대 3회 재시도
- **진행 상황 표시**: 터미널에서 실시간 처리 상태 확인

### 동작 방식

- 파일명만 있는 경우: vault에서 검색 후 vault 루트 기준 경로로 변환
- 이미 경로가 있는 경우: 그대로 유지
- 찾지 못한 경우: 원본 유지 + 경고 출력

### 지원 확장자

png, jpg, jpeg, gif, webp, svg, bmp, tiff, ico

### 사용법

```bash
cd Codes

# 기본 사용 (GPT로 이미지 설명 생성)
python Convert_Image-Link_Wiki-to-Markdown.py "파일명.md"

# Gemini 모델 사용
python Convert_Image-Link_Wiki-to-Markdown.py "파일명.md" -m gemini

# AI 설명 없이 경로 변환만
python Convert_Image-Link_Wiki-to-Markdown.py "파일명.md" --no-describe

# Dry-run 모드 (변경사항 미리보기, 파일 수정 없음)
python Convert_Image-Link_Wiki-to-Markdown.py "파일명.md" -n
```

### CLI 옵션

| 옵션 | 설명 |
|------|------|
| `-n, --dry-run` | 변경사항 미리보기 (파일 수정 없음) |
| `-m, --model` | AI 모델 선택: `gpt` (기본값) 또는 `gemini` |
| `--no-describe` | AI 설명 생성 건너뛰기 (경로 변환만 수행) |

### 예시 출력

```
Building image index...
Found 10751 image files

============================================================
🖼️  발견한 이미지: 5개
🤖 사용 모델: GPT
⚡ 동시 처리: 20개
============================================================

[1/5] 🔍 분석 중: chart.png
        ✅ 완료: 이 차트는 2020년부터 2024년까지의 매출 성장...
[2/5] 🔍 분석 중: diagram.jpg
        ✅ 완료: 시스템 아키텍처를 보여주는 다이어그램으로...

============================================================
📊 처리 결과 요약
   ✅ 성공: 5개
   ❌ 실패: 0개
   ⏭️ 건너뜀: 0개
   📝 총 처리: 5개
============================================================

✅ Converted 5 image link(s) in: 파일명.md
```

### 설정 파일

#### `.env` (API 키 설정)

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-mini

GOOGLE_API_KEY=AIza...
GOOGLE_MODEL=gemini-3-flash-preview
```

#### `prompt.md` (프롬프트 템플릿)

AI에게 전달할 프롬프트 템플릿입니다. SMART 형식으로 구성되어 있으며, 한국어로 이미지 설명을 생성합니다.

### 필요 패키지

```bash
pip install python-dotenv openai google-generativeai Pillow
```
