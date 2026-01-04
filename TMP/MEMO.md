`TMP/Convert_Image-Link_Wiki-to-Markdown.py`를 만들어주면 좋겠어.
가상환경도 `TMP`에 구성해줘.
`TMP/📰2025 세대·젠더 국민통합 조사.md`와 같은 마크다운 파일을 사용자가 파라미터로 입력하면, 여기서 `![[Path_Image.png(or jpg or wbep etc)]]`을 `![](Path_Image.png(or jpg or wbep etc))`으로 교체하는 코드를 만들어줘. 

---

`Codes/Convert_Image-Link_Wiki-to-Markdown.py`은 `![[Path_Image.png(or jpg or wbep etc)]]`을 `![](Path_Image.png(or jpg or wbep etc))`으로 교체하는 코드야.
`Codes/📰쿠팡 노동자들 이야기는 달랐다.md`를 보면 알겠지만 `![[327135821566fda5a5842942f012e8c8_MD5.jpg]]`나 `![[bc57e2d31c4ec56fcaee47c0ea0d08b1_MD5.jpg]]`처럼 이미지가 파일명으로만 나와 있어.
이걸 `![](🧷Attachments/327135821566fda5a5842942f012e8c8_MD5.jpg)`나 `![](🧷Attachments/bc57e2d31c4ec56fcaee47c0ea0d08b1_MD5.jpg)`처럼 상대경로로 바꿔주도록 코드를 수정해주면 좋겠어. 할 수 있을까?

---

근데 이미지가 꼭 `🧷Attachments/`에 저장되어 있지 않을 수 있어.

---

우리가 만든 `Codes/Convert_Image-Link_Wiki-to-Markdown.py`를 개선하고 싶어.
지금은 wikilink형식의 첨부된 이미지를 마크다운 형식인 `![](Path_Image)`로 바꿔.
여기서 `.claude/skills/Seongjin_Book-Prep/Scripts/pdf_to_md.py`를 참조해 `![Description_Image](Path_Image)`로 바꿀 수 있으면 좋겠어.
Gemini 또는 GPT api를 호출해서 사용할건데, `pdf_to_md.py`와 마찬가지로 `Codes/.env`를 참조할거야.
전체적으로 목적이 이해가 되니?