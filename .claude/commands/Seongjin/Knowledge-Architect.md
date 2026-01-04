---
name: Knowledge-Architect
description: "Restructure text-based learning materials into logically organized prose documents with zero information loss"
argument-hint: '{source} "{instructions}" - Source folder or file path, and restructuring instructions'
allowed-tools: Task, Bash
model: inherit
---

# Knowledge Architect Command

**User Interaction Architecture**: This command operates without user interaction. All processing is automatic. User provides feedback only if needed after completion.

**Execution Model**: Commands orchestrate through `Task()` tool. Bash is used only for file listing and directory creation.

**Delegation Pattern**: Parallel workflow with automatic file processing:
- Step 1: Source type determination (folder vs file)
- Step 2: Collect all eligible markdown files (if folder, process all .md files automatically)
- Step 3: Knowledge-Architect agent delegation for restructuring (PARALLEL for multiple files)
- Step 4: Report results

---

## Command Purpose

Restructure text-based learning materials into logically organized, well-structured prose documents through agent delegation:
1. Analyze source content structure and information architecture
2. Reorganize into logical, readable prose with zero information loss (via Knowledge-Architect agent)

**Parameters**: Supply via `$ARGUMENTS`
- `{source}`: Folder path (e.g., `TMP/examples2`) or file path (e.g., `TMP/examples2/0.intro.md`)
- `{instructions}`: Restructuring instructions in quotes (optional, e.g., `"focus on main concepts"`)

**Example Usage**:
```
/Knowledge-Architect TMP/examples2
/Knowledge-Architect TMP/examples2/0.intro.md "emphasize key takeaways"
/Knowledge-Architect TMP/notes/ "academic style"
```

---

## Execution Philosophy: "Information Architecture with Zero Loss"

The `/Knowledge-Architect` command transforms scattered learning materials into well-organized prose documents through complete agent delegation.

### Core Principles

1. **Absolute Source Fidelity**: Every piece of information from the original must be preserved
2. **Prose-Centric Writing**: All content flows as natural, readable prose (not bullet lists)
3. **Logical Structure**: Information reorganized for optimal comprehension
4. **Zero Summarization**: No information compression or loss

### Output Format Rules

[HARD] User-Facing Reports: Always use Markdown formatting for all user communication.

User Report Example:

```
Knowledge Architecture Complete

Source Analysis:
- Files Processed: 2
- Output Documents: 2

Generated Artifacts:
1. Input: TMP/examples2/0.intro.md
   Output: TMP/examples2/Reconstruct_0.intro/Reconstruct_0.intro.md

2. Input: TMP/examples2/1.chapter.md
   Output: TMP/examples2/Reconstruct_1.chapter/Reconstruct_1.chapter.md

Status: SUCCESS
```

[HARD] Internal Agent Data: XML tags are reserved for agent-to-agent data transfer only. Never display XML tags to users.

### Tool Usage Discipline [HARD]

This command uses these tools:

- **Task()**: Delegates to Knowledge-Architect agent for content restructuring
  - WHY: Knowledge-Architect reads source files and generates restructured prose
  - IMPACT: Main command does NOT read source file contents directly

- **Bash()**: Used ONLY for two purposes:
  1. List files in source folder: `ls "{folder}"`
  2. Create output directories: `mkdir -p "{output_folder}"`
  - WHY: File listing and directory creation require shell access
  - IMPACT: Limited to non-content-reading operations

[HARD] Main command MUST NOT use Read() tool on source files.
- WHY: Knowledge-Architect agent handles all file reading
- IMPACT: Ensures clean separation of concerns

---

## Associated Agents

**Core Agent**:

- **Seongjin_Agent_Knowledge-Architect**: Analyzes source files and generates restructured prose documents
  - Input: source_file_path, output_file_path, user_instructions
  - Output: Restructured markdown file with logical organization and zero information loss
  - Capabilities: Information architecture, prose writing, structural reorganization

---

## Agent Invocation Patterns (CLAUDE.md Compliance)

This command uses agent execution patterns defined in CLAUDE.md.

### Parallel Execution Workflow

Command implements parallel workflow for maximum efficiency:

Step Flow:
- Step 1: Source Type Determination (Bash ls check)
- Step 2: Collect All Eligible Files (automatic for folders)
- Step 3: Content Restructuring - PARALLEL (all Knowledge-Architect subagents run simultaneously)
- Step 4: Report Results

WHY: Parallel processing maximizes throughput
- Steps 1-2: Sequential (dependency chain)
- Step 3: PARALLEL - All Task() calls execute simultaneously

IMPACT: 10 files processed in parallel = 10x faster than sequential

### Execution Mode Details

**Step 3 - PARALLEL Execution (Restructuring Phase)**:
- [HARD] Launch ALL Task() calls to Knowledge-Architect in a SINGLE message (parallel execution)
- WHY: Claude-based processing has no rate limit concerns
- IMPACT: Multiple files restructured simultaneously

### Resumable Agent Support FAIL

Not applicable - restructuring is atomic per file

WHY: Each file generates one output document
- Typical execution time: 1-3 minutes per file depending on content length
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
- If source ends with `/` or ls shows directory contents: Treat as folder
- If source is a single file path (ends with .md): Treat as file
- If source does not exist: Report error

---

### Step 2: Collect All Eligible Files (Folder Only)

**Condition**: Execute only if source is a folder

**Tool**: Bash

List all eligible files in folder:

```bash
ls "{source}" | grep -E '\.md$'
```

[HARD] Automatically process ALL .md files in the folder
- WHY: Eliminates unnecessary user interaction
- IMPACT: Streamlined workflow for batch processing

Collect all eligible file paths for Step 3.

---

### Step 3: Content Restructuring via Knowledge-Architect

**Tool**: Task (Knowledge-Architect subagent)

For each file, determine output paths:
- Source file: `{source_folder}/{filename}.md`
- Output folder: `{source_folder}/Reconstruct_{filename_without_ext}/`
- Output file: `{source_folder}/Reconstruct_{filename_without_ext}/Reconstruct_{filename_without_ext}.md`

**Output Path Convention Examples**:
- Source: `TMP/examples2/0.서론.md`
- Output Folder: `TMP/examples2/Reconstruct_0.서론/`
- Output File: `TMP/examples2/Reconstruct_0.서론/Reconstruct_0.서론.md`

- Source: `TMP/examples2/1.운명적 동맹.md`
- Output Folder: `TMP/examples2/Reconstruct_1.운명적 동맹/`
- Output File: `TMP/examples2/Reconstruct_1.운명적 동맹/Reconstruct_1.운명적 동맹.md`

For each file, delegate to Knowledge-Architect:

```python
Task(
    subagent_type="Seongjin_Agent_Knowledge-Architect",
    prompt="""
    Restructure the following source file into a well-organized prose document:

    Input File Path: {absolute_path_to_source_file}
    Output File Path: {absolute_path_to_output_file}
    User Instructions: {user_instructions or "None provided"}

    Requirements:
    - Create output directory if it does not exist
    - Read the ENTIRE source file content
    - Restructure into logical, flowing prose
    - Preserve ALL information from the source (zero summarization)
    - Apply prose-centric writing style (avoid bullet lists)
    - Follow the formatting rules in the agent definition
    - Save the restructured content to the output file path

    Return: Confirmation of output file creation with word count comparison (original vs restructured)
    """
)
```

[HARD] Pass ONLY file paths to the subagent. Do NOT read file contents in main command.
- WHY: Knowledge-Architect agent handles file reading and content processing
- IMPACT: Ensures complete file processing without truncation

[HARD] Launch ALL Task() calls in a SINGLE message for parallel execution
- WHY: No rate limit concerns for Claude-based processing
- IMPACT: All files processed simultaneously for maximum speed

---

### Step 4: Results Summary (CLI Output Only)

**Tool**: Direct Markdown output

After all files are processed, output a summary to the user via CLI.

**Summary Template**:

```markdown
## Knowledge Architecture Complete

**Files Processed**: {file_count}

### Generated Documents

| Source | Output |
|:-------|:-------|
| {source_1} | {output_1} |
| {source_2} | {output_2} |
| ... | ... |

**Status**: SUCCESS
```

[HARD] Do NOT use AskUserQuestion for next steps
- WHY: User will provide feedback if needed; unnecessary prompting interrupts workflow
- IMPACT: Streamlined completion without forced interaction

---

## Error Handling

Common Errors and Solutions:

**Source Not Found**:
- Check if path is correct
- Verify file or folder exists using `ls` command

**No Eligible Files**:
- Folder contains no .md files
- Suggest adding markdown files or specifying different path

**Content Restructuring Failed**:
- Knowledge-Architect could not read or parse source file
- Check file encoding and format

**Output Directory Creation Failed**:
- Permission issues on target directory
- Check write permissions

---

## Quick Reference

| Scenario | Command | Expected Outcome |
|----------|---------|------------------|
| Single file | `/Knowledge-Architect TMP/doc.md` | 1 restructured document generated |
| Single file with instructions | `/Knowledge-Architect TMP/doc.md "academic style"` | 1 restructured document with style applied |
| Folder (all files) | `/Knowledge-Architect TMP/notes/` | All .md files processed in parallel |

**File Types Supported**:
- Markdown (.md): Direct reading and restructuring

**Output Structure**:
- Source: `{folder}/{filename}.md`
- Output: `{folder}/Reconstruct_{filename_without_ext}/Reconstruct_{filename_without_ext}.md`

Version: 1.0.0
Last Updated: 2025-12-30
Architecture: Command -> Knowledge-Architect Agent (PARALLEL) -> Results Summary

---

## EXECUTION DIRECTIVE

[HARD] Execute the command following the "Information Architecture with Zero Loss" philosophy described above.

1. Parse $ARGUMENTS to extract source path and instructions
   - First argument: source path (folder or file)
   - Remaining arguments in quotes: user instructions (optional)

2. [HARD] Determine if source is folder or file using Bash ls
   - WHY: Different workflow for folder vs file
   - IMPACT: Ensures correct file collection

3. [HARD] If folder, collect all .md files automatically
   - WHY: Eliminates unnecessary user interaction
   - IMPACT: Streamlined batch processing

4. [HARD] Calculate output paths for each file
   - For source `{folder}/{filename}.md`:
   - Output folder: `{folder}/Reconstruct_{filename_without_ext}/`
   - Output file: `{folder}/Reconstruct_{filename_without_ext}/Reconstruct_{filename_without_ext}.md`
   - Use absolute paths for all file references

5. [HARD] Launch ALL Task() calls to Seongjin_Agent_Knowledge-Architect in PARALLEL (single message with multiple tool calls)
   - [HARD] For MULTIPLE files: Call ALL Task() tools in ONE message to execute in parallel
   - Pass ONLY: input_file_path, output_file_path, user_instructions
   - Do NOT read source file content in main command
   - WHY: Parallel execution is significantly faster
   - IMPACT: All restructuring completes simultaneously

6. [HARD] After ALL files are processed, display results summary via CLI
   - Output summary directly to user (no file creation)
   - Include: files processed count, source-to-output mapping
   - Do NOT use AskUserQuestion
   - WHY: Completion feedback informs user of results
   - IMPACT: User sees all results at once

7. [HARD] Proceed with execution immediately - implement all steps in sequence
   - WHY: Immediate execution ensures command completion
   - IMPACT: Describing work without executing blocks productivity
