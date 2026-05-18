import sqlite3
import json
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: S110
        pass


def extract_workspace_data(workspace_path):
    """Extract data from a workspace storage folder."""
    db_path = workspace_path / "state.vscdb"
    workspace_json = workspace_path / "workspace.json"

    result = {
        "workspace_id": workspace_path.name,
        "workspace_folder": None,
        "chat_sessions": [],
        "has_data": False,
    }

    # Read workspace.json to get folder info
    if workspace_json.exists():
        try:
            with open(workspace_json, "r", encoding="utf-8") as f:
                ws_data = json.load(f)
                result["workspace_folder"] = ws_data.get("folder", "Unknown")
        except Exception:  # noqa: S110
            pass

    # Extract from database
    if not db_path.exists():
        return result

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get chat session data
        cursor.execute(
            "SELECT key, value FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%Chat%' OR key LIKE '%session%'"
        )
        rows = cursor.fetchall()

        for key, value in rows:
            try:
                if value:
                    parsed_value = (
                        json.loads(value) if isinstance(value, str) else value
                    )
                    result["chat_sessions"].append({"key": key, "data": parsed_value})
                    result["has_data"] = True
            except Exception:  # noqa: S110
                pass

        conn.close()

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    workspace_storage = Path(
        "C:/Users/Reena/AppData/Roaming/Code/User/workspaceStorage"
    )

    print("[SCAN] Scanning all VSCode workspace storage folders...")
    print("=" * 60)

    all_workspaces = []

    for workspace_dir in workspace_storage.iterdir():
        if workspace_dir.is_dir():
            print(f"[CHECK] {workspace_dir.name}")
            data = extract_workspace_data(workspace_dir)
            all_workspaces.append(data)

            if data["has_data"]:
                print("  [FOUND] Chat data found!")
                print(f"  Folder: {data['workspace_folder']}")
            else:
                print("  [EMPTY] No chat data")

    print()
    print("=" * 60)
    print(f"[SUMMARY] Scanned {len(all_workspaces)} workspaces")

    # Save results
    output_file = "all_workspaces_chat_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_workspaces, f, indent=2, default=str)

    print(f"[SAVED] Results saved to: {output_file}")

    # Find DailyPlus_AI workspace
    dailyplus_workspace = None
    for ws in all_workspaces:
        if ws["workspace_folder"] and "DailyPlus_AI" in ws["workspace_folder"]:
            dailyplus_workspace = ws
            break

    if dailyplus_workspace:
        print()
        print("[SUCCESS] Found DailyPlus_AI workspace!")
        print(f"Workspace ID: {dailyplus_workspace['workspace_id']}")
        print(f"Folder: {dailyplus_workspace['workspace_folder']}")

        if dailyplus_workspace["chat_sessions"]:
            print(f"Chat sessions found: {len(dailyplus_workspace['chat_sessions'])}")

            # Save DailyPlus specific data
            dailyplus_file = "dailyplus_chat_history.json"
            with open(dailyplus_file, "w", encoding="utf-8") as f:
                json.dump(dailyplus_workspace, f, indent=2, default=str)
            print(f"[SAVED] DailyPlus chat data saved to: {dailyplus_file}")
        else:
            print("[WARN] No chat sessions found in DailyPlus workspace")
    else:
        print()
        print("[WARN] DailyPlus_AI workspace not found in storage")


if __name__ == "__main__":
    main()

# Made with Bob
