#!/usr/bin/env python3
"""
Historical badge calculation script.

Calculates badges retroactively for all existing networking contacts.

Usage:
    python scripts/calculate_historical_badges.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.badge_calculation_service import BadgeCalculationService


def main():
    """Calculate historical badges for all existing contacts"""
    print("=" * 70)
    print("Historical Badge Calculation")
    print("=" * 70)
    print()
    
    try:
        badge_service = BadgeCalculationService()
        
        print("Calculating badges for all existing contacts...")
        print("This may take a few moments...")
        print()
        
        # Calculate historical badges
        rewards_data = badge_service.calculate_historical_badges()
        
        # Print summary
        print()
        print("=" * 70)
        print("CALCULATION COMPLETE")
        print("=" * 70)
        print()
        print(f"Total Points: {rewards_data['total_points']}")
        print()
        print("Points by Category:")
        for category, points in rewards_data['points_by_category'].items():
            print(f"  {category.capitalize()}: {points} points")
        print()
        print("Badges Earned:")
        earned_count = 0
        for badge_id, badge_data in rewards_data['badges'].items():
            if badge_data['earned']:
                earned_count += 1
                badge_def = badge_service.badge_definitions[badge_id]
                print(f"  ✓ {badge_def['name']}: {badge_data['count']} (Required: {badge_data.get('required', 1)})")
        
        if earned_count == 0:
            print("  No badges earned yet.")
        
        print()
        print(f"Rewards data saved to: {badge_service.rewards_file}")
        print()
        print("=" * 70)
        
        return 0
    
    except Exception as e:
        import traceback
        print(f"Error calculating historical badges: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

