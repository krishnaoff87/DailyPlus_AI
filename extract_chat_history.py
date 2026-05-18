import sqlite3
import json
import os
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def extract_vscode_chat_history(db_path):
    """
    Extract chat history from VSCode's state.vscdb SQLite database.
    """
    if not os.path.exists(db_path):
        print(f"[ERROR] Database file not found: {db_path}")
        return None

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"[INFO] Found {len(tables)} tables in database:")
        for table in tables:
            print(f"  - {table[0]}")

        # Extract all data from each table
        all_data = {}
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()

                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]

                # Convert to list of dictionaries
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Try to parse JSON if it looks like JSON
                        if isinstance(value, str) and (
                            value.startswith("{") or value.startswith("[")
                        ):
                            try:
                                value = json.loads(value)
                            except Exception:  # noqa: S110
                                pass
                        row_dict[col] = value
                    table_data.append(row_dict)

                all_data[table_name] = {
                    "columns": columns,
                    "row_count": len(rows),
                    "data": table_data,
                }

                print(f"  [OK] {table_name}: {len(rows)} rows")

            except Exception as e:
                print(f"  [WARN] Error reading {table_name}: {e}")

        conn.close()
        return all_data

    except Exception as e:
        print(f"[ERROR] Error connecting to database: {e}")
        return None


def search_for_chat_data(data):
    """
    Search through extracted data for chat-related content.
    """
    chat_related = {}

    for table_name, table_info in data.items():
        for row in table_info["data"]:
            # Look for chat-related keywords in the data
            row_str = json.dumps(row, default=str).lower()
            if any(
                keyword in row_str
                for keyword in [
                    "chat",
                    "conversation",
                    "message",
                    "assistant",
                    "user",
                    "bob",
                    "roo",
                    "cline",
                ]
            ):
                if table_name not in chat_related:
                    chat_related[table_name] = []
                chat_related[table_name].append(row)

    return chat_related


def main():
    # Path to the VSCode workspace storage
    workspace_storage = Path(
        "C:/Users/Reena/AppData/Roaming/Code/User/workspaceStorage/ffc775bb521e4f138a9363ee28bc42ca"
    )
    db_path = workspace_storage / "state.vscdb"

    print("[EXTRACT] VSCode Chat History Extraction")
    print("=" * 60)
    print(f"Database: {db_path}")
    print()

    # Extract all data
    data = extract_vscode_chat_history(str(db_path))

    if data:
        print()
        print("[SEARCH] Searching for chat-related data...")
        print("=" * 60)

        chat_data = search_for_chat_data(data)

        if chat_data:
            print(f"[SUCCESS] Found chat data in {len(chat_data)} tables")

            # Save to JSON file
            output_file = "vscode_chat_data_extracted.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, indent=2, default=str)

            print(f"[SAVED] Chat data saved to: {output_file}")

            # Save full database dump
            full_output = "vscode_full_database_dump.json"
            with open(full_output, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            print(f"[SAVED] Full database dump saved to: {full_output}")

        else:
            print("[WARN] No chat-related data found in database")

            # Still save the full dump for manual inspection
            full_output = "vscode_full_database_dump.json"
            with open(full_output, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            print(f"[SAVED] Full database dump saved to: {full_output}")
            print("        You can manually inspect this file for chat data")


if __name__ == "__main__":
    main()

# Made with Bob
