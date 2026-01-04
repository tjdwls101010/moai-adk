---
name: ppt
description: "Generate PPT slide images from markdown or PDF files using Nano-Banana"
argument-hint: '{source} "{instructions}" - Source folder or file path, and generation instructions'
allowed-tools: Task, Bash
model: inherit
skills: pdf, Seongjin_Nano-Banana
---

# PPT Slide Image Generator Command

**User Interaction Architecture**: This command operates without user interaction. All processing is automatic. User provides feedback only if needed after completion.

**Execution Model**: Commands orchestrate through `Task()` tool. Bash is used only for file listing and Nano-Banana script execution.

**Delegation Pattern**: Sequential workflow with automatic file processing:
- Step 1: Source type determination (folder vs file)
- Step 2: Collect all eligible files (if folder, process all .md/.pdf files automatically)
- Step 3: PPT-Planner agent delegation for JSON generation
- Step 4: Nano-Banana script execution for image generation
- Step 5: PDF merge (combine all slide images into single PDF)

---

## Command Purpose

Generate PPT slide images from markdown or PDF source files through a two-stage process:
1. Analyze source content and create slide outline JSON (via PPT-Planner agent)
2. Generate slide images from JSON prompts (via Generate_Slides.py script)

**Parameters**: Supply via `$ARGUMENTS`
- `{source}`: Folder path (e.g., `TMP/`) or file path (e.g., `TMP/document.md`)
- `{instructions}`: Generation instructions in quotes (e.g., `"easy for beginners"`)

**Example Usage**:
```
/ppt TMP/ "executive summary style"
/ppt TMP/report.md "beginner-friendly"
```

---

## Execution Philosophy: "Source to Slides"

The `/ppt` command transforms source documents into presentation slide images through complete agent delegation.

### Output Format Rules

[HARD] User-Facing Reports: Always use Markdown formatting for all user communication.

User Report Example:

```
PPT Generation Complete

Source Analysis:
- Files Processed: 2
- Total Slides Generated: 24

Generated Artifacts:
1. TMP/report_slides.json (12 slides)
   Images: TMP/report_images/
2. TMP/analysis_slides.json (12 slides)
   Images: TMP/analysis_images/

Status: SUCCESS
```

[HARD] Internal Agent Data: XML tags are reserved for agent-to-agent data transfer only. Never display XML tags to users.

### Tool Usage Discipline [HARD]

This command uses these tools:

- **Task()**: Delegates to PPT-Planner agent for JSON generation
  - WHY: PPT-Planner reads source files and generates structured slide outlines
  - IMPACT: Main command does NOT read source files directly

- **Bash()**: Used ONLY for three purposes:
  1. List files in source folder: `ls "{folder}"`
  2. Execute Nano-Banana script: `uv run python {absolute_script_path} "{json_file}" --output-dir "{output_dir}"`
  3. Merge slide images into PDF: Python inline script with Pillow
  - WHY: File listing, script execution, and PDF generation require shell access
  - IMPACT: Limited to non-file-reading operations
  - NOTE: Use `uv run python` instead of `python` to ensure correct environment and dependencies
  - [HARD] Use absolute paths for script location. Do NOT use environment variables like `$CLAUDE_PROJECT_DIR` as they are not resolved in Bash tool
  - Script path pattern: `{working_directory}/.claude/skills/Seongjin_Nano-Banana/Scripts/Generate_Slides.py`

[HARD] Main command MUST NOT use Read() tool on source files.
- WHY: PPT-Planner agent handles all file reading
- IMPACT: Ensures clean separation of concerns

---

## Associated Agents & Skills

**Core Agent**:

- **Seongjin_Agent_PPT-Planner**: Analyzes source files and generates slide outline JSON
  - Input: source_file_path, output_path, user_instruction
  - Output: JSON file with slide structure and Nano-Banana prompts
  - Skills: pdf (for PDF file processing)

**Skill**:

- **Seongjin_Nano-Banana**: Generates slide images from JSON prompts
  - Script: `.claude/skills/Seongjin_Nano-Banana/Scripts/Generate_Slides.py`
  - Input: JSON file path, output directory
  - Output: PNG images for each slide

---

## Agent Invocation Patterns (CLAUDE.md Compliance)

This command uses agent execution patterns defined in CLAUDE.md.

### Hybrid Parallel-Sequential Workflow

Command implements hybrid workflow optimized for speed and reliability:

Step Flow:
- Step 1: Source Type Determination (Bash ls check)
- Step 2: Collect All Eligible Files (automatic for folders)
- Step 3: JSON Generation - PARALLEL (all PPT-Planner subagents run simultaneously)
- Step 4: Image Generation - SEQUENTIAL (one file at a time, Gemini API rate limit)
- Step 5: PDF Merge (after each file's images complete)

WHY: Hybrid approach maximizes speed while respecting API limits
- Steps 1-2: Sequential (dependency chain)
- Step 3: PARALLEL - PPT-Planner uses Claude, no rate limit concerns
- Steps 4-5: Sequential per file - Gemini API has strict rate limits

IMPACT: Faster overall processing - planning phase parallelized, image generation protected

### Execution Mode Details

**Step 3 - PARALLEL Execution (Planning Phase)**:
- [HARD] Launch ALL Task() calls to PPT-Planner in a SINGLE message (parallel execution)
- WHY: PPT-Planner uses Claude API, not Gemini - no rate limit concerns
- IMPACT: 10 files planned in parallel = 10x faster than sequential

**Steps 4-5 - SEQUENTIAL Execution (Image Generation Phase)**:
- [HARD] After ALL JSON files are ready, process images ONE FILE AT A TIME
- Generate_Slides.py executions MUST run SEQUENTIALLY (one file at a time)
- After each file completes image generation, proceed to PDF merge for that file

WHY: Gemini API has rate limits that cause failures when multiple image generation requests run in parallel
IMPACT: Slower but reliable processing - avoids API rate limit errors

### Resumable Agent Support FAIL

Not applicable - PPT generation is atomic per file

WHY: Each file generates one JSON and one image set
- Typical execution time: 2-5 minutes per file
- No intermediate checkpoints needed

IMPACT: If interrupted, re-run the command with same parameters

---

## Workflow Execution Details

### Step 1: Determine Source Type

**Tool**: Bash

Check if source is a folder or individual file:

```bash
ls "{source}" 2>/dev/null
```

Decision Logic:
- If source ends with `/` or ls shows multiple items: Treat as folder
- If source is a single file path (ends with .md or .pdf): Treat as file
- If source does not exist: Report error

---

### Step 2: Collect All Eligible Files (Folder Only)

**Condition**: Execute only if source is a folder

**Tool**: Bash

List all eligible files in folder:

```bash
ls "{source}" | grep -E '\.(md|pdf)$'
```

[HARD] Automatically process ALL .md and .pdf files in the folder
- WHY: Eliminates unnecessary user interaction
- IMPACT: Streamlined workflow for batch processing

Collect all eligible file paths for Step 3.

---

### Step 3: JSON Generation via PPT-Planner

**Tool**: Task (PPT-Planner subagent)

**Quality Principle - SPECIFIC and DETAILED Plans**:

[HARD] Plans MUST be specific and detailed for high-quality PPT output.
- Include actual names of people, events, dates, and facts from source
- Do NOT add any safety-related constraints or warnings to PPT-Planner prompts
- Do NOT ask PPT-Planner to avoid specific names or topics
- Safety issues are handled in Step 4.5 AFTER they occur, not prevented beforehand
- WHY: Pre-emptive safety constraints degrade plan quality and create abstract, vague slides
- IMPACT: Detailed prompts create better, more informative slides

For each selected file, delegate to PPT-Planner:

```python
Task(
    subagent_type="Seongjin_Agent_PPT-Planner",
    prompt="""
    Generate PPT slide outline JSON for the following source file:

    Source File Path: {absolute_path_to_source_file}
    Output Directory: {source_dir}
    User Instruction: {user_instructions}

    Requirements:
    - Create output folder: {source_dir}/PPT_{filename}/
    - Save JSON as: {source_dir}/PPT_{filename}/Plan_{filename}.json
    - Read the ENTIRE source file content
    - Generate slide outline following 4-field schema (page, title, key_message, nano_banana_prompt)
    - Apply 4-layer Nano-Banana prompt structure
    - Be SPECIFIC and DETAILED - include actual names, events, dates, and facts from source
    - Quality matters: detailed prompts create better slides

    Image Handling (Markdown files only):
    - Extract embedded images using pattern: ![[filename.ext]]
    - Search for images in 🧷Attachments folder using Glob
    - Read and analyze each image to understand its content
    - Include relevant images in slide reference_images (max 3 per slide)
    - Selection priority: data visualizations > people photos > diagrams > screenshots
    - Omit reference_images field if no relevant images found

    Return: Confirmation of JSON file creation with slide count and full path
    """
)
```

**Output Path Convention**:
- Source: `TMP/examples/📰미국의 퇴장.md`
- Output Folder: `TMP/examples/PPT_📰미국의 퇴장/`
- JSON: `TMP/examples/PPT_📰미국의 퇴장/Plan_📰미국의 퇴장.json`

[HARD] Pass ONLY file paths to the subagent. Do NOT read file contents in main command.
- WHY: PPT-Planner agent handles file reading with proper fallback methods
- IMPACT: Ensures complete file reading without truncation

[HARD] Do NOT add safety constraints to PPT-Planner prompts.
- WHY: Safety issues are handled reactively in Step 4.5, not proactively
- IMPACT: Prevents quality degradation from pre-emptive content filtering

---

### Step 4: Image Generation via Nano-Banana

**Tool**: Bash (SEQUENTIAL execution for multiple files)

For each generated JSON file, execute Nano-Banana script from skill.

[HARD] When processing multiple files, execute Bash calls ONE AT A TIME (sequential execution).
- WHY: Gemini API rate limits cause failures when parallel requests exceed quota
- IMPACT: Reliable image generation without API errors
- Process: Complete one file entirely (images + PDF + summary) before starting next file

[HARD] Use absolute path for script location. Environment variables like `$CLAUDE_PROJECT_DIR` are NOT resolved in Bash tool.

[HARD] Special character path handling (emoji, Korean, spaces):
- All paths MUST be wrapped in double quotes
- Execute script by first `cd` to script directory, then run with relative path
- WHY: `uv run python` with absolute script path outside script directory fails to load dependencies (e.g., `dotenv`)
- WHY: Paths with special characters fail without proper quoting
- IMPACT: Ensures dependencies are loaded and paths are parsed correctly

Correct pattern:
```bash
cd "{script_directory}" && uv run python Generate_Slides.py "{json_file}" --output-dir "{ppt_folder}"
```

Example with special characters:
```bash
cd "/Users/seongjin/Documents/⭐성진이의 옵시디언/.claude/skills/Seongjin_Nano-Banana/Scripts" && uv run python Generate_Slides.py "/Users/seongjin/Documents/⭐성진이의 옵시디언/📥Articles&Videos/PPT_📰제목/Plan_📰제목.json" --output-dir "/Users/seongjin/Documents/⭐성진이의 옵시디언/📥Articles&Videos/PPT_📰제목/"
```

Path construction:
- Script directory: `{working_directory}/.claude/skills/Seongjin_Nano-Banana/Scripts`
- Get working directory from the JSON file path or use known project root
- Example: If JSON is at `/Users/seongjin/Documents/⭐vault/TMP/PPT_test/Plan_test.json`
- Script directory is: `/Users/seongjin/Documents/⭐vault/.claude/skills/Seongjin_Nano-Banana/Scripts`

**Output Directory Convention**:
- JSON: `TMP/examples/PPT_📰미국의 퇴장/Plan_📰미국의 퇴장.json`
- Images: `TMP/examples/PPT_📰미국의 퇴장/` (same folder as JSON)

The script:
- Uses Gemini API for image generation
- Creates `slide_001.png`, `slide_002.png`, etc.
- Handles rate limiting with automatic retry
- Parallel execution with ThreadPoolExecutor

[HARD] Ensure .env file with GOOGLE_API_KEY exists at `.claude/skills/Seongjin_Nano-Banana/Scripts/.env`
- WHY: Generate_Slides.py requires API key for Gemini access
- IMPACT: Script will fail without valid API key

---

### Step 4.5: Safety Error Recovery - POST-HOC ONLY (v2.0.0)

**Philosophy**: React, Don't Prevent

[HARD] Safety handling is REACTIVE, not PROACTIVE.
- Do NOT prevent safety issues in Step 3 (planning phase)
- Only handle safety issues AFTER they occur in Step 4 (image generation)
- WHY: Pre-emptive filtering degrades content quality
- IMPACT: High-quality detailed plans + targeted fixes for specific failures

**Condition**: Execute only if Step 4 produced failures with IMAGE_SAFETY reason

**Tool**: Task (PPT-Planner subagent) + Bash

After Generate_Slides.py execution, check for failures:

1. Parse the script output for `FAILURE_REPORT_JSON_START` ... `FAILURE_REPORT_JSON_END` block
2. If failed_slides exist with reason containing "IMAGE_SAFETY" or "SAFETY_FILTER":

Recovery Workflow (for FAILED slides ONLY):

Step 4.5.1: Call PPT-Planner to revise the problematic prompts

```python
Task(
    subagent_type="Seongjin_Agent_PPT-Planner",
    prompt="""
    SAFETY ERROR RECOVERY: Revise prompts for failed slides.

    JSON File Path: {json_file_path}
    Failed Slides: {list of failed slide pages and titles}
    Failure Reason: IMAGE_SAFETY - Gemini API blocked due to sensitive content

    Requirements:
    - Read the existing JSON file
    - For ONLY the failed slides listed above, revise the nano_banana_prompt
    - Remove or rephrase sensitive content (historical figures, political symbols, etc.)
    - Keep the same slide structure and key_message
    - Maintain historical/educational context without triggering safety filters
    - Save the updated JSON to the SAME file path (overwrite)

    Revision Guidelines:
    - Replace specific names with general descriptions (e.g., "historical dictator" instead of specific name)
    - Remove references to symbols, flags, or imagery associated with extremist movements
    - Focus on concepts and patterns rather than specific individuals
    - Use neutral, academic language

    Return: Confirmation of which slides were revised and the updated JSON file path
    """
)
```

Step 4.5.2: Retry image generation for failed slides only

```bash
uv run python "{script_path}" "{json_file}" --output-dir "{output_dir}" --slides {comma_separated_failed_pages}
```

Step 4.5.3: If still failing after retry:
- Log failures to console output
- Continue with PDF merge using available slides
- Do NOT block the entire workflow for individual slide failures

[HARD] Maximum 1 retry attempt per file
- WHY: Prevents infinite loops on truly problematic content
- IMPACT: Workflow continues even if some slides cannot be generated

---

### Step 5: PDF Merge

**Tool**: Bash (Python with Pillow) - Execute immediately after each file's images are generated

After images are generated for a file, merge them into a single PDF file.

[HARD] Execute PDF merge immediately after image generation completes for each file (part of sequential per-file workflow).

```bash
uv run python -c "
from PIL import Image
import os

folder = '{ppt_folder}'
images = []

# Load images in order
for i in range(1, {slide_count}+1):
    img_path = os.path.join(folder, f'slide_{i:03d}.png')
    if os.path.exists(img_path):
        img = Image.open(img_path).convert('RGB')
        images.append(img)

# Save as PDF
output_path = os.path.join(folder, '{filename}.pdf')
images[0].save(output_path, save_all=True, append_images=images[1:], resolution=100.0)
print(f'PDF created: {output_path}')
"
```

**PDF Output Convention**:
- Images: `PPT_📰미국의 퇴장/slide_001.png` ~ `slide_NNN.png`
- PDF: `PPT_📰미국의 퇴장/📰미국의 퇴장.pdf`

[HARD] Use the source filename (without extension) for the PDF filename
- WHY: Consistent naming makes it easy to identify the PDF source
- IMPACT: Users can quickly find the PDF for each source file

---

### Step 6: Results Summary (CLI Output Only)

**Tool**: Direct Markdown output - Execute after each file completes

After each file is processed (images generated + PDF merged), output a summary to the user via CLI.

**Summary Template**:

```markdown
## ✅ {source_filename} - Complete

**Slides Generated**: {slide_count}
**PDF**: `{filename}.pdf`
**Output Folder**: `PPT_{filename}/`

### Slides
| Page | Title |
|:---:|:---|
| 1 | {slide_1_title} |
| 2 | {slide_2_title} |
| ... | ... |
```

[HARD] Do NOT use AskUserQuestion for next steps
- WHY: User will provide feedback if needed; unnecessary prompting interrupts workflow
- IMPACT: Streamlined completion without forced interaction

[HARD] Do NOT save summary to file
- WHY: Users can review PDF and images directly; file summaries are unnecessary
- IMPACT: Cleaner output folder with only essential files

---

## Error Handling

Common Errors and Solutions:

**Source Not Found**:
- Check if path is correct
- Verify file exists using `ls` command

**No Eligible Files**:
- Folder contains no .md or .pdf files
- Suggest adding source files or specifying different path

**JSON Generation Failed**:
- PPT-Planner could not read or parse source file
- Check file encoding and format

**Image Generation Failed**:
- Generate_Slides.py script error
- Common causes: API key missing, rate limit exceeded, network error
- Script has built-in retry logic (10 retries, 30-second delay)

**API Key Missing**:
- Create `.env` file at `.claude/skills/Seongjin_Nano-Banana/Scripts/.env`
- Add: `GOOGLE_API_KEY=your_key_here`

---

## Reference Image Support

The PPT command automatically extracts and includes relevant images from markdown source files.

### How It Works
1. **Image Extraction**: PPT-Planner agent parses markdown for `![[filename.ext]]` patterns
2. **Path Resolution**: Searches `🧷Attachments` folder using Glob to find absolute paths
3. **Content Analysis**: Reads each image to understand what it depicts
4. **Smart Assignment**: Assigns relevant images to slides based on content and section mapping

### Selection Criteria
Images are prioritized by relevance:
- **HIGH**: Charts, data visualizations, diagrams, photos of people mentioned
- **MEDIUM**: Screenshots, infographics, illustrative images
- **LOW**: Decorative images, stock photos (excluded)

### Constraints
- Maximum 3 reference images per slide
- Only applies to markdown files (PDF text-only)
- Supported formats: PNG, JPG, JPEG, GIF, WEBP

### JSON Output Example
```json
{
  "slides": [
    {
      "page": 3,
      "title": "시장 성장 추세",
      "key_message": "...",
      "nano_banana_prompt": "...",
      "reference_images": ["/path/to/🧷Attachments/market_chart.png"]
    }
  ]
}
```

---

## Quick Reference

| Scenario | Command | Expected Outcome |
|----------|---------|------------------|
| Single file | `/ppt TMP/doc.md "summary style"` | 1 JSON + images generated |
| Folder (all files) | `/ppt TMP/ "beginner-friendly"` | All .md/.pdf files processed automatically |
| Korean content | `/ppt TMP/report.md "for beginners"` | Korean text in slides |

**File Types Supported**:
- Markdown (.md): Direct reading
- PDF (.pdf): Text extraction via pdf skill

**Output Files** (all in `PPT_{filename}/` folder):
- `{filename}.pdf`: Combined PDF with all slides
- `Plan_{filename}.json`: Slide outline with prompts
- `slide_001.png` ~ `slide_NNN.png`: Generated slide images

Version: 2.5.0
Last Updated: 2026-01-04
Architecture: Command -> PPT-Planner Agent (PARALLEL, DETAILED, IMAGE-AWARE) -> Seongjin_Nano-Banana (SEQUENTIAL) -> Safety Recovery (POST-HOC) -> PDF Merge -> CLI Summary
Changes (v2.5.0): Added reference image support - PPT-Planner extracts embedded images from markdown, analyzes content, assigns relevant images to slides (max 3 per slide)
Changes (v2.4.0): Fixed special character path handling - use `cd` to script directory + relative path execution; all paths must be quoted for emoji/Korean/spaces support
Changes (v2.3.0): Removed SUMMARY.md file generation - results summary now displayed via CLI only for cleaner output folders
Changes (v2.2.0): Quality-first planning - plans must be SPECIFIC and DETAILED with actual names/events/facts; safety handling is REACTIVE only (post-hoc), not proactive; prevents quality degradation from pre-emptive content filtering
Changes (v2.1.0): Hybrid parallel-sequential workflow - planning phase runs in parallel (10x faster), image generation remains sequential for API rate limit protection
Changes (v2.0.0): Added Safety Error Recovery workflow - automatically revises prompts blocked by IMAGE_SAFETY and retries with --slides parameter
Changes (v1.9.0): Sequential execution for image generation - prevents Gemini API rate limit errors by processing one file at a time
Changes (v1.8.0): Parallel execution for multiple files - Bash calls for image generation and PDF merge now execute sequentially per file
Changes (v1.7.0): Added automatic PDF merge step - all slide images are combined into single PDF file
Changes (v1.5.0): Removed AskUserQuestion from workflow; fixed environment variable issue by requiring absolute paths for Nano-Banana script
Changes (v1.4.0): Integrated with Seongjin_Nano-Banana skill, script path now uses skill directory

---

## EXECUTION DIRECTIVE

[HARD] Execute the command following the "Source to Slides" philosophy described above.

1. Parse $ARGUMENTS to extract source path and instructions
   - First argument: source path (folder or file)
   - Remaining arguments in quotes: user instructions

2. [HARD] Determine if source is folder or file using Bash ls
   - WHY: Different workflow for folder vs file
   - IMPACT: Ensures correct file collection

3. [HARD] If folder, collect all .md and .pdf files automatically
   - WHY: Eliminates unnecessary user interaction
   - IMPACT: Streamlined batch processing

4. [HARD] Launch ALL Task() calls to PPT-Planner in PARALLEL (single message with multiple tool calls)
   - [HARD] For MULTIPLE files: Call ALL Task() tools in ONE message to execute in parallel
   - Pass ONLY: source_file_path, output_path, user_instruction
   - Do NOT read source file content in main command
   - [HARD] Do NOT add safety constraints or warnings to prompts - plans must be SPECIFIC and DETAILED
   - [HARD] Include actual names, events, dates, facts - quality requires detail
   - WHY: PPT-Planner uses Claude API (no rate limit) - parallel execution is 10x faster
   - WHY: Pre-emptive safety constraints degrade plan quality
   - IMPACT: All planning completes simultaneously with high-quality detailed content

5. [HARD] WAIT for ALL JSON files to be ready, THEN execute Generate_Slides.py SEQUENTIALLY for each JSON file
   - [HARD] For MULTIPLE files: Execute ONE file at a time, wait for completion before starting next
   - [HARD] Use `cd` to script directory + relative path execution pattern
   - [HARD] All paths MUST be wrapped in double quotes (handles emoji, Korean, spaces)
   - Correct: `cd "{script_dir}" && uv run python Generate_Slides.py "{json_file}" --output-dir "{output_dir}"`
   - Wrong: `uv run python "/absolute/path/to/Generate_Slides.py" ...` (dependencies not loaded)
   - Wrong: `cd /path/with spaces/...` (unquoted path with special characters fails)
   - WHY: `uv run` needs to be in script directory to load pyproject.toml dependencies
   - WHY: Paths with special characters require proper quoting
   - NOTE: Use `uv run python` to ensure correct Python environment and dependencies
   - IMPACT: Reliable image generation without dependency or path parsing errors

5.5 [HARD] POST-HOC Safety Error Recovery (Step 4.5) - REACT, DON'T PREVENT
   - This is REACTIVE handling - only for slides that actually failed
   - Parse script output for FAILURE_REPORT_JSON_START block
   - If IMAGE_SAFETY or SAFETY_FILTER errors detected:
     a. Call PPT-Planner to revise ONLY the failed slide prompts (not entire plan)
     b. Retry with `--slides {failed_pages}` parameter
     c. If still failing, log to console and continue
   - Maximum 1 retry attempt per file
   - WHY: React to actual failures, don't pre-emptively degrade quality
   - IMPACT: High-quality plans + targeted fixes for specific failures

6. [HARD] After EACH file's image generation completes, merge images into PDF
   - Execute PDF merge immediately after image generation for each file
   - Use Bash with inline Python script using Pillow
   - Load images in order (slide_001.png, slide_002.png, ...)
   - Save as `{filename}.pdf` in the same folder
   - WHY: PDF provides convenient single-file format for sharing and viewing
   - IMPACT: Users get ready-to-use presentation file

7. [HARD] After EACH file's PDF merge completes, display results summary via CLI
   - Output summary directly to user (no file creation)
   - Include: source filename, slide count, PDF path, output folder, slide list with titles
   - Do NOT use AskUserQuestion
   - Do NOT save summary to file
   - WHY: Per-file completion feedback keeps user informed of progress
   - IMPACT: User sees progress as each file completes with cleaner output folders

8. [HARD] Proceed with execution immediately - implement all steps in sequence
   - WHY: Immediate execution ensures command completion
   - IMPACT: Describing work without executing blocks productivity
