# !/usr/bin/python

import os, stat
import json

from datetime import datetime, timezone

# path from which to start audit
ROOT_DIR = "public_html/"
INITIAL_RUN = False

# set up class to model individual audits
class FileAudit:
    def __init__(self, path, st_mode, st_size, st_mtime):
        self.path = path
        self.stat_result = {
            "st_mode": st_mode,
            "st_size": st_size,
            "st_mtime": st_mtime
        }

    def __str__(self):
        return f"{self.path} - {json.dumps(self.stat_result)}"

    def __hash__(self):
        return hash((
            self.path, 
            self.stat_result["st_mode"],
            self.stat_result["st_size"],
            self.stat_result["st_mtime"]
        ))

    def __eq__(self, other):
        return (
            self.path, 
            self.stat_result["st_mode"],
            self.stat_result["st_size"],
            self.stat_result["st_mtime"]
        ) == (
            other.path, 
            other.stat_result["st_mode"],
            other.stat_result["st_size"],
            other.stat_result["st_mtime"]
        )


def load_log_file():
    # open log file and read it to list
    try:
        audit_log_fr = open("audit_log.log", "r")
        audit_log_list = audit_log_fr.read().split("\n")
        audit_log_fr.close

        audit_log = []

        # convert list of strings to FileAudit objects        
        # should probably do additional checks here but this at least handles initialization
        if audit_log_list and len(audit_log_list) > 0:
            for audit_str in audit_log_list:
                if len(audit_str) > 0:
                    path, stat_result_str = audit_str.split(" - ")
                    stat_result = json.loads(stat_result_str)
                    audit_log.append(
                        FileAudit(
                            path,
                            stat_result["st_mode"],
                            stat_result["st_size"],
                            stat_result["st_mtime"]
                        )
                    )
            return audit_log
        else:
            print("Empty log file found.")
    except FileNotFoundError as e:
        print("No log file found. One will be created.")
        
    print("The Auditor will begin tracking your files.")
    return None


def audit_file_system():
    # open log file for writing
    audit_log_fw = open("audit_log.log", "w")
    new_audit = []

    # recurse/walk directories and files, add FileAudit objects to new_audit list
    for root, dirs, files in os.walk(ROOT_DIR, followlinks=True):
        for name in files:
            path = os.path.join(root, name)
            # ignore the source code and log file itself
            if path != "./audit_log.log" and path != "./main.py":
                stat_result = os.stat(os.path.join(root, name))
                new_audit.append(
                    FileAudit(
                        path,
                        stat_result.st_mode,
                        stat_result.st_size,
                        stat_result.st_mtime
                    )
                )

    # write new audit to log file
    audit_log_fw.write(f"\n".join([audit.__str__() for audit in new_audit])) 
    audit_log_fw.close()

    return new_audit


def analyze_results(previous_audit, current_audit):
    deleted = set(previous_audit) - set(current_audit)
    new = set(current_audit) - set(previous_audit)

    if len(deleted) < 1 and len(new) < 1:
        print("No items for review.")
    else:
        # store paths/names of edited items for easy reference 
        # so they aren't counted as an addition/deletion
        edits = []

        # files that have changed appear in both lists
        # this is terribly non-performant, but works
        for new_file in new:
            for deleted_file in deleted:
                if deleted_file.path == new_file.path:
                    edits.append(new_file.path)
                    print(f"{new_file.path} was edited at {datetime.fromtimestamp(new_file.stat_result['st_mtime'], tz=timezone.utc)}. \nHere's what changed:")
                    if new_file.stat_result["st_mode"] != deleted_file.stat_result["st_mode"]:
                        print(f"Mode: {stat.filemode(deleted_file.stat_result['st_mode'])} --> {stat.filemode(new_file.stat_result['st_mode'])}")
                    if new_file.stat_result["st_size"] != deleted_file.stat_result["st_size"]:
                        print(f"Size: {deleted_file.stat_result['st_size']} --> {new_file.stat_result['st_size']} (bytes)")
        for audit in deleted:
            if audit.path not in edits:
                print(f"(-) File deletion detected: {audit.path}")

        for audit in new:
            if audit.path not in edits:
                print(f"(+) New file detected: {audit.path}")


if __name__ == "__main__":
    print("🔒 File System Security Audit Running...")

    previous_audit = load_log_file()
    current_audit = audit_file_system()

    # compare audit_log with new_audit
    if previous_audit and current_audit:
        analyze_results(previous_audit=previous_audit, current_audit=current_audit)
