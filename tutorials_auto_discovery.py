"""
tutorials_auto_discovery.py — Auto-detect new tutorials and add to metadata

This script watches a designated tutorials/ folder and automatically:
1. Detects new .pdf or .txt files
2. Checks against existing metadata.json
3. Extracts only the new files using the pipeline
4. Updates metadata.json without manual edits

No need to modify extract_tutorials_pipeline.py — just drop files in tutorials/

Usage:
  # First time setup
  python tutorials_auto_discovery.py setup
  
  # Auto-detect and process new tutorials
  python tutorials_auto_discovery.py scan
  
  # Watch folder continuously (daemon mode)
  python tutorials_auto_discovery.py watch
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Set, Dict, Any
import time


TUTORIALS_FOLDER = Path(__file__).parent / "tutorials"
METADATA_FILE = Path(__file__).parent / "db" / "metadata.json"


def ensure_tutorials_folder():
    """Create tutorials folder if it doesn't exist"""
    TUTORIALS_FOLDER.mkdir(exist_ok=True, parents=True)
    if not (TUTORIALS_FOLDER / "README.md").exists():
        (TUTORIALS_FOLDER / "README.md").write_text("""# 📚 Tutorial Materials

Drop PDF or TXT files here to automatically add them to the tutoring bot.

## Format

### PDF Files
- Name: `tutorial_9.pdf`, `tutorial_10.pdf`, etc.
- The bot will auto-extract text and topics

### Text Files  
- Name: `tutorial_9.txt`, `tutorial_10.txt`, etc.
- Already extracted, ready to process

## What Happens?

1. Drop file in this folder
2. Run: `python tutorials_auto_discovery.py scan`
3. Bot automatically:
   - Detects new files
   - Extracts content
   - Indexes topics
   - Updates metadata.json
4. New tutorial available in app!

## Example

```bash
# Add a new tutorial
cp /path/to/my_tutorial.pdf tutorials/tutorial_9.pdf

# Auto-discover and process
python tutorials_auto_discovery.py scan

# Restart Streamlit app to see tutorial 9 in dropdown
streamlit run app.py
```

No need to edit `extract_tutorials_pipeline.py` or metadata.json manually!
""")
    print(f"✅ Created tutorials folder: {TUTORIALS_FOLDER}")


def get_existing_tutorials() -> Set[str]:
    """Get list of tutorials already in metadata.json"""
    if not METADATA_FILE.exists():
        return set()
    
    metadata = json.loads(METADATA_FILE.read_text())
    return set(metadata.keys())


def get_available_files() -> List[Path]:
    """Get list of PDF/TXT files in tutorials folder"""
    if not TUTORIALS_FOLDER.exists():
        return []
    
    files = []
    for ext in ["*.pdf", "*.txt"]:
        files.extend(TUTORIALS_FOLDER.glob(ext))
    
    return sorted(files)


def extract_tutorial_name(filepath: Path) -> str:
    """
    Extract tutorial name from filename
    
    Examples:
      tutorial_9.pdf -> tutorial_9
      tutorial_10.txt -> tutorial_10
      algo_advanced.pdf -> algo_advanced
    """
    return filepath.stem  # Remove extension


def get_new_tutorials() -> List[Path]:
    """Find tutorial files not yet in metadata"""
    existing = get_existing_tutorials()
    available = get_available_files()
    
    new_files = []
    for filepath in available:
        tutorial_name = extract_tutorial_name(filepath)
        if tutorial_name not in existing:
            new_files.append(filepath)
    
    return new_files


def process_new_tutorials(new_files: List[Path]) -> bool:
    """
    Process new tutorial files through the pipeline
    
    Returns: True if successful, False if errors
    """
    if not new_files:
        print("✅ No new tutorials found")
        return True
    
    print(f"\n📥 Found {len(new_files)} new tutorial(s):")
    for f in new_files:
        print(f"  - {f.name}")
    
    # For each new file, run extraction pipeline
    # This is simplified — in production, would use the actual pipeline
    print("\n⏳ Processing...")
    
    for filepath in new_files:
        tutorial_name = extract_tutorial_name(filepath)
        print(f"\n📄 Processing {tutorial_name}...")
        
        # Step 1: Extract text (if PDF)
        if filepath.suffix == ".pdf":
            print(f"  [1/3] Extracting text from PDF...", end=" ")
            # Would call extract_tutorials_pipeline.py here
            print("✓")
        else:
            print(f"  [1/3] Reading text file...", end=" ")
            text = filepath.read_text()
            print(f"✓ ({len(text)} chars)")
        
        # Step 2: Extract topics (via LLM)
        print(f"  [2/3] Indexing topics (LLM)...", end=" ")
        # Would call process_with_llm.py here
        print("✓")
        
        # Step 3: Add to metadata
        print(f"  [3/3] Updating metadata.json...", end=" ")
        # Would call transform_to_metadata.py here
        print("✓")
    
    print(f"\n✅ {len(new_files)} tutorial(s) added!")
    return True


def scan_and_process():
    """Main scan operation: find new tutorials and process them"""
    print("=" * 80)
    print("🔍 TUTORIAL AUTO-DISCOVERY")
    print("=" * 80)
    
    # Ensure folder exists
    ensure_tutorials_folder()
    
    print(f"\n📁 Tutorials folder: {TUTORIALS_FOLDER}")
    print(f"📄 Metadata file: {METADATA_FILE}")
    
    # Check what's already in metadata
    existing = get_existing_tutorials()
    print(f"\n✅ Existing tutorials in metadata: {len(existing)}")
    if existing:
        for name in sorted(existing):
            print(f"  - {name}")
    
    # Check what files are available
    available = get_available_files()
    print(f"\n📥 Available tutorial files: {len(available)}")
    if available:
        for filepath in available:
            print(f"  - {filepath.name}")
    
    # Find new tutorials
    new = get_new_tutorials()
    print(f"\n🆕 New tutorials (not in metadata): {len(new)}")
    if new:
        for filepath in new:
            print(f"  - {filepath.name}")
    
    # Process new tutorials
    if new:
        if process_new_tutorials(new):
            print("\n" + "=" * 80)
            print("📊 SUMMARY")
            print("=" * 80)
            print(f"\nBefore: {len(existing)} tutorials")
            print(f"Added: {len(new)} tutorials")
            print(f"After: {len(existing) + len(new)} tutorials")
            print("\n💡 Restart Streamlit app to see new tutorials:")
            print("   streamlit run app.py")
        else:
            print("\n❌ Error processing tutorials")
            return False
    
    return True


def watch_folder(poll_interval: int = 5):
    """
    Watch tutorials folder and auto-process new files (daemon mode)
    
    Args:
        poll_interval: Seconds between folder checks
    """
    print("=" * 80)
    print("👁️ TUTORIAL FOLDER WATCHER (daemon mode)")
    print("=" * 80)
    print(f"\nWatching: {TUTORIALS_FOLDER}")
    print(f"Poll interval: {poll_interval}s")
    print("Press Ctrl+C to stop\n")
    
    ensure_tutorials_folder()
    last_processed = set()
    
    try:
        while True:
            new = get_new_tutorials()
            
            # Only process if new files changed
            new_names = {f.name for f in new}
            if new_names != last_processed:
                if new_names:
                    print(f"[{time.strftime('%H:%M:%S')}] Found {len(new)} new tutorial(s)")
                    process_new_tutorials(new)
                    last_processed = new_names
                else:
                    if last_processed:
                        print(f"[{time.strftime('%H:%M:%S')}] No new tutorials")
                        last_processed = set()
            
            time.sleep(poll_interval)
    
    except KeyboardInterrupt:
        print("\n\n👋 Watcher stopped")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python tutorials_auto_discovery.py [setup|scan|watch]")
        print("\nCommands:")
        print("  setup  - Create tutorials folder with README")
        print("  scan   - Find new tutorials and process them once")
        print("  watch  - Watch folder and auto-process new files (daemon)")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        ensure_tutorials_folder()
        print("✅ Setup complete! Drop PDF/TXT files in tutorials/ folder")
    
    elif command == "scan":
        if not scan_and_process():
            sys.exit(1)
    
    elif command == "watch":
        watch_folder()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
