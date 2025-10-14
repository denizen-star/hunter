# Hiring Team Information Extraction Example

## Input Text (from LinkedIn job posting)
```
Meet the hiring team
Ethan Vatske
Ethan Vatske  
 3rd
Lead Recruiter at Insight Global
Job poster
```

## AI Extraction (Section 13)
```
Ethan Vatske | Lead Recruiter at Insight Global | Connection: 3rd degree | Role: Job poster
```

## Visual Display in Job Description Tab

### 👥 Hiring Team Information

```
┌─────────────────────────────────────────────────────────────┐
│ Ethan Vatske                                    [3rd] [Job poster] │
│ Lead Recruiter at Insight Global                              │
└─────────────────────────────────────────────────────────────┘
```

### Features:
- **Name**: Prominently displayed in bold
- **Position**: Shown below name in gray text
- **Connection Degree**: Colored badge (green for 1st/2nd, yellow for 3rd+)
- **Role**: Colored badge (blue for "Job poster", purple for others)

## Multiple Team Members Example
```
Ethan Vatske | Lead Recruiter at Insight Global | Connection: 3rd degree | Role: Job poster
Sarah Johnson | Senior Recruiter at Insight Global | Connection: 2nd degree | Role: Hiring manager
Mike Chen | Engineering Manager at TechCorp | Connection: 1st degree | Role: Interviewer
```

Would display as three separate cards with appropriate color coding.

## Benefits:
1. **Network Analysis**: See your connection degree to hiring team members
2. **Strategic Outreach**: Know who posted the job vs who will interview
3. **Relationship Building**: Identify mutual connections for warm introductions
4. **Decision Making**: Understand the hiring team structure

## Automatic Detection:
- Looks for "Meet the hiring team" sections
- Extracts name, position, company, connection degree, and role
- Formats into structured cards with visual badges
- Only displays when hiring team information is available
