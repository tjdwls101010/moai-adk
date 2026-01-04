#!/usr/bin/env python3
"""
PDF to Markdown Converter with AI Image Descriptions

PDF를 마크다운으로 변환하고, 이미지에 AI 기반 설명을 추가합니다.
Gemini 또는 GPT 모델을 선택할 수 있습니다.

Usage:
    python pdf_to_md.py -p "path/to/file.pdf"           # 기본: GPT 사용
    python pdf_to_md.py -p "path/to/file.pdf" -m gpt    # GPT 사용
    python pdf_to_md.py -p "path/to/file.pdf" -m gemini # Gemini 사용
"""

import argparse
import asyncio
import base64
import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import PIL.Image
import pymupdf4llm
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ==================== 설정값 ====================
DPI = 150  # 이미지 해상도
IMAGE_FORMAT = "png"  # 이미지 포맷 (png, jpg)
CONTEXT_CHARS = 1111  # 이미지 앞뒤로 추출할 텍스트 길이
CONCURRENT = 555  # 동시 처리할 이미지 개수
PROMPT_FILE = "prompt_book.md"  # 프롬프트 파일 경로
FILE_ENCODING = "utf-8"
BACKUP_EXTENSION = ".md.backup"
IMAGE_PATTERN = r'!\[([^\]]*)\]\(([^)]+)\)'

# 환경변수에서 API 키 및 모델명 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-3-pro-preview")


def parse_args():
    """CLI 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="PDF를 마크다운으로 변환하고 AI 이미지 설명을 추가합니다."
    )
    parser.add_argument(
        "-p", "--pdf",
        required=True,
        help="변환할 PDF 파일 경로"
    )
    parser.add_argument(
        "-m", "--model",
        choices=["gemini", "gpt"],
        default="gpt",
        help="이미지 분석에 사용할 AI 모델 (기본값: gpt)"
    )
    return parser.parse_args()


def convert_pdf_to_markdown(
    pdf_path: str,
    dpi: int = 150,
    image_format: str = "png"
) -> Tuple[str, str, str]:
    """
    PDF를 마크다운으로 변환

    PDF 경로가 ./folder1/folder2/file.pdf이면:
    - 출력 폴더: ./folder1/folder2/ (PDF와 같은 폴더)
    - 마크다운: ./folder1/folder2/file.md
    - 이미지: ./folder1/folder2/images/ (공통 폴더)

    Returns:
        (output_folder, markdown_file_path, cache_file_path)
    """
    # 파일 존재 확인
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

    # 출력 폴더는 PDF와 같은 폴더
    pdf_stem = pdf_file.stem
    output_folder = pdf_file.parent

    # 마크다운 파일 경로
    markdown_file = output_folder / f"{pdf_stem}.md"

    # 이미지 디렉토리 (공통 images 폴더)
    image_dir_abs = output_folder / "images"
    image_dir_abs.mkdir(parents=True, exist_ok=True)

    image_dir_relative = str(image_dir_abs)

    print(f"🔄 PDF 변환 시작...")
    print(f"📄 입력: {pdf_path}")
    print(f"📁 출력 폴더: {output_folder}")
    print(f"📄 마크다운: {markdown_file}")
    print(f"🖼️  이미지 저장: {image_dir_abs}")

    # PDF 변환
    markdown_text = pymupdf4llm.to_markdown(
        str(pdf_file),
        page_chunks=False,
        write_images=True,
        image_path=image_dir_relative,
        image_format=image_format,
        dpi=dpi
    )

    # 이미지 경로를 상대 경로로 수정
    print(f"\n🔧 이미지 경로를 상대 경로로 수정 중...")

    folder_prefix = str(output_folder.resolve())

    markdown_text = re.sub(
        rf'!\[([^\]]*)\]\({re.escape(folder_prefix)}/images/',
        r'![\1](images/',
        markdown_text
    )

    markdown_text = re.sub(
        rf'!\[([^\]]*)\]\({re.escape(str(output_folder))}/images/',
        r'![\1](images/',
        markdown_text
    )

    markdown_text = re.sub(
        r'!\[([^\]]*)\]\(.*/images/images/',
        r'![\1](images/',
        markdown_text
    )

    print(f"✅ 이미지 경로 수정 완료")

    # 마크다운 파일 저장
    markdown_file.write_text(markdown_text, encoding="utf-8")

    # 캐시 파일 경로 (출력 폴더에 image-cache_[폴더명].json 형식으로 저장)
    cache_file = output_folder / f"image-cache_{pdf_stem}.json"

    file_size_kb = len(markdown_text.encode("utf-8")) / 1024
    print(f"\n✅ 변환 완료!")
    print(f"📄 마크다운: {markdown_file}")
    print(f"📊 파일 크기: {file_size_kb:.2f} KB")
    print(f"📏 텍스트 길이: {len(markdown_text):,} 문자")
    print(f"💾 캐시 파일: {cache_file}")

    return str(output_folder), str(markdown_file), str(cache_file)


@dataclass
class ImageMatch:
    """이미지 매치 정보"""
    full_match: str
    alt_text: str
    image_path: str
    start_pos: int
    end_pos: int
    context_before: str
    context_after: str


class ImageDescriber:
    """이미지 설명 생성기"""

    def __init__(
        self,
        markdown_path: str,
        model_type: str = "gpt",
        context_chars: int = 1111,
        concurrent: int = 555,
        cache_file: str = ".image_cache.json",
        prompt_file: str = "prompt_book.md"
    ):
        self.markdown_path = Path(markdown_path)
        self.model_type = model_type.lower()
        self.context_chars = context_chars
        self.concurrent = concurrent
        self.cache_file = Path(cache_file)
        self.prompt_file = Path(prompt_file)

        self.cache = self._load_cache()
        self._load_prompt_template()

        # 모델 초기화
        if self.model_type == "gemini":
            self._init_gemini()
        else:
            self._init_openai()

        self.processed_count = 0
        self.total_count = 0
        self.lock = None

    def _load_cache(self) -> Dict:
        """캐시 로드"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding=FILE_ENCODING) as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 캐시 로드 실패: {e}")
        return {}

    def _save_cache(self):
        """캐시 저장"""
        try:
            with open(self.cache_file, 'w', encoding=FILE_ENCODING) as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 캐시 저장 실패: {e}")

    def _init_gemini(self):
        """Gemini 초기화"""
        import google.generativeai as genai

        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY 또는 GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")

        genai.configure(api_key=GOOGLE_API_KEY)
        self.gemini_client = genai.GenerativeModel(GOOGLE_MODEL)
        self.model_name = GOOGLE_MODEL
        print(f"🤖 Gemini 모델 초기화: {GOOGLE_MODEL}")

    def _init_openai(self):
        """OpenAI 초기화"""
        from openai import OpenAI

        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")

        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.model_name = OPENAI_MODEL
        print(f"🤖 OpenAI 모델 초기화: {OPENAI_MODEL}")

    def _load_prompt_template(self):
        """프롬프트 템플릿 로드"""
        try:
            with open(self.prompt_file, 'r', encoding=FILE_ENCODING) as f:
                self.prompt_template = f.read()
            print(f"✅ 프롬프트 템플릿 로드: {self.prompt_file}")
        except FileNotFoundError:
            print(f"⚠️ 프롬프트 파일을 찾을 수 없습니다: {self.prompt_file}")
            print(f"⚠️ 기본 프롬프트를 사용합니다.")
            self.prompt_template = """이미지를 분석하여 설명을 생성하세요.

Context before: {context_before}
Context after: {context_after}
Image: {image_path}"""
        except Exception as e:
            print(f"⚠️ 프롬프트 로드 실패: {e}")
            self.prompt_template = "이미지를 분석하세요."

    def find_images(self, content: str) -> List[ImageMatch]:
        """마크다운에서 이미지 찾기"""
        matches = []

        for match in re.finditer(IMAGE_PATTERN, content):
            alt_text = match.group(1)
            image_path = match.group(2)
            start_pos = match.start()
            end_pos = match.end()

            context_start = max(0, start_pos - self.context_chars)
            context_end = min(len(content), end_pos + self.context_chars)

            context_before = content[context_start:start_pos].strip()
            context_after = content[end_pos:context_end].strip()

            matches.append(ImageMatch(
                full_match=match.group(0),
                alt_text=alt_text,
                image_path=image_path,
                start_pos=start_pos,
                end_pos=end_pos,
                context_before=context_before,
                context_after=context_after
            ))

        return matches

    def _get_cache_key(self, image_match: ImageMatch) -> str:
        """캐시 키 생성"""
        key_data = f"{image_match.image_path}:{image_match.context_before}:{image_match.context_after}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def describe_image_gemini(self, image_match: ImageMatch, image_path: Path) -> str:
        """Gemini로 이미지 설명 생성"""
        prompt = self.prompt_template.format(
            image_match=image_match,
            context_before=image_match.context_before,
            context_after=image_match.context_after,
            image_path=str(image_path)
        )

        try:
            img = PIL.Image.open(image_path)
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                [prompt, img]
            )
            return response.text.strip()
        except Exception as e:
            print(f"  ❌ Gemini API 호출 실패: {e}")
            return "이미지 분석 실패"

    async def describe_image_gpt(self, image_match: ImageMatch, image_path: Path) -> str:
        """GPT로 이미지 설명 생성"""
        prompt = self.prompt_template.format(
            image_match=image_match,
            context_before=image_match.context_before,
            context_after=image_match.context_after,
            image_path=str(image_path)
        )

        try:
            # 이미지를 base64로 인코딩
            with open(image_path, "rb") as f:
                image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # 이미지 포맷 확인
            suffix = image_path.suffix.lower()
            if suffix == ".png":
                media_type = "image/png"
            elif suffix in [".jpg", ".jpeg"]:
                media_type = "image/jpeg"
            elif suffix == ".webp":
                media_type = "image/webp"
            elif suffix == ".gif":
                media_type = "image/gif"
            else:
                media_type = "image/png"

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.model_name,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}"
                            }
                        }
                    ]
                }],
                max_completion_tokens=4096
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  ❌ OpenAI API 호출 실패: {e}")
            return "이미지 분석 실패"

    async def describe_image(self, image_match: ImageMatch) -> str:
        """이미지 설명 생성 (캐시 활용)"""
        cache_key = self._get_cache_key(image_match)

        # 캐시 확인
        if cache_key in self.cache:
            print(f"  ✓ 캐시에서 로드: {image_match.image_path}")
            cached_data = self.cache[cache_key]
            if isinstance(cached_data, dict):
                return cached_data["description"]
            else:
                return cached_data

        # 이미지 파일 경로
        image_path = self.markdown_path.parent / image_match.image_path

        if not image_path.exists():
            print(f"  ⚠️ 이미지 파일 없음: {image_path}")
            return "이미지 파일 없음"

        print(f"  🔍 분석 중: {image_match.image_path}")

        # 모델에 따라 적절한 API 호출
        if self.model_type == "gemini":
            description = await self.describe_image_gemini(image_match, image_path)
        else:
            description = await self.describe_image_gpt(image_match, image_path)

        # 캐시에 저장
        self.cache[cache_key] = {
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "model": self.model_name
        }
        self._save_cache()

        return description

    async def process_images(self, matches: List[ImageMatch]) -> List[Tuple[ImageMatch, str]]:
        """이미지 병렬 처리"""
        self.total_count = len(matches)
        self.processed_count = 0
        self.lock = asyncio.Lock()

        semaphore = asyncio.Semaphore(self.concurrent)

        async def process_with_semaphore(match):
            async with semaphore:
                description = await self.describe_image(match)
                async with self.lock:
                    self.processed_count += 1
                    if self.processed_count % 10 == 0 or self.processed_count == self.total_count:
                        print(f"\n📊 진행률: {self.processed_count}/{self.total_count} ({self.processed_count*100//self.total_count}%)")
                return (match, description)

        tasks = [process_with_semaphore(match) for match in matches]
        results = await asyncio.gather(*tasks)

        print(f"\n{'='*60}")
        print(f"✅ 모든 이미지 처리 완료: {self.total_count}개")
        print(f"{'='*60}\n")

        return results

    def update_markdown(self, content: str, results: List[Tuple[ImageMatch, str]]) -> str:
        """마크다운 업데이트"""
        results_sorted = sorted(results, key=lambda x: x[0].start_pos, reverse=True)

        for match, description in results_sorted:
            description = description.replace('\n', ' ').strip()
            new_text = f"![{description}]({match.image_path})"
            content = content[:match.start_pos] + new_text + content[match.end_pos:]

        return content

    async def run(self):
        """메인 실행"""
        print(f"\n📝 마크다운 파일: {self.markdown_path}")
        print(f"🤖 LLM: {self.model_name} ({self.model_type})")
        print(f"⚡ 동시 처리: {self.concurrent}")
        print(f"📏 Context 길이: {self.context_chars}자")
        print(f"📋 프롬프트: {self.prompt_file}\n")

        # 파일 읽기
        with open(self.markdown_path, 'r', encoding=FILE_ENCODING) as f:
            content = f.read()

        # 이미지 찾기
        matches = self.find_images(content)
        print(f"🖼️  발견한 이미지: {len(matches)}개\n")

        if not matches:
            print("처리할 이미지가 없습니다.")
            return

        # 이미지 처리
        results = await self.process_images(matches)

        # 결과 출력
        print("\n" + "="*60)
        print("처리 결과:")
        print("="*60)
        for match, description in results[:5]:
            print(f"\n📍 {match.image_path}")
            print(f"   {description[:100]}...")

        # 마크다운 업데이트
        updated_content = self.update_markdown(content, results)

        # 백업 생성
        backup_path = Path(str(self.markdown_path) + BACKUP_EXTENSION)
        with open(backup_path, 'w', encoding=FILE_ENCODING) as f:
            f.write(content)
        print(f"\n💾 백업 생성: {backup_path}")

        # 파일 저장
        with open(self.markdown_path, 'w', encoding=FILE_ENCODING) as f:
            f.write(updated_content)
        print(f"✅ 파일 업데이트 완료: {self.markdown_path}")


def main():
    """메인 함수"""
    args = parse_args()

    print("\n" + "="*60)
    print("📚 PDF to Markdown Converter with AI Image Descriptions")
    print("="*60)
    print(f"📄 PDF: {args.pdf}")
    print(f"🤖 모델: {args.model}")
    print("="*60 + "\n")

    # 1. PDF -> 마크다운 변환
    output_folder, markdown_file, cache_file = convert_pdf_to_markdown(
        pdf_path=args.pdf,
        dpi=DPI,
        image_format=IMAGE_FORMAT
    )

    # 2. 이미지 설명 추가
    # prompt_file 경로 설정 (스크립트와 같은 디렉토리에 있다고 가정)
    script_dir = Path(__file__).parent
    prompt_file = script_dir / PROMPT_FILE

    describer = ImageDescriber(
        markdown_path=markdown_file,
        model_type=args.model,
        context_chars=CONTEXT_CHARS,
        concurrent=CONCURRENT,
        cache_file=cache_file,
        prompt_file=str(prompt_file)
    )

    asyncio.run(describer.run())

    print("\n" + "="*60)
    print("🎉 모든 작업 완료!")
    print(f"📄 결과 파일: {markdown_file}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
