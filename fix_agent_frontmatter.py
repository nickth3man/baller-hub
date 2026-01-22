#!/usr/bin/env python3
"""
Script to fix OpenCode agent files by cleaning their frontmatter.

Keeps only 'description' and 'mode' fields in YAML frontmatter,
removing all other fields to comply with OpenCode format.
"""

import sys
from pathlib import Path

try:
    import frontmatter
except ImportError:
    print("Error: python-frontmatter library not found.")
    print("Install with: pip install python-frontmatter")
    sys.exit(1)


def fix_agent_frontmatter(file_path: Path) -> bool:
    """
    Fix the frontmatter of a single agent file.

    Args:
        file_path: Path to the agent file

    Returns:
        True if file was modified, False if already correct
    """
    try:
        # Load the file with frontmatter
        with open(file_path, encoding='utf-8') as f:
            post = frontmatter.load(f)

        # Get current metadata
        current_metadata = dict(post.metadata)

        # Create new metadata with only description and mode, cleaned
        new_metadata = {}
        if 'description' in current_metadata:
            # Clean the description: strip whitespace and normalize newlines
            desc = current_metadata['description']
            if isinstance(desc, str):
                # Remove trailing whitespace and normalize line breaks
                desc = desc.strip()
                # Remove excessive blank lines
                import re
                desc = re.sub(r'\n\s*\n\s*\n+', '\n\n', desc)
            new_metadata['description'] = desc
        if 'mode' in current_metadata:
            new_metadata['mode'] = current_metadata['mode']

        # Check if metadata needs to be updated
        if current_metadata == new_metadata:
            return False  # No changes needed

        # Update metadata
        post.metadata = new_metadata

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all agent files."""
    agents_dir = Path('.opencode/agents')

    if not agents_dir.exists():
        print(f"Error: {agents_dir} directory not found")
        sys.exit(1)

    # Get all .md files in agents directory
    agent_files = list(agents_dir.glob('*.md'))

    if not agent_files:
        print(f"No .md files found in {agents_dir}")
        sys.exit(1)

    print(f"Found {len(agent_files)} agent files")

    modified_count = 0
    error_count = 0

    for file_path in sorted(agent_files):
        print(f"Processing {file_path.name}...", end=' ')

        try:
            modified = fix_agent_frontmatter(file_path)
            if modified:
                print("MODIFIED")
                modified_count += 1
            else:
                print("OK")
        except Exception as e:
            print(f"ERROR: {e}")
            error_count += 1

    print("""
Summary:""")
    print(f"  Files processed: {len(agent_files)}")
    print(f"  Files modified: {modified_count}")
    print(f"  Errors: {error_count}")

    if error_count == 0:
        print("All files processed successfully!")
    else:
        print(f"Completed with {error_count} errors")
        sys.exit(1)


if __name__ == '__main__':
    main()
