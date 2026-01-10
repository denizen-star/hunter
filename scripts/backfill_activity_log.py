#!/usr/bin/env python3
"""
Migration script to backfill activity log from existing applications and networking contacts.
This should be run once to populate the activity log with historical data.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.services.networking_processor import NetworkingProcessor
from app.services.activity_log_service import ActivityLogService
from datetime import datetime, timezone, timedelta


def backfill_activity_log():
    """Backfill activity log from existing data"""
    print("=" * 80)
    print("Activity Log Backfill Migration")
    print("=" * 80)
    print()
    
    job_processor = JobProcessor()
    networking_processor = NetworkingProcessor()
    activity_log = ActivityLogService()
    
    # Load existing log to check what's already there
    existing_log = activity_log._load_log()
    existing_activity_ids = {a.get('id') for a in existing_log.get('activities', [])}
    print(f"Found {len(existing_activity_ids)} existing activities in log")
    print()
    
    # Backfill job applications
    print("Processing job applications...")
    applications = job_processor.list_all_applications()
    print(f"Found {len(applications)} applications")
    
    created_count = 0
    status_count = 0
    
    for app in applications:
        # Log application creation
        activity_id = f"{app.id}_{app.created_at.strftime('%Y%m%d%H%M%S')}"
        if activity_id not in existing_activity_ids:
            try:
                activity_log.log_application_created(
                    application_id=app.id,
                    company=app.company,
                    job_title=app.job_title,
                    created_at=app.created_at,
                    match_score=app.match_score,
                    status=app.status
                )
                created_count += 1
            except Exception as e:
                print(f"  Warning: Could not log application {app.id}: {e}")
        
        # Log status changes from update files
        updates = job_processor.get_application_updates(app)
        for update in updates:
            try:
                from datetime import datetime as dt
                update_dt = dt.strptime(update['timestamp'], '%Y%m%d%H%M%S')
                update_dt = update_dt.replace(tzinfo=timezone(timedelta(hours=-4)))
                
                activity_id = f"{app.id}_status_{update_dt.strftime('%Y%m%d%H%M%S')}"
                if activity_id not in existing_activity_ids:
                    # We need to determine the old status - for now, use current status
                    # In a real scenario, we'd need to track status history
                    old_status = app.status  # This is approximate
                    
                    # Normalize networking statuses to remove person names
                    status = update['status']
                    if update.get('type') == 'networking':
                        # Remove person names from networking statuses
                        # Pattern: "Name-Status" or "Name---Status" -> "Status"
                        parts = status.replace('---', '-').replace('--', '-').split('-')
                        status_keywords = ['contacted', 'sent', 'research', 'conversation', 'pending', 
                                          'inactive', 'dormant', 'ready', 'new', 'connection', 'archive', 'cold', 'to']
                        for part in reversed(parts):
                            part_lower = part.lower()
                            if any(keyword in part_lower for keyword in status_keywords):
                                status = part.replace('-', ' ').strip()
                                break
                        else:
                            # If no keyword found, use last part
                            if len(parts) > 1:
                                status = parts[-1].replace('-', ' ').strip()
                    
                    activity_log.log_application_status_changed(
                        application_id=app.id,
                        company=app.company,
                        job_title=app.job_title,
                        old_status=old_status,
                        new_status=status,
                        updated_at=update_dt,
                        notes=None
                    )
                    status_count += 1
            except Exception as e:
                print(f"  Warning: Could not log status update for {app.id}: {e}")
    
    print(f"  ✓ Logged {created_count} application creations")
    print(f"  ✓ Logged {status_count} status changes")
    print()
    
    # Backfill networking contacts
    print("Processing networking contacts...")
    contacts = networking_processor.list_all_contacts()
    print(f"Found {len(contacts)} networking contacts")
    
    contact_created_count = 0
    contact_status_count = 0
    
    for contact in contacts:
        # Log contact creation
        activity_id = f"{contact.id}_{contact.created_at.strftime('%Y%m%d%H%M%S')}"
        if activity_id not in existing_activity_ids:
            try:
                activity_log.log_networking_contact_created(
                    contact_id=contact.id,
                    person_name=contact.person_name,
                    company_name=contact.company_name,
                    job_title=contact.job_title,
                    created_at=contact.created_at,
                    status=contact.status,
                    match_score=contact.match_score
                )
                contact_created_count += 1
            except Exception as e:
                print(f"  Warning: Could not log contact {contact.id}: {e}")
        
        # Log status changes from update files
        updates = networking_processor.get_contact_updates(contact)
        for update in updates:
            try:
                from datetime import datetime as dt
                update_dt = dt.strptime(update['timestamp'], '%Y%m%d%H%M%S')
                update_dt = update_dt.replace(tzinfo=timezone(timedelta(hours=-4)))
                
                activity_id = f"{contact.id}_status_{update_dt.strftime('%Y%m%d%H%M%S')}"
                if activity_id not in existing_activity_ids:
                    old_status = contact.status  # This is approximate
                    
                    # Normalize networking statuses to remove person names
                    status = update['status']
                    # Remove person names from networking statuses
                    # Pattern: "Name-Status" or "Name---Status" -> "Status"
                    parts = status.replace('---', '-').replace('--', '-').split('-')
                    status_keywords = ['contacted', 'sent', 'research', 'conversation', 'pending', 
                                      'inactive', 'dormant', 'ready', 'new', 'connection', 'archive', 'cold', 'to']
                    for part in reversed(parts):
                        part_lower = part.lower()
                        if any(keyword in part_lower for keyword in status_keywords):
                            status = part.replace('-', ' ').strip()
                            break
                    else:
                        # If no keyword found, use last part
                        if len(parts) > 1:
                            status = parts[-1].replace('-', ' ').strip()
                    
                    activity_log.log_networking_status_changed(
                        contact_id=contact.id,
                        person_name=contact.person_name,
                        company_name=contact.company_name,
                        old_status=old_status,
                        new_status=status,
                        updated_at=update_dt,
                        notes=None
                    )
                    contact_status_count += 1
            except Exception as e:
                print(f"  Warning: Could not log status update for {contact.id}: {e}")
    
    print(f"  ✓ Logged {contact_created_count} networking contact creations")
    print(f"  ✓ Logged {contact_status_count} networking status changes")
    print()
    
    # Summary
    print("=" * 80)
    print("Backfill Complete!")
    print("=" * 80)
    print(f"Total activities logged:")
    print(f"  - Application creations: {created_count}")
    print(f"  - Application status changes: {status_count}")
    print(f"  - Networking contact creations: {contact_created_count}")
    print(f"  - Networking status changes: {contact_status_count}")
    print(f"  - Grand total: {created_count + status_count + contact_created_count + contact_status_count}")
    print()
    print("The activity log is now ready for fast reporting!")


if __name__ == '__main__':
    backfill_activity_log()

