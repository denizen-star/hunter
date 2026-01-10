# Hunter Daily - {{ date }}

{%- if status_changes and status_changes.total_changes > 0 %}
- **Total Status Changes**: {{ status_changes.total_changes }}
{%- if daily_activities %}
- **Total Activities**: {{ daily_activities|length }}
- **New Applications**: {{ new_applications_count }}
- **Status Changes**: {{ status_changes_count }}
- **Networking Contacts**: {{ networking_contacts_count }}
{%- endif %}
<div class="status-list-container">
{%- if status_changes.from_to_changes %}
{%- for transition, count in status_changes.from_to_changes.items() %}
<div class="status-item" data-transition="{{ transition }}">
  <div class="status-marker"></div>
  <div class="status-content">{{ transition }}: {{ count }}</div>
</div>
{%- endfor %}
{%- else %}
<div class="status-item">
  <div class="status-content">No status transitions today.</div>
</div>
{%- endif %}
</div>

---
{%- else %}
No status changes today.

---
{%- endif %}
## Today's Activities
{%- if daily_activities %}
<div class="status-list-container">
{%- for activity in daily_activities %}
<div class="status-item" data-status="{{ activity.status|lower|replace(' ', '-')|replace('/', '-') }}">
  <div class="status-marker"></div>
  <div class="status-content">
    <span class="timeline-time">{{ activity.timestamp }}</span> - 
    <span class="timeline-company">{{ activity.company }}</span> - 
    <span class="timeline-position">{{ activity.position }}</span> - 
    <span class="timeline-status">{{ activity.status_display }}</span>
  </div>
</div>
{%- endfor %}
</div>
{%- else %}
No activities recorded today.
{%- endif %}

---
## Reports Snapshot - Last 30 Days
<div class="status-list-container">
{%- if status_distribution %}
{%- for status, count in status_distribution.items() %}
<div class="status-item" data-status="{{ status|lower|replace(' ', '-')|replace('/', '-') }}" data-status-raw="{{ status }}">
  <div class="status-marker"></div>
  <div class="status-content"><strong>{{ status }}</strong>: {{ count }}</div>
</div>
{%- endfor %}
{%- else %}
<div class="status-item">
  <div class="status-content">No status data available.</div>
</div>
{%- endif %}
</div>

### Key Metrics
### Application Analytics
- **Total Applications**: {{ metrics.total_applications }}
- **Response Rate**: {{ "%.1f"|format(metrics.response_rate) }}%
- **Interview Conversion Rate**: {{ "%.1f"|format(metrics.interview_rate) }}%

- **Applied**: {{ pipeline.applied }}
- **Responded**: {{ pipeline.responded }} ({{ "%.1f"|format(pipeline.response_rate) }}%)
- **Phone Screens**: {{ pipeline.phone_screen }} ({{ "%.1f"|format(pipeline.phone_screen_rate) }}%)
- **Interviews**: {{ pipeline.interview }} ({{ "%.1f"|format(pipeline.interview_rate) }}%)
- **Offers**: {{ pipeline.offer }} ({{ "%.1f"|format(pipeline.offer_rate) }}%)
---
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

