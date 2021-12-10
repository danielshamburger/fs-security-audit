# 🔒 File System Security Audit

This script crawls the file system from a specified directory and runs a basic security audit allowing the user to monitor file changes, including new and deleted files as well as changes to file size or mode.

To automatically run this tool upon the start of a shell session on a Unix system (with bash), add `python $HOME/{path-to-source}/fs-security-audit/main.py` to `~/.bashrc`.

## System Overview

1. Check for and open log file. Parse JSON containing the previous state of the system and store it for comparison.
2. Walk through directories with `os.walk` and record file information using `os.stat`.
3. Compare the previous state of the file system with the current state and output deletions, additions, and edits.

## Data Structures

The `FileAudit` class defines the data structure to hold a single file audit:
```
def __init__(self, path, st_mode, st_size, st_mtime):
  self.path = path
  self.stat_result = {
    "st_mode": st_mode,
    "st_size": st_size,
    "st_mtime": st_mtime
  }
```
