#!/usr/bin/env python3
"""
Migration script for networking status system.

Migrates contacts from old status system (16 statuses) to new status system (11 statuses).

Usage:
    python scripts/migrate_networking_statuses.py [--dry-run] [--backup-dir BACKUP_DIR]

Options:
    --dry-run: Run migration without making changes (test mode)
    --backup-dir: Directory to store backups (default: data/backups/networking_migration_YYYYMMDD_HHMMSS)
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import shutil
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.file_utils import get_data_path, load_yaml, save_yaml, ensure_dir_exists
from app.models.networking_contact import NetworkingContact


# Status migration mapping: old status -> new status
STATUS_MIGRATION_MAP = {
    # No change
    'To Research': 'To Research',
    
    # Prospecting phase
    'Ready to Contact': 'Ready to Connect',
    
    # Outreach phase
    'Contacted - Sent': 'Pending Reply',
    'Contacted---Sent': 'Pending Reply',
    'Contacted Sent': 'Pending Reply',
    'Contacted - Replied': 'Connected - Initial',
    'Contacted---Replied': 'Connected - Initial',
    'Contacted Replied': 'Connected - Initial',
    'Contacted - No Response': 'Pending Reply',
    'Contacted---No Response': 'Pending Reply',
    'Contacted No Response': 'Pending Reply',
    'New Connection': 'Connected - Initial',
    'Cold/Archive': 'Cold/Inactive',
    
    # Engagement phase
    'In Conversation': 'In Conversation',  # No change
    'Action Pending - You': 'In Conversation',
    'Action Pending---You': 'In Conversation',
    'Action Pending You': 'In Conversation',
    'Action Pending - Them': 'In Conversation',
    'Action Pending---Them': 'In Conversation',
    'Action Pending Them': 'In Conversation',
    'Meeting Scheduled': 'Meeting Scheduled',  # No change
    'Meeting Complete': 'Meeting Complete',  # No change
    
    # Nurture phase
    'Nurture (1-3 Mo.)': 'Strong Connection',
    'Nurture (4-6 Mo.)': 'Strong Connection',
    'Nurture 1-3 Mo': 'Strong Connection',
    'Nurture 4-6 Mo': 'Strong Connection',
    'Referral Partner': 'Referral Partner',  # No change
    'Inactive/Dormant': 'Dormant',
    'Dormant': 'Dormant'  # Handle if already migrated
}


def normalize_status(status: str) -> str:
    """Normalize status string for matching"""
    if not status:
        return status
    # Handle variations in spacing and dashes
    normalized = status.strip().replace('  ', ' ').replace('---', ' - ')
    return normalized


def get_new_status(old_status: str) -> str:
    """Get new status for old status"""
    if not old_status:
        return old_status
    
    # Try exact match first
    if old_status in STATUS_MIGRATION_MAP:
        return STATUS_MIGRATION_MAP[old_status]
    
    # Try normalized match
    normalized = normalize_status(old_status)
    if normalized in STATUS_MIGRATION_MAP:
        return STATUS_MIGRATION_MAP[normalized]
    
    # Check if already a new status
    new_statuses = [
        'To Research', 'Ready to Connect', 'Pending Reply',
        'Connected - Initial', 'Cold/Inactive', 'In Conversation',
        'Meeting Scheduled', 'Meeting Complete', 'Strong Connection',
        'Referral Partner', 'Dormant'
    ]
    
    if old_status in new_statuses or normalized in new_statuses:
        return old_status  # Already migrated
    
    # Unknown status - return as-is with warning
    print(f"Warning: Unknown status '{old_status}' - keeping as-is")
    return old_status


def backup_contact_metadata(contact_folder: Path, backup_dir: Path) -> Path:
    """Backup a contact's metadata.yaml file"""
    metadata_file = contact_folder / 'metadata.yaml'
    if not metadata_file.exists():
        return None
    
    # Create backup path maintaining folder structure
    relative_path = contact_folder.relative_to(get_data_path('networking'))
    backup_path = backup_dir / relative_path
    ensure_dir_exists(backup_path)
    
    backup_file = backup_path / 'metadata.yaml'
    shutil.copy2(metadata_file, backup_file)
    return backup_file


def migrate_contact(contact_folder: Path, dry_run: bool = False) -> dict:
    """Migrate a single contact's status"""
    metadata_file = contact_folder / 'metadata.yaml'
    
    if not metadata_file.exists():
        return {
            'status': 'skipped',
            'reason': 'No metadata.yaml found',
            'contact_folder': str(contact_folder)
        }
    
    try:
        metadata = load_yaml(metadata_file)
        old_status = metadata.get('status', 'To Research')
        new_status = get_new_status(old_status)
        
        if old_status == new_status:
            return {
                'status': 'no_change',
                'old_status': old_status,
                'new_status': new_status,
                'contact_folder': str(contact_folder)
            }
        
        if not dry_run:
            # Update metadata
            metadata['status'] = new_status
            # Add migration metadata
            if 'migration_history' not in metadata:
                metadata['migration_history'] = []
            metadata['migration_history'].append({
                'old_status': old_status,
                'new_status': new_status,
                'migrated_at': datetime.now().isoformat()
            })
            save_yaml(metadata, metadata_file)
        
        return {
            'status': 'migrated',
            'old_status': old_status,
            'new_status': new_status,
            'contact_folder': str(contact_folder)
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'contact_folder': str(contact_folder)
        }


def create_backup(networking_dir: Path, backup_dir: Path) -> None:
    """Create backup of all metadata.yaml files"""
    print(f"Creating backup to {backup_dir}...")
    ensure_dir_exists(backup_dir)
    
    contact_folders = [f for f in networking_dir.iterdir() if f.is_dir()]
    backed_up = 0
    
    for contact_folder in contact_folders:
        try:
            backup_file = backup_contact_metadata(contact_folder, backup_dir)
            if backup_file:
                backed_up += 1
        except Exception as e:
            print(f"Warning: Could not backup {contact_folder.name}: {e}")
    
    print(f"Backed up {backed_up} contact metadata files")


def validate_migration(networking_dir: Path) -> dict:
    """Validate migrated contacts"""
    print("Validating migration...")
    
    contact_folders = [f for f in networking_dir.iterdir() if f.is_dir()]
    valid_statuses = [
        'To Research', 'Ready to Connect', 'Pending Reply',
        'Connected - Initial', 'Cold/Inactive', 'In Conversation',
        'Meeting Scheduled', 'Meeting Complete', 'Strong Connection',
        'Referral Partner', 'Dormant'
    ]
    
    validation_results = {
        'total': len(contact_folders),
        'valid': 0,
        'invalid': 0,
        'errors': []
    }
    
    for contact_folder in contact_folders:
        metadata_file = contact_folder / 'metadata.yaml'
        if not metadata_file.exists():
            continue
        
        try:
            metadata = load_yaml(metadata_file)
            status = metadata.get('status', '')
            
            if status in valid_statuses:
                validation_results['valid'] += 1
            else:
                validation_results['invalid'] += 1
                validation_results['errors'].append({
                    'contact': contact_folder.name,
                    'status': status
                })
        except Exception as e:
            validation_results['invalid'] += 1
            validation_results['errors'].append({
                'contact': contact_folder.name,
                'error': str(e)
            })
    
    return validation_results


def generate_migration_report(results: list, validation: dict, output_file: Path) -> None:
    """Generate migration report"""
    report = {
        'migration_date': datetime.now().isoformat(),
        'summary': {
            'total_contacts': len(results),
            'migrated': sum(1 for r in results if r['status'] == 'migrated'),
            'no_change': sum(1 for r in results if r['status'] == 'no_change'),
            'skipped': sum(1 for r in results if r['status'] == 'skipped'),
            'errors': sum(1 for r in results if r['status'] == 'error')
        },
        'status_changes': {},
        'results': results,
        'validation': validation
    }
    
    # Count status changes
    for result in results:
        if result['status'] == 'migrated':
            old = result['old_status']
            new = result['new_status']
            key = f"{old} -> {new}"
            report['status_changes'][key] = report['status_changes'].get(key, 0) + 1
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nMigration report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Migrate networking contact statuses')
    parser.add_argument('--dry-run', action='store_true', help='Run without making changes')
    parser.add_argument('--backup-dir', type=str, help='Backup directory path')
    args = parser.parse_args()
    
    networking_dir = get_data_path('networking')
    
    if not networking_dir.exists():
        print(f"Error: Networking directory not found: {networking_dir}")
        return 1
    
    # Create backup directory
    if args.backup_dir:
        backup_dir = Path(args.backup_dir)
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = get_data_path(f'backups/networking_migration_{timestamp}')
    
    if args.dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No changes will be made")
        print("=" * 70)
    else:
        # Create backup
        create_backup(networking_dir, backup_dir)
        print(f"\nBackup created at: {backup_dir}\n")
    
    # Get all contact folders
    contact_folders = [f for f in networking_dir.iterdir() if f.is_dir()]
    print(f"Found {len(contact_folders)} contact folders\n")
    
    # Migrate contacts
    results = []
    for i, contact_folder in enumerate(contact_folders, 1):
        print(f"[{i}/{len(contact_folders)}] Processing {contact_folder.name}...", end=' ')
        result = migrate_contact(contact_folder, dry_run=args.dry_run)
        results.append(result)
        
        if result['status'] == 'migrated':
            print(f"✓ {result['old_status']} -> {result['new_status']}")
        elif result['status'] == 'no_change':
            print(f"- (no change: {result['old_status']})")
        elif result['status'] == 'skipped':
            print(f"⚠ Skipped: {result['reason']}")
        elif result['status'] == 'error':
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
    
    # Validate migration
    if not args.dry_run:
        validation = validate_migration(networking_dir)
        print(f"\nValidation Results:")
        print(f"  Valid: {validation['valid']}/{validation['total']}")
        print(f"  Invalid: {validation['invalid']}/{validation['total']}")
        
        if validation['errors']:
            print(f"\nErrors found:")
            for error in validation['errors'][:10]:  # Show first 10
                print(f"  - {error.get('contact', 'Unknown')}: {error.get('status', error.get('error', 'Unknown'))}")
            if len(validation['errors']) > 10:
                print(f"  ... and {len(validation['errors']) - 10} more")
    else:
        validation = {'total': len(contact_folders), 'valid': 0, 'invalid': 0, 'errors': []}
    
    # Generate report
    report_file = backup_dir / 'migration_report.json' if not args.dry_run else Path('migration_report_dryrun.json')
    generate_migration_report(results, validation, report_file)
    
    # Print summary
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    migrated = sum(1 for r in results if r['status'] == 'migrated')
    no_change = sum(1 for r in results if r['status'] == 'no_change')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    errors = sum(1 for r in results if r['status'] == 'error')
    
    print(f"Total contacts: {len(results)}")
    print(f"  Migrated: {migrated}")
    print(f"  No change needed: {no_change}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    
    if args.dry_run:
        print("\nThis was a DRY RUN. No changes were made.")
        print("Run without --dry-run to apply migration.")
    else:
        print(f"\nMigration complete! Backup saved to: {backup_dir}")
    
    return 0 if errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

