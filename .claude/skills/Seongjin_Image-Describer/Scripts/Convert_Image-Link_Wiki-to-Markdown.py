#!/usr/bin/env python3
"""
Convert Wiki-style image links to Markdown-style image links with AI descriptions.

Wiki style:  ![[image.png]]
Markdown style:  ![AI 설명](path/image.png)

Usage:
    python Convert_Image-Link_Wiki-to-Markdown.py <markdown_file>
    python Convert_Image-Link_Wiki-to-Markdown.py <markdown_file> -m gemini
    python Convert_Image-Link_Wiki-to-Markdown.py <markdown_file> --no-describe

Example:
    python Convert_Image-Link_Wiki-to-Markdown.py "📰2025 세대·젠더 국민통합 조사.md"
"""

import argparse
import asyncio
import base64
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(Path(__file__).parent / ".env")

# ==================== 설정값 ====================
# Vault 루트 경로 (고정)
VAULT_ROOT = Path("/Users/seongjin/Documents/⭐성진이의 옵시디언")

# 환경변수에서 API 키 및 모델명 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-3-flash-preview")

# 이미지 분석 설정
CONTEXT_CHARS = 500   # 이미지 앞뒤로 추출할 텍스트 길이
MAX_RETRIES = 3       # API 호출 재시도 횟수
CONCURRENT = 20       # 동시 처리할 이미지 개수
PROMPT_FILE = "prompt.md"
FILE_ENCODING = "utf-8"

# 패턴
WIKI_PATTERN = r'!\[\[([^\]]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|tiff|ico))\]\]'
MARKDOWN_EMPTY_ALT_PATTERN = r'!\[\]\(([^)]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|tiff|ico))\)'


def build_image_index(vault_root: Path) -> dict[str, Path]:
    """vault 전체에서 이미지 파일을 검색하여 {파일명: 절대경로} 인덱스 생성."""
    extensions = ('png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp', 'tiff', 'ico')
    index = {}
    for ext in extensions:
        for img_path in vault_root.rglob(f'*.{ext}'):
            index[img_path.name] = img_path
        for img_path in vault_root.rglob(f'*.{ext.upper()}'):
            index[img_path.name] = img_path
    return index


def get_vault_relative_path(image_path: Path) -> str:
    """vault 루트 기준 상대경로 반환."""
    return str(image_path.relative_to(VAULT_ROOT))


def load_prompt_template() -> str:
    """prompt.md에서 프롬프트 템플릿 로드"""
    prompt_path = Path(__file__).parent / PROMPT_FILE
    if prompt_path.exists():
        return prompt_path.read_text(encoding=FILE_ENCODING)
    # 기본 프롬프트 (fallback)
    return """이미지를 분석하여 설명을 생성하세요.

Context before: {context_before}
Context after: {context_after}
Image: {image_path}"""


def convert_wiki_links_to_markdown(file_path: Path, image_index: dict[str, Path]) -> int:
    """
    1단계: Wiki link를 Markdown 형식으로 즉시 변환 & 저장
    Returns: 변환된 링크 수
    """
    content = file_path.read_text(encoding=FILE_ENCODING)

    matches = list(re.finditer(WIKI_PATTERN, content, re.IGNORECASE))
    if not matches:
        return 0

    converted_count = 0
    warnings = []

    # 역순으로 처리 (위치 밀림 방지)
    for match in reversed(matches):
        filename = match.group(1)

        # 경로 결정
        if '/' in filename or '\\' in filename:
            vault_path = filename
        elif filename in image_index:
            vault_path = get_vault_relative_path(image_index[filename])
        else:
            warnings.append(f"⚠️ 파일 없음: {filename}")
            continue

        # 즉시 변환: ![[file]] → ![](path)
        new_text = f"![]({vault_path})"
        content = content[:match.start()] + new_text + content[match.end():]
        converted_count += 1

    # 즉시 저장
    file_path.write_text(content, encoding=FILE_ENCODING)

    for warning in warnings:
        print(warning)

    return converted_count


async def describe_image_gpt(
    image_path: Path,
    context_before: str,
    context_after: str,
    prompt_template: str
) -> str:
    """GPT로 이미지 설명 생성 (재시도 로직 포함)"""
    from openai import OpenAI

    if not OPENAI_API_KEY:
        print("  ⚠️ OPENAI_API_KEY가 설정되지 않았습니다.")
        return ""

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = prompt_template.format(
        context_before=context_before,
        context_after=context_after,
        image_path=str(image_path)
    )

    # 이미지를 base64로 인코딩
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')

    # 이미지 포맷 확인
    suffix = image_path.suffix.lower()
    media_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.gif': 'image/gif'
    }.get(suffix, 'image/png')

    for attempt in range(MAX_RETRIES):
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=OPENAI_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{media_type};base64,{base64_image}"}
                        }
                    ]
                }],
                max_completion_tokens=4096
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"        ⚠️ 재시도 {attempt + 1}/{MAX_RETRIES}: {e}")
                await asyncio.sleep(1)
            else:
                print(f"        ❌ API 호출 실패: {e}")
                return ""


async def describe_image_gemini(
    image_path: Path,
    context_before: str,
    context_after: str,
    prompt_template: str
) -> str:
    """Gemini로 이미지 설명 생성 (재시도 로직 포함)"""
    import google.generativeai as genai
    import PIL.Image

    if not GOOGLE_API_KEY:
        print("  ⚠️ GOOGLE_API_KEY가 설정되지 않았습니다.")
        return ""

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(GOOGLE_MODEL)

    prompt = prompt_template.format(
        context_before=context_before,
        context_after=context_after,
        image_path=str(image_path)
    )

    for attempt in range(MAX_RETRIES):
        try:
            img = PIL.Image.open(image_path)
            response = await asyncio.to_thread(
                model.generate_content,
                [prompt, img]
            )
            return response.text.strip()
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"        ⚠️ 재시도 {attempt + 1}/{MAX_RETRIES}: {e}")
                await asyncio.sleep(1)
            else:
                print(f"        ❌ API 호출 실패: {e}")
                return ""


async def process_single_image_and_save(
    file_path: Path,
    image_path_str: str,
    idx: int,
    total: int,
    describe_func,
    prompt_template: str,
    semaphore: asyncio.Semaphore,
    lock: asyncio.Lock,
    results: dict
):
    """단일 이미지 처리 후 즉시 파일에 저장"""
    async with semaphore:
        print(f"[{idx}/{total}] 🔍 분석 중: {Path(image_path_str).name}")

        # 이미지 절대 경로 계산
        image_abs_path = VAULT_ROOT / image_path_str
        if not image_abs_path.exists():
            print(f"        ⚠️ 이미지 파일 없음")
            async with lock:
                results['skip'] += 1
            return

        # 현재 파일 내용 읽기 (lock 내에서)
        async with lock:
            content = file_path.read_text(encoding=FILE_ENCODING)

        # 해당 이미지의 위치와 컨텍스트 찾기
        pattern = rf'!\[\]\({re.escape(image_path_str)}\)'
        match = re.search(pattern, content)

        if not match:
            print(f"        ⚠️ 이미 처리됨 또는 찾을 수 없음")
            async with lock:
                results['skip'] += 1
            return

        # 컨텍스트 추출
        start = max(0, match.start() - CONTEXT_CHARS)
        end = min(len(content), match.end() + CONTEXT_CHARS)
        context_before = content[start:match.start()].strip()
        context_after = content[match.end():end].strip()

        # LLM 호출
        alt_text = await describe_func(
            image_abs_path,
            context_before,
            context_after,
            prompt_template
        )

        if alt_text:
            # 실제 줄바꿈만 공백으로 변환 (문자열 '\n'은 유지)
            alt_text = alt_text.replace('\n', ' ').strip()

            # 즉시 파일에 저장 (lock 내에서)
            async with lock:
                # 다시 읽기 (다른 태스크가 수정했을 수 있음)
                content = file_path.read_text(encoding=FILE_ENCODING)

                # 해당 패턴을 새 텍스트로 교체 (lambda 사용으로 \n 이스케이프 문제 방지)
                new_text = f"![{alt_text}]({image_path_str})"
                content = re.sub(pattern, lambda m: new_text, content, count=1)

                # 저장
                file_path.write_text(content, encoding=FILE_ENCODING)
                results['success'] += 1

            preview = alt_text[:50] + "..." if len(alt_text) > 50 else alt_text
            print(f"        ✅ 완료: {preview}")
        else:
            async with lock:
                results['fail'] += 1
            print(f"        ❌ 실패: 설명 생성 안됨")


async def add_descriptions_to_empty_alt(
    file_path: Path,
    model_type: str = "gpt"
) -> dict:
    """
    2단계: alt text가 비어있는 Markdown 이미지에 AI 설명 추가
    각 이미지 처리 완료 시 즉시 저장
    """
    content = file_path.read_text(encoding=FILE_ENCODING)

    # alt text가 비어있는 이미지 찾기: ![](path)
    matches = list(re.finditer(MARKDOWN_EMPTY_ALT_PATTERN, content, re.IGNORECASE))

    if not matches:
        return {'success': 0, 'fail': 0, 'skip': 0, 'total': 0}

    prompt_template = load_prompt_template()
    describe_func = describe_image_gpt if model_type == "gpt" else describe_image_gemini

    print(f"\n{'='*60}")
    print(f"🖼️  설명이 필요한 이미지: {len(matches)}개")
    print(f"🤖 사용 모델: {model_type.upper()}")
    print(f"⚡ 동시 처리: {CONCURRENT}개")
    print(f"{'='*60}\n")

    # 이미지 경로 목록 추출
    image_paths = [match.group(1) for match in matches]

    # 병렬 처리
    semaphore = asyncio.Semaphore(CONCURRENT)
    lock = asyncio.Lock()
    results = {'success': 0, 'fail': 0, 'skip': 0}

    tasks = [
        process_single_image_and_save(
            file_path,
            image_path,
            idx,
            len(image_paths),
            describe_func,
            prompt_template,
            semaphore,
            lock,
            results
        )
        for idx, image_path in enumerate(image_paths, 1)
    ]

    await asyncio.gather(*tasks)

    results['total'] = len(matches)

    # 최종 요약
    print(f"\n{'='*60}")
    print(f"📊 처리 결과 요약")
    print(f"   ✅ 성공: {results['success']}개")
    print(f"   ❌ 실패: {results['fail']}개")
    print(f"   ⏭️ 건너뜀: {results['skip']}개")
    print(f"   📝 총 처리: {results['total']}개")
    print(f"{'='*60}\n")

    return results


async def async_main():
    """비동기 메인 함수"""
    parser = argparse.ArgumentParser(
        description='Convert Wiki-style image links (![[image.png]]) to Markdown-style (![설명](image.png))'
    )
    parser.add_argument(
        'file',
        type=str,
        help='Path to the markdown file to convert'
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying the file'
    )
    parser.add_argument(
        '-m', '--model',
        choices=['gpt', 'gemini'],
        default='gpt',
        help='이미지 분석에 사용할 AI 모델 (기본값: gpt)'
    )
    parser.add_argument(
        '--no-describe',
        action='store_true',
        help='AI 이미지 설명 생성 건너뛰기 (경로 변환만 수행)'
    )

    args = parser.parse_args()

    # Resolve file path
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not file_path.is_file():
        print(f"Error: Not a file: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Build image index
    print("Building image index...")
    image_index = build_image_index(VAULT_ROOT)
    print(f"Found {len(image_index)} image files")

    # Dry-run 모드
    if args.dry_run:
        content = file_path.read_text(encoding=FILE_ENCODING)

        wiki_matches = list(re.finditer(WIKI_PATTERN, content, re.IGNORECASE))
        empty_alt_matches = list(re.finditer(MARKDOWN_EMPTY_ALT_PATTERN, content, re.IGNORECASE))

        print(f"\n[Dry Run] {file_path}")
        print(f"  Wiki 링크 (변환 필요): {len(wiki_matches)}개")
        print(f"  빈 alt text (설명 필요): {len(empty_alt_matches)}개")

        if wiki_matches:
            print("\nWiki 링크 변환 미리보기:")
            for match in wiki_matches[:5]:
                filename = match.group(1)
                if '/' in filename or '\\' in filename:
                    vault_path = filename
                elif filename in image_index:
                    vault_path = get_vault_relative_path(image_index[filename])
                else:
                    print(f"  {match.group(0)} -> [파일 없음]")
                    continue
                print(f"  {match.group(0)} -> ![]({vault_path})")
            if len(wiki_matches) > 5:
                print(f"  ... 외 {len(wiki_matches) - 5}개")

        if empty_alt_matches and not args.no_describe:
            print("\n빈 alt text 이미지 (AI 설명 생성 예정):")
            for match in empty_alt_matches[:5]:
                print(f"  ![](  {match.group(1)})")
            if len(empty_alt_matches) > 5:
                print(f"  ... 외 {len(empty_alt_matches) - 5}개")

        return

    # ===== 1단계: Wiki 링크 → Markdown 변환 (즉시 저장) =====
    content = file_path.read_text(encoding=FILE_ENCODING)
    wiki_count = len(re.findall(WIKI_PATTERN, content, re.IGNORECASE))

    if wiki_count > 0:
        print(f"\n📝 1단계: Wiki 링크 변환 ({wiki_count}개)")
        converted = convert_wiki_links_to_markdown(file_path, image_index)
        print(f"   ✅ {converted}개 변환 완료 (즉시 저장됨)")

    # ===== 2단계: AI 설명 추가 (각각 즉시 저장) =====
    if not args.no_describe:
        print(f"\n📝 2단계: AI 이미지 설명 생성")
        await add_descriptions_to_empty_alt(file_path, model_type=args.model)
    else:
        print(f"\n⏭️ AI 설명 생성 건너뜀 (--no-describe)")

    print(f"✅ 완료: {file_path}")


def main():
    """메인 함수"""
    asyncio.run(async_main())


if __name__ == '__main__':
    main()
