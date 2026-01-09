# Hunter Daily - {{ date }}

## Status Changes Summary
{%- if status_changes and status_changes.total_changes > 0 %}
### Overview
- **Total Status Changes Today**: {{ status_changes.total_changes }}

### Status Transitions (From → To)
{%- if status_changes.from_to_changes %}
{%- for transition, count in status_changes.from_to_changes.items() %}
- {{ transition }}: {{ count }}
{%- endfor %}
{%- else %}
No status transitions today.
{%- endif %}

---
{%- else %}
No status changes today.

---
{%- endif %}
## Today's Activities
{%- if daily_activities %}
### Summary
- **Total Activities**: {{ daily_activities|length }}
- **New Applications**: {{ new_applications_count }}
- **Status Changes**: {{ status_changes_count }}
- **Networking Contacts**: {{ networking_contacts_count }}

### Activity Details
{%- for activity in daily_activities %}
{{ loop.index }}. **{{ activity.timestamp }}** - {{ activity.company }} - {{ activity.position }}
   {{ loop.index }}.1. {{ activity.activity }}
   {{ loop.index }}.2. Status: {{ activity.status }}
{%- endfor %}
{%- else %}
No activities recorded today.
{%- endif %}

---

## Key Metrics (Last 30 Days)
### Application Analytics
- **Total Applications**: {{ metrics.total_applications }}
- **Response Rate**: {{ "%.1f"|format(metrics.response_rate) }}%
- **Interview Conversion Rate**: {{ "%.1f"|format(metrics.interview_rate) }}%

### Pipeline Status
- **Applied**: {{ pipeline.applied }}
- **Responded**: {{ pipeline.responded }} ({{ "%.1f"|format(pipeline.response_rate) }}%)
- **Phone Screens**: {{ pipeline.phone_screen }} ({{ "%.1f"|format(pipeline.phone_screen_rate) }}%)
- **Interviews**: {{ pipeline.interview }} ({{ "%.1f"|format(pipeline.interview_rate) }}%)
- **Offers**: {{ pipeline.offer }} ({{ "%.1f"|format(pipeline.offer_rate) }}%)

---

## Reports Snapshot
### Status Distribution
{%- if status_distribution %}
{%- for status, count in status_distribution.items() %}
- **{{ status }}**: {{ count }}
{%- endfor %}
{%- else %}
No status data available.
{%- endif %}

---

## Best Performing Days
{%- if best_days %}
{%- for day, stats in best_days.items() %}
- **{{ day }}**: {{ stats.total_applications }} applications, {{ "%.1f"|format(stats.response_rate) }}% response rate
{%- endfor %}
{%- else %}
No day performance data available.
{%- endif %}

---

{%- if skills_analysis is defined %}
## Skills Analysis
### Most Requested Skills (Top 10)
{%- for skill in skills_analysis.most_requested %}
- **{{ skill.skill }}**: Appears in {{ skill.frequency }} jobs ({{ "%.1f"|format(skill.percentage) }}%)
{%- endfor %}

### Skill Gaps (Top 10)
{%- for gap in skills_analysis.skill_gaps %}
- **{{ gap.skill }}**: Missing in {{ gap.frequency }} jobs ({{ "%.1f"|format(gap.percentage) }}%)
{%- endfor %}
{%- endif %}

---

*Generated on {{ generated_at }}*

