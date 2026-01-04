서브에이전트 `builder-command`를 활용해 서브에이전트 `Seongjin_Agent_Nano-Banana`를 활용해 `Nano-Banana`로 PPT 슬라이드를 생성하는 커맨드 `ppt`를 만들고 싶어요.
구체적으로 어떻게 커맨드를 만들지 당신과 함께 논의하고 싶어요.
내가 뭘 만들고자 하는지는 `.seongjin/PPT_Nano-Banana/HISTORY.md`에 내용이 포함되어 있어요.
이를 참조하세요.

---

사용자가 `/ppt {source} "{지침}"`을 입력할 때, `{source}`는 폴더일 수도 있고, 개별 마크다운 파일일 수도 있어.
`{source}`가 폴더라면 `Bash(ls)`로 폴더에 포함된 파일들을 확인하고, 사용자에게 `AskUserQuestion`로 어떤 파일들을 ppt를 만드는데 사용할지 multi-select할 수 있도록 해.
그리고 각각의 파일 경로를 서브에이전트 `Seongjin_Agent_PPT-Planner`에 입력해, 서브에이전트로 하여금 `Read()`하고 PPT 슬라이드 개요를 json으로 작성해 `Write()`해 저장하도록 하는거지.
이렇게 각각의 파일에 대해 작성되고 저장된 PPT 슬라이드 개요 json 파일을 메인에이전트가 모두 `Bash`(또는 다른 방법도 괜찮아)로 통합 json 파일을 생성하고.
통합 json을 `Read()`해 사용자에게 개선하고 싶은 부분이 있는지 `AskUserQuestion`로 피드백을 받아.
그리고 개요에 대한 피드백이 완료되면, 사용자에게 `AskUserQuestion`로 적절한 디자인 옵션을 제안해주고 선택받는거지.
그리고 선택된 디자인과 각 슬라이드 페이지에 대한 정보를 병렬적으로 서브에이전트 `Seongjin_Agent_Nano-Banana`에 입력해 슬라이드를 만들도록 합니다.
각각의 서브에이전트가 생성한 이미지는 하나의 폴더에 저장되어야 하고.
모든 서브에이전트의 작업이 완료되면, 메인 에이전트는 스킬 `pdf`로 이미지를 병합해 하나의 pdf 파일을 같은 폴더에 저장합니다.

---

커맨드를 만들 땐, `builder-command`를 사용해야 합니다.
서브에이전트를 만들 땐, `builder-agent`를 사용해야 합니다.

---

`Seongjin_Agent_PPT-Planner`로 ppt 개요를 json 형식으로 완성하고 `AskUserQuestion`로 사용자의 피드백을 받잖아.
근데 `AskUserQuestion`를 사용하는 주체가 서브에이전트가 아닌 메인에이전트인 거 같네.
그럼 메인 에이전트가 서브에이전트가 읽었던 파일을 직접 읽어야 하잖아.
그보단 서브에이전트를 `resume()`해서 json을 수정하라고 요청하는게 더 낫지 않아?

---

내가 뭘 만들고자 하는지는 `.seongjin/PPT_Nano-Banana/HISTORY.md`에 내용이 포함되어 있어요.
Nano-Banana 이미지 생성 모델을 사용해 16:9 비율의 PPT 슬라이드를 만들어야 하며, 예시는 `.seongjin/PPT_Nano-Banana/References/The Adoption and Usage of AI Agents/Agent_AI_First_Field_Report conv_png`를 보면 알 수 있을거예요.
우선 서브에이전트 `builder-agent`를 활용해 서브에이전트 `.claude/agents/Seongjin_Agent_PPT-Planner.md`를 만들고 싶어요.
서브에이전트에 어떤 파일 경로를 입력하면, 그 파일 경로의 파일을 `Read()`(파일의 크기가 너무 커서 Error가 발생한다면 `Bash(cat)`으로 전체를 읽어야 함. 어떤 경우에도 파일을 일부만 읽어서는 안됨. 반드시 전체 내용을 읽어야 함.)하고, PPT 슬라이드 개요를 `Write()`해 json 파일로 저장해야해.
`.claude/PPT-Planner.md`은 이전에 만든 서브에이전트인데, 이는 각 슬라이드를 markdown 파일로 만드는데, 난 지금 하나의 json파일로 만들려는 거야. 그래도 참고할 내용은 있을거야.
`.claude/Nano-Banana.md`은 이전에 만든 서브에이전트인데, Nano-Banana MCP를 활용해 직접 이미지를 생성하는 기능을 해. 이후에 Nano-Banana를 MCP가 아니라 코드를 사용할거야. 그래서 우리가 지금 만들고자 하는 `Seongjin_Agent_PPT-Planner`은 단지 계획을 하는거야. 이후에 코드에 입력될 각 슬라이드의 프롬프트를 만들려는게 목표야. `.claude/Nano-Banana.md`를 보면, Nano-Banana를 위한 프롬프트 엔지니어링 기법 등이 포함되어 있어요. 이를 json 형식의 계획을 작성할 때, 프롬프트가 최적의 프롬프트 엔지니어링 기법이 적용되어 있어야 해.

---

너가 이전에 만든 서브에이전트 `Seongjin_Agent_PPT-Planner`는 훌륭해.
다만 그 결과로 만들어낸 `TMP/📰보수 개신교의 탄생_slides_v2.json`를 내가 직접 확인해보니, `text_content`, `layout`, `visual_element`이라는 key는 따로 필요가 없을거 같아.
실제 Nano-Banana에 입력하는건 `nano_banana_prompt` 뿐이거든. 
서브에이전트 `builder-agent`를 활용해 이점을 개선해줄 수 있을까?

---

`TMP/README.md`에 명시된 코드에 우리가 만든 json을 입력해 실행해봐.

---

이제 `.claude/commands/ppt.md`를 만들고 싶어.
사용자가 `/ppt {source} "{지침}"`을 입력할 때, `{source}`는 폴더일 수도 있고, 개별 마크다운 파일일 수도 있어.
`{source}`가 폴더라면 `Bash(ls)`로 폴더에 포함된 파일들을 확인하고, 사용자에게 `AskUserQuestion`로 어떤 파일들을 ppt를 만드는데 사용할지 multi-select할 수 있도록 해.
그리고 각각의 파일 경로를 서브에이전트 `Seongjin_Agent_PPT-Planner`에 입력해, 서브에이전트로 하여금 `Read()`하고 PPT 슬라이드 개요를 json으로 작성해 `Write()`해 저장하도록 하는거지.
이때 주의해야 할 사항은 메인 에이전트는 직접 파일들을 `Read()`하지 않는다는 거야. 단지 서브에이전트에게 파일의 경로를 전달하는 역할만을 하면 되.
이렇게 각각의 파일에 대해 `TMP/README.md`에 명시된 코드에 파라미터로 입력해 슬라이드를 만드는 커맨드를 만들고 싶은거야.
커맨드를 만들 땐, `builder-command`를 사용하면 좋겠어.

---

우리가 지금까지 커맨드와 서브에이전트를 잘 만들었어.
우리가 실제 이미지를 생성할 때, `TMP/README.md`를 참조해 `TMP/Nano-Banana.py`를 실행해.
근데 다른 로컬 환경에서도 이 코드를 잘 사용하려면 Claude-Code에서 사용할 수 있도록 스킬로 만들려고 해.
`builder-skill`로 스킬을 만들거야.
`.claude/skills/Seongjin_Skill_Nano-Banana`에 스킬을 만들어주면 좋겠어.
코드는 `.claude/skills/Seongjin_Skill_Nano-Banana/Scripts/Nano-Banana.py`로 옮겨두었으니, 이를 사용하도록 `.claude/skills/Seongjin_Skill_Nano-Banana/SKILL.md`를 작성해주면 되.
스킬을 모두 만들고 나서는 아마 우리가 만들었던 커맨드 `.claude/commands/Seongjin/PPT.md`를 수정할 필요가 있을거야.

---

커맨드가 모든 작업을 완료하고, 아래와 같은 질문을 하네.
```
다음 작업을 선택해 주세요.

  1. 이미지 확인
     생성된 슬라이드 이미지 폴더 열기
  2. 추가 파일 처리
     다른 마크다운/PDF 파일로 PPT 생성
  3. 슬라이드 수정
     JSON 파일 편집 후 이미지 재생성
❯ 4. 완료
     세션 종료
  5. Type something.
```
이 과정은 딱히 필요없을거 같아. 곧바로 작업을 요약해서 사용자에게 설명해줘.
만약 사용자가 생각하기에 피드백이 필요하면 말할거야. 굳이 먼저 물어볼 필요 없어.
이에 맞게 커맨드를 수정해줘.

중간에 커맨드가 실행하는 과정에서 아래와 같은 오류가 발생했어.
이런 오류가 반복되지 않도록 커맨드를 개선해줄 수 있을까?
```
⏺ Bash(uv run python "$CLAUDE_PROJECT_DIR/.claude/skills/Seongjin_Skill_Nano-Banana/Scripts/Nano-Banana.py" '/Users/seongjin/Cursor/moai-adk/TMP/examples/PPT_📰실리콘밸리의           timeout: 10m 
      유령/Plan_📰실리콘밸리의 유령.json' --output-dir '/Users/seongjin/Cursor/moai-adk/TMP/examples/PPT_📰실리콘밸리의 유령/')                                                        0s
  ⎿  Error: Exit code 2
     /Users/seongjin/Cursor/moai-adk/.venv/bin/python3: can't open file '/.claude/skills/Seongjin_Skill_Nano-Banana/Scripts/Nano-Banana.py': [Errno 2] No such file or directory
```

커맨드를 사용하는 과정에서 아래와 같은 오류가 나오는 경우가 있어.
왜그러지?
```
  JSON 파일을 읽어보니 파일 자체는 정상적으로 보입니다. JSON 파싱 에러가 발생했다고 했는데, line 42 column 283에서 문제가 있다고 했습니다. 

  line 42를 보면:
  "nano_banana_prompt": "Create a professional presentation slide image with data visualization and metaphor. Title at top in large bold dark teal text: '민주주의 침식은 거의 감지할 수 없다'. Left 
  side (40%): large prominent statistic '51%' in dark teal with label below '2011년 베네수엘라 국민이 자국을 "매우 민주적"으로 평가'. Below that, text: '경보벨을 울릴 단일한 순간이 없음'. Right 
  side (60%): conceptual illustration of slowly boiling frog in pot metaphor - frog sitting in pot with subtle steam rising, thermometer showing gradual temperature increase, peaceful expression on
   frog suggesting unawareness. Clean line art illustration style with muted colors. Light warm background. Subtle warning symbolism. 16:9 aspect ratio, 1920x1080 resolution. Korean text and 
  numbers clearly readable."

  여기서 "매우 민주적"이라는 부분에 이중 따옴표가 있어서 JSON 파싱 에러가 발생한 것 같습니다. 이스케이프 처리가 안되어 있네요.

  Python으로 다시 검증해보겠습니다. 일단 파일을 수정해야 합니다.

⏺ JSON 파일에서 line 42에 이스케이프되지 않은 이중 따옴표 문제가 있습니다.
```

---

`Bash(uv run python /Users/seongjin/Cursor/moai-adk/.claude/skills/Seongjin_Nano-Banana/Scripts/Nano-Banana.py "TMP/examples/PPT_5.민주주의의 가드레일/Plan_5.민주주의의              timeout: 10m 가드레일.json" --output-dir "TMP/examples/PPT_5.민주주의의 가드레일")`

---

서브에이전트 `builder-command`를 활용해 서브에이전트 `Seongjin_Agent_Knowledge-Architect`를 활용해 사용자가 제공한 정보를 재구조화하는 커맨드 `Knowledge-Architect`를 만들어주면 좋겠어요.
서브에이전트 `Seongjin_Agent_Knowledge-Architect`는 평소에 내가 Claude 챗봇에서 시스템프롬프트로 적용해 사용하던 정보 재구조화 프롬프트입니다.
사용자가 `/Knowledge-Architect {source} "{지침}"`을 입력할 때, `{source}`는 폴더일 수도 있고, 개별 마크다운 파일일 수도 있어.
`{source}`가 폴더라면 `Bash(ls)`로 폴더에 포함된 파일들을 확인하고, `{source}`가 파일이라면 `Bash(ls)`로 파일의 정확한 경로를 확인해야 합니다.
그리고 `{source}`가 폴더이든 파일이든, 각 파일에 대해 병렬적으로 `Seongjin_Agent_Knowledge-Architect`에 파일 경로를 제공해 처리를 지시해야 해요.
메인 에이전트는 직접 `Read()`를 하진 않아야 하며, 오로지 파일 경로를 파악하고 서브에이전트에 파일 경로를 제공하는 조율자로서의 역할만 해야합니다.

커맨드는 예를 들어 `/Knowledge-Architect TMP/examples2`를 입력받으면, `Bash(ls)`로 `TMP/examples2`에 포함된 파일들을 확인합니다.
그럼 아래처럼 결과를 받을겁니다.
```
ls TMP/examples2
0.서론.md
1.운명적 동맹.md
```
그럼 해당 폴더 내에 `{name_folder}/Reconstruct_{name_File}`를 만들어야 해.
서브에이전트에 어떤 파일 경로를 입력하면, 그 파일 경로의 파일을 `Read()`(파일의 크기가 너무 커서 Error가 발생한다면 `Bash(cat)`으로 전체를 읽어야 함. 어떤 경우에도 파일을 일부만 읽어서는 안됨. 반드시 전체 내용을 읽어야 함.)하고, 재구조화 파일을 `Write()`해 md 파일로 저장해야해.
예를 들어, `TMP/examples2/Reconstruct_0.서론`, `TMP/examples2/Reconstruct_1.운명적 동맹`를 만드는 겁니다.
그리고 나서 `Seongjin_Agent_Knowledge-Architect`에게 이런식의 입력을 해서 작업을 하도록 하는거죠.
```
Input File: TMP/examples2/0.서론.md
Output File: TMP/examples2/Reconstruct_0.서론/Reconstruct_0.서론.md
```
서브에이전트 `Seongjin_Agent_Knowledge-Architect`는 현재 내가 Claude 챗봇에서 사용하던 시스템프롬프트라, Claude-Code상에서 서브에이전트로 사용하기에 적합하지 않을 수 있어요.
그래서 서브에이전트 `builder-agent`로 서브에이전트 `Seongjin_Agent_Knowledge-Architect`를 적합하게 개선해주면 좋겠어요.

커맨드 `Knowledge-Architect`와 서브에이전트 `Seongjin_Agent_Knowledge-Architect`를 만드는게 목표야.
너가 직접 서브에이전트 `builder-agent`와 `builder-command`를 읽을 필요는 없이, 활용을 하면 되.
전체적으로 이해가 되니?

---

서브에이전트 `builder-command`를 활용해 서브에이전트 `Seongjin_Agent_Mermaid-Architect`를 활용해 사용자가 제공한 정보를 Mermaid 다이어그램으로 변환하는 커맨드 `Mermaid-Architect`를 만들어주면 좋겠어요.
서브에이전트 `Seongjin_Agent_Mermaid-Architect`는 평소에 내가 Claude 챗봇에서 시스템프롬프트로 적용해 사용하던 Mermaid 다이어그램으로 변환 프롬프트입니다.
사용자가 `/Mermaid-Architect {source} "{지침}"`을 입력할 때, `{source}`는 폴더일 수도 있고, 개별 마크다운 파일일 수도 있어.
`{source}`가 폴더라면 `Bash(ls)`로 폴더에 포함된 파일들을 확인하고, `{source}`가 파일이라면 `Bash(ls)`로 파일의 정확한 경로를 확인해야 합니다.
그리고 `{source}`가 폴더이든 파일이든, 각 파일에 대해 병렬적으로 `Seongjin_Agent_Mermaid-Architect`에 파일 경로를 제공해 처리를 지시해야 해요.
메인 에이전트는 직접 `Read()`를 하진 않아야 하며, 오로지 파일 경로를 파악하고 서브에이전트에 파일 경로를 제공하는 조율자로서의 역할만 해야합니다.

커맨드는 예를 들어 `/Mermaid-Architect TMP`를 입력받으면, `Bash(ls)`로 `TMP`에 포함된 파일들을 확인합니다.
그럼 아래처럼 결과를 받을겁니다.
```
ls TMP
조던피터슨.md
Widening Inequalities of Place.md
```
그럼 해당 폴더 내에 `{name_folder}/Mermaid_{name_File}`를 만들어야 해.
서브에이전트에 어떤 파일 경로를 입력하면, 그 파일 경로의 파일을 `Read()`(파일의 크기가 너무 커서 Error가 발생한다면 `Bash(cat)`으로 전체를 읽어야 함. 어떤 경우에도 파일을 일부만 읽어서는 안됨. 반드시 전체 내용을 읽어야 함.)하고, Mermaid 파일을 `Write()`해 md 파일로 저장해야해.
예를 들어, `TMP/Mermaid_조던피터슨/Mermaid_조던피터슨.md`, `TMP/Mermaid_Widening Inequalities of Place/Mermaid_Widening Inequalities of Place.md`를 만드는 겁니다.
`Seongjin_Agent_Mermaid-Architect`에게 이런식의 입력을 해서 작업을 하도록 하는거죠.
```
Input File: TMP/조던피터슨.md
Output File: TMP/Mermaid_조던피터슨/Mermaid_조던피터슨.md
```
서브에이전트 `Seongjin_Agent_Mermaid-Architect`는 현재 내가 Claude 챗봇에서 사용하던 시스템프롬프트라, Claude-Code상에서 서브에이전트로 사용하기에 적합하지 않을 수 있어요.
그래서 서브에이전트 `builder-agent`로 서브에이전트 `Seongjin_Agent_Mermaid-Architect`를 적합하게 개선해주면 좋겠어요.

커맨드 `Mermaid-Architect`와 서브에이전트 `Seongjin_Agent_Mermaid-Architect`를 만드는게 목표야.
너가 직접 서브에이전트 `builder-agent`와 `builder-command`를 읽을 필요는 없이, 활용을 하면 되.

그리고 현재 `Seongjin_Agent_Mermaid-Architect`는 사용자가 입력한 정보를 Claude가 스스로 생각해 구조화하고, 사용자와 끊임없이 소통하며 논리를 채워나가도록 설계되어 있어요.
굳이 사용자와 소통하며 진행할 필요없이, Claude가 자체적으로 사용자로부터 입력받은 정보를 처음부터 끝까지 꼼꼼히 읽고 이해해 재구조화하고 Mermaid를 작성해주면 됩니다.

전체적으로 이해가 되니?

---

`builder-skill`를 사용해 `.claude/skills/Seongjin_Book-Prep`를 만들어주면 좋겠어요.
`.claude/skills/Seongjin_Book-Prep/Scripts`에 내가 기존에 만든 코드를 저장해놨는데, 이들 코드의 내용은 `.claude/skills/Seongjin_Book-Prep/SKILL.md`를 참조하시면 됩니다.
pdf 형식의 책을 사용자가 입력하면, 이를 LLM을 사용해 분석을 할거야.
그런데 책 전체를 LLM에 입력하면 Context Overflow가 발생할 수 있기 때문에, 적합한 단위로 pdf를 분할하는게 중요해.
`check_toc.py`로 toc를 만들어 책의 각 목차가 얼마만큼의 분량을 가지는지 알 수 있으며, 목차의 제목으로 내용을 추측할 수도 있을겁니다.
`TMP/Split_PDF/Examples/The Idea of Justice/toc.json`를 읽으면 toc 파일이 어떻게 구성되어 있는지 알 수 있을거야.
`check_toc.py`를 통해 만들어진 toc를 확인해 pdf 분할하는데 적절한 level을 선택할 수 있을겁니다.
앞서 결정한 level을 바탕으로 `split_pdf.py`로 pdf를 분할할 수 있어요.
그리고 그렇게 해서 만들어진 각 분할된 pdf에 대해 `pdf_to_md.py`를 적용해 마크다운으로 변환해야 해요.
이렇게 마크다운으로 변환하는 이유는 Claude-Code는 pdf를 읽어 분석할 수 없기 때문이야.

또한 `pdf_to_md.py`는 pdf에 포함된 각 이미지에 대해 llm api를 호출해 텍스트화 해서 Claude-Code가 텍스트 뿐만 아니라 이미지까지도 분석대상으로 삼을 수 있도록 하고 있어.
근데 여기서 중요한게 pdf의 분할 level을 결정하는거야.
너무 자잘하게 분할하면 분석하는데 있어서 맥락이 충분히 반영되지 않을 수 있고, 너무 크게 분할하면 Context Overflow가 발생할 수 있어.

`TMP/Split_PDF/Examples/Value.pdf`에 대해 분할한다면, level=1로 분할해 아래와 같이 분할하면 좋겠어.
```
Part I – The Rise of the Market Society.pdf
Part II – Three Crises of Value(s).pdf
Part III – Reclaiming Our Values.pdf
```
`TMP/Split_PDF/Examples/The Idea of Justice.pdf`에 대해 분할한다면, level=2로 분할해 아래와 같이 분할하면 좋겠어.
```
Introduction.pdf
PART ONE: The Demands of Justice.pdf
PART TWO: Forms of Reasoning.pdf
PART THREE: The Materials of Justice.pdf
PART FOUR: Public Reasoning and Democracy.pdf
```
`TMP/Split_PDF/Examples/Outclassed.pdf`에 대해 분할한다면, level=1로 분할해 아래와 같이 분할하면 좋겠어.
```
Part I: Aren’t You Sick of Losing Elections or Just Scraping By?.pdf
Part II: What’s the Matter with Kansas?.pdf
Part III: What’s the Matter with Cambridge?.pdf
Part IV: The Path Past Far-Right Populism.pdf
```

분할 레벨은 본문의 최상위 레벨로 정하면 좋겠어요.
일반적으로 본문의 최상위 레벨이 level=1인 경우가 많은데, 때때로 어떤 pdf 파일은 level=1이 서론, 본론, 결론으로 구성되어서, 이런 경우에 level=1로 분할하면 본문 수백 페이지(전체 pdf의 90% 이상)가 하나의 파일에 포함되어 버리는데, 이런건 적절한 분할이라고 말할 수 없어.

`builder-skill`를 사용해 `.claude/skills/Seongjin_Book-Prep/SKILL.md`를 적절히 수정해줘요.
너가 직접 서브에이전트 `builder-skill`를 읽을 필요는 없이, 활용을 하면 되.
전체적으로 이해가 되니?

---

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

---

내가 만든 커맨드, 서브에이전트, 스킬을 사용하는 과정에서 혹시 오류가 나거나 내 목적에 어긋나게 잘못 행동하는 경우가 있었나?
이런 경우가 반복되지 않도록, 이들 파일을 개선할 점이 있을지 살펴보고 제안해줘.
그리고 서브에이전트를 병렬로 실행하는데 background로 실행하지 말고 항상 foreground로 모두 병렬로 실행하면 좋겠습니다.
그리고 스킬을 사용할 때, gpt가 아니라 gemini를 사용하도록 파라미터를 사용하는데, 사용자가 명시적으로 요청하지 않는 이상 이 파라미터는 사용하지 않으면 좋겠어요.
`skill.md`에 모델 파라미터에 대한 지시가 있다면 수정해줘.

---

첨부한 `PPT-Planner.md`는 제가 만든 서브에이전트 정의입니다.
이는 사용자가 마크다운 파일 경로를 입력하면, 그 파일을 `Read()`해서 `Plan_보유세 강화하면 수요 억제될까?.json`와 같은 PPT 개요 json 파일을 만들어줍니다.
PPT는 Nano-Banana-Pro라는 이미지 생성 ai모델을 사용해 만들기 때문에, 각 슬라이드에 Nano-Banana-Pro에 최적화된 프롬프트를 만듭니다.

이 서브에이전트의 시스템프롬프트를 Claude 챗봇의 시스템프롬프트로 수정하고자 합니다.
Nano-Banana-Pro에 최적화된 프롬프트를 생성하되, 이는 첨부한 이미지와 같은 국회의원 홍보자료를 만들기 위한 시스템프롬프트를 만드는게 목적입니다.
첨부한 파일들을 모두 `Read()`해 홍보자료는 어떤 디자인을 가져야할지, 어떤 텍스트 정보를 포함하면 좋을지 등을 파악하세요. 
예컨데 당신이 만든 시스템프롬프트가 적용된 챗봇에 사용자가 아래와 같은 텍스트를 입력하면, 이 텍스트를 포함하는 Nano-Banana-Pro 프롬프트를 생성하는 겁니다.
여기에 디자인도 당신이 이 시스템프롬프트를 만드는 과정에서 참조한 이미지들에서 획득한 인사이트를 바탕으로 제안해줘야겠죠.
```
우리 동네 안전, 든든하게 지키겠습니다

[혜화경찰서 동묘파출소 ]

이전 신축!
총사업비 88억 8천 2백만 원중,
7억 3천만 원 2026년 예산 반영 확정!

앞으로도 종로의 안전 인프라 확충에
최선을 다하겠습니다.
```
또는 사용자가 어떤 이미지(`카드뉴스 예시.png`)와 인물 이미지(`인물.png`)를 제공하면 프롬프트에는 해당 파일명이 포함되어야 해.
그래야 Nano-Banana-Pro가 사용자로부터 같은 이미지와 당신이 만든 텍스트 프롬프트를 종합해 일관성 있는 이미지를 생성할 수 있을테니까.

`/mnt/user-data/uploads/PPT-Planner.md`를 `/mnt/user-data/outputs/PPT-Planner.md`로 복제해서 저장하세요.
`/mnt/user-data/outputs/PPT-Planner.md`를 Claude 챗봇에 적합하도록 수정해주세요.

전체적으로 무슨 의도인지 알겠니?
그럼 일단 `/mnt/user-data/outputs/PPT-Planner.md`를 내 의도에 맞게 수정해주고, 이후에 참조하면 좋을만한 모범 홍보자료 이미지를 제공해줄게.
이를 참조해 넌 다시 시스템프롬프트를 개선하는거지.

---

참고로 홍보자료는 언제나 9:16비율을 가질거야.

---

`TMP/Convert_Image-Link_Wiki-to-Markdown.py`를 만들어주면 좋겠어.
가상환경도 `TMP`에 구성해줘.
`TMP/📰2025 세대·젠더 국민통합 조사.md`와 같은 마크다운 파일을 사용자가 파라미터로 입력하면, 여기서 `![[Path_Image.png(or jpg or wbep etc)]]`을 `![](Path_Image.png(or jpg or wbep etc))`으로 교체하는 코드를 만들어줘. 

---

내가 만든 커맨드 `.claude/commands/Seongjin/PPT.md`를 실행하면, 사용자가 입력한 마크다운 파일 경로를 서브에이전트 `.claude/agents/Seongjin/PPT-Planner.md`에 입력해.
그리고 서브에이전트는 마크다운 파일의 내용 전체를 읽고, 포함된 이미지는 코드베이스 전체에서 search해 read한 다음에 ppt를 만드는데 도움이 될 만한 이미지를 계획 json파일에 reference_image 필드에 포함시키는 로직을 가지고 있어.

근데 서브에이전트에게 마크다운에 포함된 모든 이미지를 코드베이스에서 경로를 검색하고, 이를 read해 필요한 이미지를 선별하는 과정을 모두 맡기는게 context overflow를 발생시킬 우려가 커.
그래서 `.claude/skills/Seongjin_Image-Describer/Scripts/Convert_Image-Link_Wiki-to-Markdown.py`를 만들었어.
이 코드는 사용자가 제공한 마크다운 파일에서 `![[Path_Image.png(or jpg or wbep etc)]]`를 `![Description_Image](Path_Image)`로 교체하는 기능을 가져.
예를 들어, `![[bc57e2d31c4ec56fcaee47c0ea0d08b1_MD5.jpg]]`를 `![이 사진은 새벽 배송 금지 논쟁에서 노동자 대표와 관계자들이 공개 토론회에서 발언하며 대안과 쟁점을 직접 제시하는 장면을 보여준다.](🧷Attachments/bc57e2d31c4ec56fcaee47c0ea0d08b1_MD5.jpg)`와 같이 교체하는거야.

`.claude/skills/Seongjin_Image-Describer`는 `.claude/skills/Seongjin_Image-Describer/Scripts`에 필요한 코드는 저장해놓은 상태야.
`TMP/README.md`의 내용을 참조해, 이 코드를 Claude에서 사용하는 스킬로 서브에이전트 `builder-skill`를 사용해 `.claude/skills/Seongjin_Image-Describer/SKILL.md`를 만들고 싶어.

커맨드의 워크플로우 상, 스킬 `Seongjin_Image-Describer`을 통해 마크다운 파일에 대해 포함된 이미지 링크를 `![Description_Image](Path_Image)`로 교체하고나서, 서브에이전트에게 그 마크다운 파일의 경로를 입력해 계획을 만들도록 하면 되.
이렇게 `![Description_Image](Path_Image)`의 형태로 마크다운 파일 내에 이미지가 포함되어 있으면, 굳이 서브에이전트가 모든 이미지를 read할 필요는 없을거야.
이 `Description_Image`을 읽어 ppt를 만드는데 필요할지 판별하고, 이 과정에서 서브에이전트가 필요 여부를 판단할 때 read할 수는 있겠지.
다만 서브에이전트가 이전처럼 모든 이미지 파일을 read할 필요는 없어 이렇게 스킬을 사용해 미리 첨부 이미지의 `Description_Image`를 만들어놓는 과정이 효율성은 올려줄 수 있을거라 생각해.

이 작업을 하기 위해 커맨드와 서브에이전트를 수정할 필요가 있으면 수정해줘.
스킬을 만들 때는 서브에이전트 `builder-skill`를 사용하면 되고, 너가 직접 `builder-skill`를 읽을 필요는 없이, 활용을 하면 되.