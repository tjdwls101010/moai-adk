---
name: Book-Architect
description: "Orchestrate the full workflow of restructuring a PDF book into analysis-ready markdown documents"
argument-hint: '{source} "{instructions}" - PDF file path and optional restructuring instructions'
allowed-tools: Task, Bash, Read, Skill
model: inherit
---

# Book Architect Command

**User Interaction Architecture**: This command operates without user interaction. All processing is automatic. User provides feedback only if needed after completion.

**Execution Model**: Commands orchestrate through `Task()` tool. Bash is used for file verification, directory listing, and markdown file discovery. Read is used ONLY for toc.json (structure analysis). Skill invokes Seongjin_Book-Prep for PDF preparation.

**Delegation Pattern**: Two-phase workflow with parallel agent execution:
- Phase 1: PDF Preparation (Skill: Seongjin_Book-Prep)
- Phase 2: Content Restructuring (Agent: Seongjin_Agent_Book-Architect, PARALLEL for all chapters)

---

## Command Purpose

Orchestrate the full workflow of restructuring a PDF book into analysis-ready markdown documents through complete agent delegation:
1. Prepare PDF using Book-Prep skill (TOC analysis, PDF splitting, markdown conversion)
2. Restructure each chapter markdown into logically organized prose documents (via Book-Architect agent)

**Parameters**: Supply via `$ARGUMENTS`
- `{source}`: PDF file path (e.g., `TMP/Value.pdf`)
- `{instructions}`: Restructuring instructions in quotes (optional, e.g., `"Korean informal style"`)

**Example Usage**:
```
/Book-Architect TMP/Value.pdf
/Book-Architect TMP/Value.pdf "Korean informal style"
```

---

## Execution Philosophy: "PDF to Restructured Knowledge"

The `/Book-Architect` command transforms PDF books into well-organized prose documents through complete agent delegation.

### Core Principles

1. **Orchestrator Only**: Main command does NOT read markdown content (except toc.json for planning)
2. **Skill-First PDF Processing**: Use Seongjin_Book-Prep skill for all PDF operations
3. **Parallel Agent Execution**: All chapter restructuring runs simultaneously
4. **Zero Information Loss**: Agents preserve all original content while improving structure

### Output Format Rules

[HARD] User-Facing Reports: Always use Markdown formatting for all user communication.

User Report Example:

```
Book Architecture Complete

Source: TMP/Value.pdf
Chapters Processed: 15

Generated Artifacts:
1. TMP/Value/Reconstructed_5. Introduction.md
2. TMP/Value/Reconstructed_6. Part I.md
...

Status: SUCCESS
```

[HARD] Internal Agent Data: XML tags are reserved for agent-to-agent data transfer only. Never display XML tags to users.

### Tool Usage Discipline [HARD]

This command uses these tools:

- **Skill()**: Invokes Seongjin_Book-Prep skill for PDF preparation
  - WHY: Book-Prep handles TOC analysis, PDF splitting, and markdown conversion
  - IMPACT: All PDF processing delegated to specialized skill

- **Bash()**: Used for three purposes:
  1. Verify source PDF exists: `ls "{source}"`
  2. Find generated markdown files: `find "{book_folder}" -name "*.md" -type f`
  3. Exclude backup files from processing
  - WHY: File verification and discovery require shell access
  - IMPACT: Limited to non-content-reading operations

- **Read()**: Used ONLY for toc.json
  - WHY: TOC structure determines split level and chapter organization
  - IMPACT: This is the ONLY file main command reads directly

- **Task()**: Delegates to Book-Architect agent for content restructuring
  - WHY: Agent reads source markdown and generates restructured prose
  - IMPACT: Main command does NOT read markdown content directly

[HARD] Main command MUST NOT use Read() tool on markdown source files.
- WHY: Book-Architect agent handles all markdown file reading
- IMPACT: Ensures complete file processing without truncation

---

## Associated Agents & Skills

**Core Skill**:

- **Seongjin_Book-Prep**: Prepares PDF books for LLM analysis
  - Input: PDF file path
  - Output: Directory with split PDFs, markdown files, and toc.json
  - Capabilities: TOC analysis, level-based splitting, markdown conversion with AI image descriptions

**Core Agent**:

- **Seongjin_Agent_Book-Architect**: Restructures markdown content into organized prose
  - Input: source_file_path, output_file_path, user_instructions
  - Output: Restructured markdown file with logical organization and zero information loss
  - Capabilities: Information architecture, prose writing, structural reorganization

---

## Agent Invocation Patterns (CLAUDE.md Compliance)

This command uses agent execution patterns defined in CLAUDE.md.

### Sequential Phase-Based Chaining PASS

Command implements sequential chaining through 2 main phases:

Phase Flow:
- Phase 1: PDF Preparation (Seongjin_Book-Prep skill)
- Phase 2: Content Restructuring (Seongjin_Agent_Book-Architect, PARALLEL)

Each phase receives outputs from previous phases as context.

WHY: Sequential execution ensures PDF is fully prepared before restructuring begins
- Phase 2 requires markdown files generated by Phase 1
- TOC analysis determines split level before PDF splitting
- Markdown files must exist before agent restructuring

IMPACT: Skipping phases would attempt restructuring on non-existent files

### Parallel Execution PASS

Command executes multiple agents simultaneously in Phase 2:

- All Book-Architect subagent invocations run in parallel
- Each chapter processed independently
- No dependencies between chapter restructuring tasks

WHY: Chapter restructuring is independent per file
IMPACT: 15 chapters processed in parallel = 15x faster than sequential

### Resumable Agent Support FAIL

Not applicable - restructuring is atomic per file

WHY: Each chapter generates one output document
- Typical execution time: 1-5 minutes per chapter depending on content length
- PDF preparation is sequential and typically completes in 5-10 minutes

IMPACT: If interrupted, re-run the command with same parameters

---

## Workflow Execution Details

### Phase 1: PDF Preparation

**Goal**: Prepare PDF book for analysis using Book-Prep skill

#### Step 1.1: Verify Source PDF

**Tool**: Bash

Verify the source PDF file exists:

```bash
ls "{source}" 2>/dev/null
```

Decision Logic:
- If file exists: Proceed to Step 1.2
- If file not found: Report error and exit

#### Step 1.2: Invoke Book-Prep Skill

**Tool**: Skill

Invoke the Seongjin_Book-Prep skill to prepare the PDF:

The skill performs:
1. TOC Analysis: Generate toc.json with chapter structure
2. Level Selection: Determine optimal split level based on TOC
3. PDF Splitting: Split PDF by chapters at selected level
4. Markdown Conversion: Convert each chapter PDF to markdown

Expected output structure:
```
TMP/Value/
  toc.json
  5. Introduction.pdf
  5. Introduction.md
  image-cache_5. Introduction.json
  6. Part I.pdf
  6. Part I.md
  image-cache_6. Part I.json
  images/
  ...
```

#### Step 1.3: Read TOC for Structure Analysis

**Tool**: Read

Read toc.json to understand the book structure:

```bash
# Expected location: {book_folder}/toc.json
# Example: TMP/Value/toc.json
```

Extract from toc.json:
- Total chapter count
- Chapter names and structure
- Split level used

[HARD] This is the ONLY file the main command should read directly.
- WHY: TOC provides metadata needed for orchestration
- IMPACT: Reading markdown content should be delegated to agents

---

### Phase 2: Content Restructuring

**Goal**: Restructure each markdown file into organized prose via parallel agent execution

#### Step 2.1: Collect Markdown File Paths

**Tool**: Bash

Find all generated markdown files:

```bash
find "{book_folder}" -maxdepth 1 -name "*.md" -type f | grep -v ".md.backup" | grep -v "Reconstructed_"
```

Filter rules:
- Include: All .md files in book folder (excluding backups and reconstructed files)
- Exclude: .md.backup files (created by pdf_to_md.py)
- Exclude: Reconstructed_*.md files (already processed)

Store all eligible file paths for parallel processing.

#### Step 2.2: Determine Output Paths

For each markdown file, calculate output path:

- Source file: `{book_folder}/{chapter_name}.md`
- Output file: `{book_folder}/Reconstructed_{chapter_name}.md`

**Output Path Convention Examples**:
- Source: `TMP/Value/5. Introduction.md`
- Output: `TMP/Value/Reconstructed_5. Introduction.md`

- Source: `TMP/Value/6. Part I – The Rise of the Market Society.md`
- Output: `TMP/Value/Reconstructed_6. Part I – The Rise of the Market Society.md`

#### Step 2.3: Parallel Agent Delegation

**Tool**: Task (Book-Architect subagent)

For each markdown file, delegate to Book-Architect agent:

```python
Task(
    subagent_type="Seongjin_Agent_Book-Architect",
    prompt="""
    Restructure the following source file into a well-organized prose document.

    Input File Path: {absolute_path_to_source_file}
    Output File Path: {absolute_path_to_output_file}
    User Instructions: {user_instructions or "None provided"}

    Requirements:
    - Read the ENTIRE source file content
    - Analyze chapter structure and hierarchy
    - Restructure into logical, flowing prose with zero information loss
    - Apply prose-centric writing style (avoid bullet lists)
    - Preserve all examples, statistics, and specific details
    - Follow the formatting rules in the agent definition
    - Save the restructured content to the output file path
    - Use update_todo_list tool to track progress

    Return: Confirmation of output file creation with word count comparison
    """
)
```

[HARD] Pass ONLY file paths to the subagent. Do NOT read file contents in main command.
- WHY: Book-Architect agent handles file reading and content processing
- IMPACT: Ensures complete file processing without truncation

[HARD] Launch ALL Task() calls in a SINGLE message for parallel execution
- WHY: No rate limit concerns for Claude-based processing
- IMPACT: All chapters processed simultaneously for maximum speed

---

### Phase 3: Results Summary

**Tool**: Direct Markdown output

After all chapters are processed, output a summary to the user via CLI.

**Summary Template**:

```markdown
## Book Architecture Complete

**Source PDF**: {source_pdf_path}
**Chapters Processed**: {chapter_count}

### Generated Documents

| Chapter | Source | Reconstructed |
|:--------|:-------|:--------------|
| {chapter_1_name} | {source_1} | {output_1} |
| {chapter_2_name} | {source_2} | {output_2} |
| ... | ... | ... |

**Status**: SUCCESS
```

[HARD] Do NOT use AskUserQuestion for next steps
- WHY: User will provide feedback if needed; unnecessary prompting interrupts workflow
- IMPACT: Streamlined completion without forced interaction

---

## Error Handling

Common Errors and Solutions:

**Source PDF Not Found**:
- Check if path is correct
- Verify file exists using `ls` command
- Ensure path uses absolute or correct relative format

**No TOC in PDF**:
- PDF must have embedded table of contents
- Manual TOC creation required in Adobe Acrobat
- Skill will report "No TOC found" error

**Markdown Conversion Failed**:
- Check API keys in TMP/PDF_to_MD/.env
- Verify network connection for AI image descriptions
- Check TMP/PDF_to_MD/venv is properly configured

**Agent Restructuring Failed**:
- Check if markdown file is readable
- Verify file encoding (UTF-8 expected)
- Check available disk space for output files

**Virtual Environment Issues**:
- Recreate venv: `rm -rf venv && python3 -m venv venv`
- Reinstall requirements: `./venv/bin/pip install -r requirements.txt`

---

## Quick Reference

| Scenario | Command | Expected Outcome |
|----------|---------|------------------|
| Full book processing | `/Book-Architect TMP/Value.pdf` | All chapters prepared and restructured |
| With Korean instructions | `/Book-Architect TMP/Book.pdf "Korean informal style"` | Restructured in Korean informal style |
| With custom style | `/Book-Architect TMP/Book.pdf "academic formal style"` | Restructured with academic tone |

**Output Structure**:
```
{book_name}/
  toc.json
  {chapter}.pdf (split PDF)
  {chapter}.md (original markdown)
  image-cache_{chapter}.json (image cache)
  Reconstructed_{chapter}.md (restructured output)
  images/ (shared image folder)
  ...
```

Version: 1.1.0
Last Updated: 2026-01-01
Architecture: Command -> Skill (Book-Prep) -> Agent (Book-Architect, PARALLEL) -> Results Summary

---

## EXECUTION DIRECTIVE

[HARD] Execute the command following the "PDF to Restructured Knowledge" philosophy described above.

1. Parse $ARGUMENTS to extract source PDF path and optional instructions
   - First argument: PDF file path (e.g., TMP/Value.pdf)
   - Remaining arguments in quotes: user instructions (optional)

2. [HARD] Verify source PDF exists using Bash ls
   - WHY: Cannot process non-existent files
   - IMPACT: Early failure detection saves time

3. [HARD] Invoke Seongjin_Book-Prep skill for PDF preparation
   - WHY: Skill handles TOC analysis, splitting, and markdown conversion
   - IMPACT: All PDF processing delegated to specialized skill
   - Wait for skill completion before proceeding

4. [HARD] Read toc.json to understand book structure
   - WHY: Needed for progress tracking and result reporting
   - IMPACT: This is the ONLY file command reads directly

5. [HARD] Collect all markdown file paths using Bash find
   - Exclude .md.backup files
   - Use absolute paths for all file references

6. [HARD] Calculate output paths for each markdown file
   - Source: `{folder}/{chapter}.md`
   - Output: `{folder}/Reconstructed_{chapter}.md`

7. [HARD] Launch ALL Task() calls to Seongjin_Agent_Book-Architect in PARALLEL (single message with multiple tool calls)
   - [HARD] For MULTIPLE files: Call ALL Task() tools in ONE message to execute in parallel
   - Pass ONLY: input_file_path, output_file_path, user_instructions
   - Do NOT read markdown content in main command
   - WHY: Parallel execution is significantly faster
   - IMPACT: All restructuring completes simultaneously

8. [HARD] After ALL chapters are processed, display results summary via CLI
   - Output summary directly to user (no file creation)
   - Include: source PDF, chapters processed, source-to-output mapping
   - Do NOT use AskUserQuestion
   - WHY: Completion feedback informs user of results
   - IMPACT: User sees all results at once

9. [HARD] Proceed with execution immediately - implement all steps in sequence
   - WHY: Immediate execution ensures command completion
   - IMPACT: Describing work without executing blocks productivity
