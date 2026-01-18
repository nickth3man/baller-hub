import os
import sys
import time
import yaml
import re
import concurrent.futures
from dataclasses import dataclass
from typing import Optional

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class ProcessResult:
    filename: str
    success: bool
    error: Optional[str] = None
    changes_made: bool = False


def validate_file(filepath: str) -> tuple[bool, Optional[str]]:
    """Validate that the file has correct OpenCode format."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, f"Cannot read file: {e}"

    # Check frontmatter exists
    if not content.startswith("---"):
        return False, "File doesn't start with ---"

    # Parse frontmatter
    match = re.match(
        r"^---[\s\n]*(.*?)[\s\n]*---(?:[\s\n]+|$)(.*)$", content, re.DOTALL
    )
    if not match:
        return False, "Cannot parse frontmatter"

    fm_text = match.group(1)
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        return False, f"YAML parse error: {e}"

    if not isinstance(fm, dict):
        return False, "Frontmatter is not a dictionary"

    # Validate required fields
    if "description" not in fm:
        return False, "Missing 'description' field"
    if "mode" not in fm:
        return False, "Missing 'mode' field"
    if "tools" not in fm:
        return False, "Missing 'tools' field"

    if not isinstance(fm["description"], str):
        return False, "'description' must be a string"

    if fm["mode"] not in ["primary", "subagent", "all"]:
        return False, f"Invalid mode: {fm['mode']} (must be primary, subagent, or all)"

    if not isinstance(fm["tools"], dict):
        return False, "'tools' must be a dictionary"

    required_tools = ["write", "edit", "bash"]
    for tool in required_tools:
        if tool not in fm["tools"]:
            return False, f"Missing tool: {tool}"
        if not isinstance(fm["tools"][tool], bool):
            return False, f"Tool '{tool}' must be boolean"

    # Check body exists (has content after frontmatter)
    body = match.group(2).strip()
    if not body:
        return False, "Empty body (no agent prompt)"

    return True, None


def process_file(filepath: str) -> ProcessResult:
    """Process a single agent file."""
    filename = os.path.basename(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return ProcessResult(filename=filename, success=False, error=f"Read error: {e}")

    # Split frontmatter and body
    match = re.match(
        r"^---[\s\n]*(.*?)[\s\n]*---(?:[\s\n]+|$)(.*)$", content, re.DOTALL
    )

    if not match:
        return ProcessResult(
            filename=filename, success=False, error="No frontmatter found"
        )

    fm_text = match.group(1)
    body = match.group(2).lstrip("\n")

    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        return ProcessResult(
            filename=filename, success=False, error=f"YAML parse error: {exc}"
        )

    if not isinstance(fm, dict):
        return ProcessResult(
            filename=filename, success=False, error="Frontmatter is not a dict"
        )

    # Check if already in correct format (no changes needed)
    already_correct = (
        "name" not in fm
        and fm.get("mode") == "subagent"
        and isinstance(fm.get("tools"), dict)
        and all(
            fm.get("tools", {}).get(key) is False for key in ["write", "edit", "bash"]
        )
    )

    # 1. Remove 'name' field
    if "name" in fm:
        del fm["name"]

    # 2. Set 'mode' to 'subagent'
    fm["mode"] = "subagent"

    # 3. Handle 'tools' formatting
    if "tools" not in fm:
        fm["tools"] = {}

    if isinstance(fm["tools"], (list, str)):
        fm["tools"] = {"write": False, "edit": False, "bash": False}
    elif isinstance(fm["tools"], dict):
        for tool_key in ["write", "edit", "bash"]:
            if tool_key not in fm["tools"]:
                fm["tools"][tool_key] = False

    # 4. Remove artifacts like "@code-reviewer.md (4-5)" from body
    body = re.sub(r"^@.*\.md\s*\(\d+-\d+\)\s*$", "", body, flags=re.MULTILINE)
    body = body.lstrip("\n")

    # Maintain order: description, mode, then others
    ordered_fm = {}
    if "description" in fm:
        ordered_fm["description"] = fm["description"]
    ordered_fm["mode"] = "subagent"

    for k, v in fm.items():
        if k not in ["description", "mode"]:
            ordered_fm[k] = v

    # Write back
    new_fm_text = yaml.dump(
        ordered_fm,
        sort_keys=False,
        allow_unicode=True,
        width=1000,
        default_flow_style=False,
    )

    new_content = f"---\n{new_fm_text}---\n\n{body}"

    try:
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
    except Exception as e:
        return ProcessResult(
            filename=filename, success=False, error=f"Write error: {e}"
        )

    # Validate the written file
    valid, error = validate_file(filepath)
    if not valid:
        return ProcessResult(
            filename=filename,
            success=False,
            error=f"Validation failed after write: {error}",
        )

    return ProcessResult(
        filename=filename, success=True, changes_made=not already_correct
    )


def process_file_wrapper(args: tuple) -> ProcessResult:
    """Wrapper for multiprocessing."""
    filepath, _ = args
    return process_file(filepath)


def main():
    """Main entry point with parallel processing."""
    start_time = time.time()

    # Check for command line arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    dry_run = "--dry-run" in args or "-d" in args
    verbose = "--verbose" in args or "-v" in args
    workers = 4  # Default parallel workers

    # Parse worker count if specified
    for arg in args:
        if arg.startswith("--workers="):
            try:
                workers = int(arg.split("=")[1])
            except ValueError:
                print(f"Invalid worker count: {arg}")
                return

    if not os.path.exists(AGENT_DIR):
        print(f"Directory not found: {AGENT_DIR}")
        return

    files = [f for f in os.listdir(AGENT_DIR) if f.endswith(".md")]
    print(f"Found {len(files)} agent files.")

    if dry_run:
        print("DRY RUN MODE - No changes will be made")
        # Validate all files without modifying
        valid_count = 0
        invalid_count = 0
        for filename in files:
            filepath = os.path.join(AGENT_DIR, filename)
            valid, error = validate_file(filepath)
            if valid:
                valid_count += 1
                if verbose:
                    print(f"  ✓ {filename}")
            else:
                invalid_count += 1
                print(f"  ✗ {filename}: {error}")

        print(f"\nValidation Results: {valid_count} valid, {invalid_count} invalid")
        return

    # Process files in parallel
    print(f"Processing {len(files)} files with {workers} workers...")

    file_paths = [(os.path.join(AGENT_DIR, f), f) for f in files]

    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        # Use imap for streaming results
        for result in executor.map(process_file_wrapper, file_paths):
            results.append(result)
            if result.success:
                if result.changes_made:
                    print(f"  Updated {result.filename}")
                elif verbose:
                    print(f"  ✓ {result.filename} (no changes needed)")
            else:
                print(f"  ✗ {result.filename}: {result.error}")

    # Summary statistics
    end_time = time.time()
    duration = end_time - start_time

    total = len(results)
    successful = sum(1 for r in results if r.success)
    failed = total - successful
    changed = sum(1 for r in results if r.success and r.changes_made)
    skipped = successful - changed

    # Error breakdown
    error_types = {}
    for r in results:
        if not r.success and r.error:
            error_type = r.error.split(":")[0] if ":" in r.error else r.error
            error_types[error_type] = error_types.get(error_type, 0) + 1

    # Print comprehensive summary
    print(f"\n{'=' * 60}")
    print(f"PROCESSING COMPLETE")
    print(f"{'=' * 60}")
    print(f"\n📊 Summary:")
    print(f"   Total files processed: {total}")
    print(f"   ✓ Successful:          {successful}")
    print(f"   ✗ Failed:              {failed}")
    print(f"   → Changed:             {changed}")
    print(f"   → Already valid:       {skipped}")
    print(f"\n⏱️  Timing:")
    print(f"   Duration:              {duration:.2f} seconds")
    print(f"   Files/second:          {total / duration:.1f}")
    print(f"   Average/file:          {(duration / total) * 1000:.1f} ms")

    if failed > 0:
        print(f"\n❌ Error Breakdown:")
        for error_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f"   {error_type}: {count}")

        print(f"\n❌ Failed Files:")
        for r in results:
            if not r.success:
                print(f"   - {r.filename}: {r.error}")
    else:
        print(f"\n✅ All files processed successfully!")

    # Show changed files summary if not verbose
    if not verbose and changed > 0:
        print(f"\n📝 Updated Files ({changed}):")
        for r in results:
            if r.success and r.changes_made:
                print(f"   - {r.filename}")

    if changed > 0:
        print(f"\n💡 Tip: Run with --verbose to see all files")
    if failed > 0:
        print(f"\n💡 Tip: Fix errors and re-run")
    else:
        print(f"\n💡 Tip: Run with --dry-run to validate without changes")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
