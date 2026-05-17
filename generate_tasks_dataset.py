import json
from datetime import datetime, timedelta

# Base date for the week
base_date = datetime(2026, 5, 12, 9, 0, 0)

# Team members
team_members = [
    "Rajesh Kumar",
    "Sneha Reddy",
    "David Martinez",
    "Ananya Iyer",
    "Vikram Singh",
    "Jessica Lee",
    "Carlos Rodriguez",
    "Lisa Wang",
    "Arun Patel",
    "Priya Sharma",
    "Michael Chen",
    "Amit Desai",
    "Jennifer Brown",
    "Tom Anderson",
    "Sarah Johnson",
    "Kevin O'Brien",
    "Emily Watson",
    "Rahul Mehta",
    "Sophie Chen",
    "James Wilson",
    "Maria Garcia",
    "Robert Taylor",
    "Nina Patel",
    "Alex Thompson",
]

# Projects
projects = [
    "Payment Gateway Modernization",
    "Customer Onboarding Enhancement",
    "Fraud Prevention Initiative",
    "Mobile App Enhancement Q2",
    "Regulatory Compliance 2026",
    "Customer Experience Platform",
    "Cloud Migration Initiative",
    "Credit Risk Management",
    "API Infrastructure Enhancement",
    "Merchant Services Platform",
    "Security Hardening Q2",
    "Financial Operations Automation",
    "Customer Retention Analytics",
    "Business Continuity Planning",
    "Data Governance Initiative",
    "International Expansion",
]


def generate_tasks():
    tasks = []
    task_count = 105

    departments = [
        "Engineering",
        "Compliance",
        "Product",
        "Customer Support",
        "Risk Management",
        "Data Analytics",
        "Marketing",
        "Finance",
        "Operations",
    ]
    priorities = ["Critical", "High", "Medium", "Low"]
    statuses = ["Completed", "In Progress", "Not Started", "Blocked", "On Hold"]
    categories = [
        "Development",
        "Testing",
        "Documentation",
        "Meeting",
        "Review",
        "Research",
        "Deployment",
        "Bug Fix",
        "Feature Request",
        "Compliance Check",
        "Security Audit",
        "Data Analysis",
        "Customer Issue",
        "Administrative",
    ]

    task_templates = [
        (
            "Payment Processing API Enhancement",
            "Engineering",
            "Development",
            "Payment Gateway Modernization",
        ),
        (
            "KYC Verification Process Update",
            "Compliance",
            "Compliance Check",
            "Customer Onboarding Enhancement",
        ),
        (
            "Fraud Detection Algorithm Optimization",
            "Data Analytics",
            "Data Analysis",
            "Fraud Prevention Initiative",
        ),
        (
            "Mobile App Feature Implementation",
            "Engineering",
            "Feature Request",
            "Mobile App Enhancement Q2",
        ),
        (
            "Regulatory Compliance Audit",
            "Compliance",
            "Compliance Check",
            "Regulatory Compliance 2026",
        ),
        (
            "Customer Support Ticket Resolution",
            "Customer Support",
            "Customer Issue",
            "Customer Experience Platform",
        ),
        (
            "Database Migration Task",
            "Engineering",
            "Deployment",
            "Cloud Migration Initiative",
        ),
        (
            "Credit Scoring Model Update",
            "Data Analytics",
            "Data Analysis",
            "Credit Risk Management",
        ),
        (
            "API Security Enhancement",
            "Engineering",
            "Security Audit",
            "API Infrastructure Enhancement",
        ),
        (
            "Merchant Onboarding Process",
            "Product",
            "Development",
            "Merchant Services Platform",
        ),
        (
            "Security Vulnerability Fix",
            "Engineering",
            "Bug Fix",
            "Security Hardening Q2",
        ),
        (
            "Financial Reconciliation Automation",
            "Finance",
            "Development",
            "Financial Operations Automation",
        ),
        (
            "Customer Churn Analysis",
            "Data Analytics",
            "Data Analysis",
            "Customer Retention Analytics",
        ),
        (
            "Disaster Recovery Testing",
            "Operations",
            "Testing",
            "Business Continuity Planning",
        ),
        (
            "Data Privacy Compliance",
            "Compliance",
            "Compliance Check",
            "Data Governance Initiative",
        ),
        (
            "International Payment Support",
            "Engineering",
            "Feature Request",
            "International Expansion",
        ),
        (
            "Performance Optimization",
            "Engineering",
            "Development",
            "Payment Gateway Modernization",
        ),
        (
            "Risk Assessment Report",
            "Risk Management",
            "Review",
            "Credit Risk Management",
        ),
        (
            "Marketing Campaign Analytics",
            "Marketing",
            "Data Analysis",
            "Customer Retention Analytics",
        ),
        (
            "Documentation Update",
            "Engineering",
            "Documentation",
            "API Infrastructure Enhancement",
        ),
    ]

    for i in range(1, task_count + 1):
        template_idx = (i - 1) % len(task_templates)
        task_name, dept, category, project = task_templates[template_idx]

        # Vary the task name
        task_name = (
            f"{task_name} - Phase {((i-1) // len(task_templates)) + 1}"
            if i > len(task_templates)
            else task_name
        )

        # Determine status and completion
        if i <= 30:
            status = "Completed"
            completion = 100
            actual_hours = (i % 20) + 8
            completion_date = (
                base_date + timedelta(days=(i % 5), hours=(i % 8))
            ).isoformat() + "Z"
        elif i <= 75:
            status = "In Progress"
            completion = 50 + (i % 40)
            actual_hours = (i % 15) + 5
            completion_date = None
        elif i <= 90:
            status = "Not Started"
            completion = 0
            actual_hours = None
            completion_date = None
        elif i <= 95:
            status = "Blocked"
            completion = 30 + (i % 20)
            actual_hours = (i % 10) + 3
            completion_date = None
        else:
            status = "On Hold"
            completion = 20 + (i % 30)
            actual_hours = (i % 8) + 2
            completion_date = None

        # Determine priority
        if i % 10 == 0:
            priority = "Critical"
        elif i % 3 == 0:
            priority = "High"
        elif i % 2 == 0:
            priority = "Medium"
        else:
            priority = "Low"

        # Calculate dates
        start_day = (i - 1) % 7
        duration_days = (i % 5) + 1
        start_date = (
            base_date + timedelta(days=start_day, hours=(i % 8))
        ).isoformat() + "Z"
        due_date = (
            base_date + timedelta(days=start_day + duration_days, hours=17)
        ).isoformat() + "Z"

        # Assign team member
        team_member = team_members[(i - 1) % len(team_members)]

        # Create stakeholders
        stakeholder_count = 2 + (i % 3)
        stakeholders = [
            team_members[j % len(team_members)] for j in range(i, i + stakeholder_count)
        ]

        # Dependencies
        dependencies = []
        if i > 10 and i % 7 == 0:
            dependencies = [f"TASK-{str(i-5).zfill(3)}"]
        elif i > 20 and i % 11 == 0:
            dependencies = [f"TASK-{str(i-10).zfill(3)}", f"TASK-{str(i-3).zfill(3)}"]

        # Tags
        tags = [
            category.lower().replace(" ", "-"),
            dept.lower().replace(" ", "-"),
            priority.lower(),
            project.lower().replace(" ", "-")[:20],
        ]

        # Estimated hours
        estimated_hours = 8 + (i % 32)

        # Description
        descriptions = [
            f"Implement and deploy {task_name.lower()} with comprehensive testing and documentation.",
            f"Analyze and optimize {task_name.lower()} to improve system performance and user experience.",
            f"Conduct thorough review of {task_name.lower()} ensuring compliance with regulatory standards.",
            f"Develop automated solution for {task_name.lower()} with monitoring and alerting capabilities.",
            f"Research and evaluate {task_name.lower()} considering scalability and security requirements.",
        ]
        description = descriptions[i % len(descriptions)]

        # Notes
        notes_templates = [
            f"Task progressing as planned. {completion}% complete with no major blockers.",
            "Completed successfully. All acceptance criteria met and deployed to production.",
            "Awaiting dependency completion. Team coordinating with stakeholders.",
            "In progress. Some technical challenges identified but solutions being implemented.",
            "Scheduled to start soon. All prerequisites and resources confirmed.",
        ]
        notes = notes_templates[i % len(notes_templates)]

        task = {
            "task_id": f"TASK-{str(i).zfill(3)}",
            "task_name": task_name,
            "task_description": description,
            "assigned_team_member": team_member,
            "department": dept,
            "priority_level": priority,
            "status": status,
            "estimated_hours": estimated_hours,
            "actual_hours": actual_hours,
            "start_date_time": start_date,
            "due_date_time": due_date,
            "completion_date_time": completion_date,
            "task_category": category,
            "dependencies": dependencies,
            "project_name": project,
            "stakeholders": stakeholders,
            "percentage_completion": completion,
            "tags": tags,
            "notes": notes,
        }

        tasks.append(task)

    return tasks


# Generate the dataset
dataset = {
    "metadata": {
        "dataset_name": "DailyPlus AI Fintech Tasks - Week Dataset",
        "version": "1.0.0",
        "generated_date": datetime.utcnow().isoformat() + "Z",
        "week_start": "2026-05-12",
        "week_end": "2026-05-18",
        "total_tasks": 105,
        "total_team_members": 24,
        "total_projects": 16,
        "departments": [
            "Engineering",
            "Compliance",
            "Product",
            "Customer Support",
            "Risk Management",
            "Data Analytics",
            "Marketing",
            "Finance",
            "Operations",
        ],
    },
    "tasks": generate_tasks(),
}

# Write to file
with open("data/fintech_tasks_week_dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {len(dataset['tasks'])} tasks")
print("File saved to: data/fintech_tasks_week_dataset.json")

# Made with Bob
