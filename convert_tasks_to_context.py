import json

# Load the tasks dataset
with open("data/fintech_tasks_week_dataset.json", "r", encoding="utf-8") as f:
    tasks_data = json.load(f)

# Convert tasks to mock context items format
context_items = []

for task in tasks_data["tasks"]:
    # Map task to context item format
    # Determine source based on task category
    source_mapping = {
        "Meeting": "calendar",
        "Customer Issue": "email",
        "Review": "email",
        "Administrative": "email",
    }
    source = source_mapping.get(task["task_category"], "chat")

    # Map priority to urgency
    urgency_mapping = {
        "Critical": "urgent",
        "High": "high",
        "Medium": "medium",
        "Low": "low",
    }
    urgency = urgency_mapping.get(task["priority_level"], "medium")

    # Create body with task details
    body = f"{task['task_description']}\n\n"
    body += f"**Project:** {task['project_name']}\n"
    body += f"**Department:** {task['department']}\n"
    body += (
        f"**Status:** {task['status']} ({task['percentage_completion']}% complete)\n"
    )
    body += f"**Estimated Hours:** {task['estimated_hours']}\n"

    if task["actual_hours"]:
        body += f"**Actual Hours:** {task['actual_hours']}\n"

    if task["dependencies"]:
        body += f"**Dependencies:** {', '.join(task['dependencies'])}\n"

    body += f"**Due Date:** {task['due_date_time']}\n"

    if task["notes"]:
        body += f"\n**Notes:** {task['notes']}"

    # Determine if has action based on status
    has_action = task["status"] in ["Not Started", "In Progress", "Blocked"]

    context_item = {
        "id": task["task_id"],
        "source": source,
        "timestamp": task["start_date_time"],
        "subject": task["task_name"],
        "body": body,
        "sender": task["assigned_team_member"],
        "participants": task["stakeholders"],
        "urgency_hint": urgency,
        "has_action": has_action,
    }

    context_items.append(context_item)

# Save to mock_daily_context.json
with open("data/mock_daily_context.json", "w", encoding="utf-8") as f:
    json.dump(context_items, f, indent=2, ensure_ascii=False)

print(f"Successfully converted {len(context_items)} tasks to context items")
print("File saved to: data/mock_daily_context.json")

# Validate the structure
print("\nValidating structure...")
sample = context_items[0]
required_fields = [
    "id",
    "source",
    "timestamp",
    "subject",
    "body",
    "sender",
    "participants",
    "urgency_hint",
    "has_action",
]
all_present = all(field in sample for field in required_fields)
print(f"All required fields present: {all_present}")
print(f"Sample item ID: {sample['id']}")
print(f"Sample source: {sample['source']}")
print(f"Sample urgency: {sample['urgency_hint']}")

# Made with Bob
