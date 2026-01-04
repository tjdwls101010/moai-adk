서브에이전트 `builder-command`를 활용해 서브에이전트 `.claude/agents/Seongjin/Book-Architect.md`를 활용해 사용자가 제공한 책 pdf 파일을 재구조화하는 커맨드 `.claude/commands/Seongjin/Book-Architect.md`를 만들어주면 좋겠어요.
서브에이전트 `Seongjin_Agent_Book-Architect`는 평소에 내가 Claude 챗봇에서 시스템프롬프트로 적용해 사용하던 책 재구조화 프롬프트입니다.
사용자가 `/Book-Architect {source} "{지침}"`을 입력할 때, `{source}`는 pdf 파일입니다.
`Bash(ls)`로 `{source}`의 정확한 경로를 파악합니다.
그리고 스킬 `Seongjin_Book-Prep`를 사용해 책 pdf파일들을 적합한 목차에 따라 분할을 하고, 각각을 md파일로 변환합니다.
커맨드는 예를 들어 `/Book-Architect TMP/Value.pdf`를 입력받으면, `Bash(ls)`로 `TMP/Value.pdf`의 정확한 경로를 확인합니다.
그럼 아래처럼 결과를 받을겁니다.
```
ls TMP/Value.pdf
TMP/Value.pdf
```
`TMP/Value.pdf`에 대해 스킬 `Seongjin_Book-Prep`를 적용하면 아래처럼 파일들이 생성될 겁니다.
```
TMP/Value
├── 1. Title Page
│   ├── 1. Title Page.md
│   ├── 1. Title Page.md.md.backup
│   └── images
│       ├── 1.-Title-Page.pdf-0-0.png
│       └── 1.-Title-Page.pdf-1-0.png
├── 1. Title Page.pdf
├── 2. Copyright
│   ├── 2. Copyright.md
│   └── images
├── 2. Copyright.pdf
├── 3. Dedication
│   ├── 3. Dedication.md
│   └── images
├── 3. Dedication.pdf
├── 4. Contents
│   ├── 4. Contents.md
│   └── images
├── 4. Contents.pdf
├── 5. Introduction
│   ├── 5. Introduction.md
│   └── images
├── 5. Introduction.pdf
├── 6. Part I – The Rise of the Market Society
│   ├── 6. Part I – The Rise of the Market Society.md
│   ├── 6. Part I – The Rise of the Market Society.md.md.backup
│   └── images
│       └── 6.-Part-I-–-The-Rise-of-the-Market-Society.pdf-48-0.png
├── 6. Part I – The Rise of the Market Society.pdf
├── 7. Part II – Three Crises of Value(s)
│   ├── 7. Part II – Three Crises of Value(s).md
│   ├── 7. Part II – Three Crises of Value(s).md.md.backup
│   └── images
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-100-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-101-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-113-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-119-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-119-1.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-121-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-123-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-125-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-127-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-129-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-131-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-131-1.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-133-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-142-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-142-1.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-147-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-149-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-152-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-154-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-164-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-167-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-168-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-169-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-170-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-178-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-196-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-199-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-34-0.png
│       ├── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-49-0.png
│       └── 7.-Part-II-–-Three-Crises-of-Value(s).pdf-50-0.png
├── 7. Part II – Three Crises of Value(s).pdf
├── 8. Part III – Reclaiming Our Values
│   ├── 8. Part III – Reclaiming Our Values.md
│   ├── 8. Part III – Reclaiming Our Values.md.md.backup
│   └── images
│       ├── 8.-Part-III-–-Reclaiming-Our-Values.pdf-101-0.png
│       ├── 8.-Part-III-–-Reclaiming-Our-Values.pdf-125-0.png
│       ├── 8.-Part-III-–-Reclaiming-Our-Values.pdf-126-0.png
│       ├── 8.-Part-III-–-Reclaiming-Our-Values.pdf-129-0.png
│       ├── 8.-Part-III-–-Reclaiming-Our-Values.pdf-130-0.png
│       ├── 8.-Part-III-–-Reclaiming-Our-Values.pdf-154-0.png
│       ├── 8.-Part-III-–-Reclaiming-Our-Values.pdf-156-0.png
│       ├── 8.-Part-III-–-Reclaiming-Our-Values.pdf-85-0.png
│       ├── 8.-Part-III-–-Reclaiming-Our-Values.pdf-95-0.png
│       └── 8.-Part-III-–-Reclaiming-Our-Values.pdf-98-0.png
├── 8. Part III – Reclaiming Our Values.pdf
├── 9. Conclusion_ Humility
│   ├── 9. Conclusion_ Humility.md
│   └── images
├── 9. Conclusion_ Humility.pdf
└── toc.json
```
그리고 여기서 md 파일들을 `Bash()`로 모두 검색해, 파일 경로를 확보합니다.
그리고 각각의 md를 병렬적으로 에이전트 `Seongjin_Agent_Book-Architect`에 입력합니다.
예를 들어, 아래처럼요.
```
Input File: TMP/Value/5. Introduction/5. Introduction.md
Output File: TMP/Value/5. Introduction/Reconstructed_5. Introduction.md
```
```
Input File: TMP/Value/6. Part I – The Rise of the Market Society/6. Part I – The Rise of the Market Society.md
Output File: TMP/Value/6. Part I – The Rise of the Market Society/Reconstructed_6. Part I – The Rise of the Market Society.md
```
```
Input File: TMP/Value/7. Part II – Three Crises of Value(s)/7. Part II – Three Crises of Value(s).md
Output File: TMP/Value/7. Part II – Three Crises of Value(s)/Reconstructed_7. Part II – Three Crises of Value(s).md
```
서브에이전트에 어떤 파일 경로를 입력하면, 그 파일 경로의 파일을 `Read()`(파일의 크기가 너무 커서 Error가 발생한다면 `Bash(cat)`으로 전체를 읽어야 함. 어떤 경우에도 파일을 일부만 읽어서는 안됨. 반드시 전체 내용을 읽어야 함.)하고,  `Write()`해 md 파일로 저장해야해.
에이전트 `Seongjin_Agent_Book-Architect`는 현재 다른 AI-IDE에서 사용하던 시스템프롬프트라, Claude-Code상에서 서브에이전트로 사용하기에 적합하지 않을 수 있어요.
그래서 서브에이전트 `builder-agent`로 서브에이전트 `Seongjin_Agent_Book-Architect`를 적합하게 개선해주면 좋겠어요.
커맨드 `Book-Architect`와 서브에이전트 `Seongjin_Agent_Book-Architect`를 만드는게 목표야.
너가 직접 서브에이전트 `builder-agent`와 `builder-command`를 읽을 필요는 없이, 활용을 하면 되.
스킬 `Seongjin_Book-Prep`에 따라 toc 파일에 대해서는 `Read()`를 해도 되지만, 그 이외에 메인 에이전트는 직접 `Read()`를 하진 않아야 하며, 오로지 파일 경로를 파악하고 서브에이전트에 파일 경로를 제공하는 조율자로서의 역할만 해야합니다.

전체적으로 이해가 되니?