"""Analytics generation service for job application insights"""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
import re
from collections import Counter
from app.models.application import Application
from app.services.job_processor import JobProcessor
from app.utils.file_utils import get_data_path, read_text_file
from app.utils.location_normalizer import LocationNormalizer


class AnalyticsGenerator:
    """Generates analytics and insights from job applications"""
    
    def __init__(self):
        self.job_processor = JobProcessor()
        self.location_normalizer = LocationNormalizer()
    
    def get_applications_for_period(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Application]:
        """
        Load all applications within the specified date range.
        Filters by created_at date.
        """
        all_applications = self.job_processor.list_all_applications()
        
        period_applications = []
        for app in all_applications:
            # Normalize timezone for comparison
            app_created_at = app.created_at
            if app_created_at.tzinfo is None:
                # Assume EST if no timezone
                app_created_at = app_created_at.replace(tzinfo=timezone(timedelta(hours=-5)))
            
            if start_date <= app_created_at <= end_date:
                period_applications.append(app)
        
        return period_applications
    
    def _normalize_status(self, status: str) -> str:
        """Normalize status strings for consistent reporting"""
        if not status:
            return ''
        normalized = status.strip().lower()
        normalized = normalized.replace('–', '-').replace('—', '-')
        normalized = normalized.replace('  ', ' ')
        
        # Status normalization map
        status_map = {
            'contacted hiring manager': 'company response',
            'company response': 'company response',
            'interviewed': 'interview notes',
            'interview notes': 'interview notes',
            'interview follow up': 'interview - follow up',
            'interview follow-up': 'interview - follow up',
            'interview - follow up': 'interview - follow up',
        }
        
        return status_map.get(normalized, normalized)
    
    def compute_application_analytics(
        self,
        applications: List[Application]
    ) -> Dict:
        """
        Compute application analytics metrics:
        - Response rate
        - Interview conversion
        - Time to response
        - Success by match score
        - Best performing day/time
        """
        if not applications:
            return {
                'response_rate': 0.0,
                'interview_conversion': {},
                'time_to_response': {},
                'success_by_match_score': {},
                'best_performing_day_time': {}
            }
        
        # Filter to applications that have been applied (not just pending)
        applied_apps = []
        for app in applications:
            normalized_status = self._normalize_status(app.status)
            if normalized_status not in ['pending']:
                applied_apps.append(app)
        
        total_applied = len(applied_apps) if applied_apps else len(applications)
        if total_applied == 0:
            total_applied = len(applications)
        
        # 1. Response Rate: Applications with response_received checklist item checked
        apps_with_response = 0
        for app in applications:
            response_at = app.get_response_received_at()
            if response_at is not None:
                apps_with_response += 1
        
        response_rate = (apps_with_response / total_applied * 100) if total_applied > 0 else 0.0
        
        # 2. Interview Conversion: Track pipeline progression
        applied_count = 0
        responded_count = 0
        phone_screen_count = 0
        interview_count = 0
        offer_count = 0
        
        for app in applications:
            normalized_status = self._normalize_status(app.status)
            
            # Count applied (not pending)
            if normalized_status != 'pending':
                applied_count += 1
            
            # Count responded (has response_received checked or company response status)
            if app.get_response_received_at() is not None or normalized_status == 'company response':
                responded_count += 1
            
            # Count phone screen / scheduled interview
            if normalized_status in ['scheduled interview', 'interview notes', 'interview - follow up']:
                phone_screen_count += 1
                interview_count += 1
            elif normalized_status == 'company response':
                phone_screen_count += 1
            
            # Count interviews (more specific)
            if normalized_status in ['interview notes', 'interview - follow up', 'scheduled interview']:
                interview_count += 1
            
            # Count offers
            if normalized_status == 'offered':
                offer_count += 1
        
        interview_conversion = {
            'applied': applied_count,
            'responded': responded_count,
            'phone_screen': phone_screen_count,
            'interview': interview_count,
            'offer': offer_count,
            'response_rate': (responded_count / applied_count * 100) if applied_count > 0 else 0.0,
            'phone_screen_rate': (phone_screen_count / responded_count * 100) if responded_count > 0 else 0.0,
            'interview_rate': (interview_count / phone_screen_count * 100) if phone_screen_count > 0 else 0.0,
            'offer_rate': (offer_count / interview_count * 100) if interview_count > 0 else 0.0
        }
        
        # 3. Time to Response: Days from applied to response_received
        response_times = []
        for app in applications:
            response_at = app.get_response_received_at()
            if response_at is not None:
                # Find when application was created or moved to "applied" status
                applied_date = app.created_at
                
                # If status was updated, use that as applied date
                if app.status_updated_at:
                    normalized_status = self._normalize_status(app.status)
                    # Try to find when it moved to "applied"
                    if normalized_status == 'applied':
                        applied_date = app.status_updated_at
                
                # Calculate days difference
                if isinstance(response_at, datetime) and isinstance(applied_date, datetime):
                    time_diff = response_at - applied_date
                    days = time_diff.total_seconds() / (24 * 3600)
                    if days >= 0:  # Only positive values
                        response_times.append(days)
        
        time_to_response = {
            'average_days': sum(response_times) / len(response_times) if response_times else 0.0,
            'median_days': sorted(response_times)[len(response_times) // 2] if response_times else 0.0,
            'min_days': min(response_times) if response_times else 0.0,
            'max_days': max(response_times) if response_times else 0.0,
            'count': len(response_times),
            'distribution': self._create_time_distribution(response_times)
        }
        
        # 4. Success by Match Score: Response/interview rates by score ranges
        score_ranges = [
            (0, 50, '0-50%'),
            (50, 70, '50-70%'),
            (70, 85, '70-85%'),
            (85, 100, '85-100%')
        ]
        
        success_by_match_score = {}
        for min_score, max_score, label in score_ranges:
            range_apps = [
                app for app in applications 
                if app.match_score is not None and min_score <= app.match_score < max_score
            ]
            
            if not range_apps:
                success_by_match_score[label] = {
                    'count': 0,
                    'response_rate': 0.0,
                    'interview_rate': 0.0
                }
                continue
            
            range_responded = sum(1 for app in range_apps if app.get_response_received_at() is not None)
            range_interviewed = sum(
                1 for app in range_apps 
                if self._normalize_status(app.status) in ['scheduled interview', 'interview notes', 'interview - follow up']
            )
            
            success_by_match_score[label] = {
                'count': len(range_apps),
                'response_rate': (range_responded / len(range_apps) * 100) if range_apps else 0.0,
                'interview_rate': (range_interviewed / len(range_apps) * 100) if range_apps else 0.0
            }
        
        # 5. Best Performing Day: Group by day of week only (not hour)
        day_stats = {}
        for app in applications:
            # Get creation time
            created = app.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone(timedelta(hours=-5)))
            
            day_of_week = created.strftime('%A')  # Monday, Tuesday, etc.
            
            # Check if this application got a response
            got_response = app.get_response_received_at() is not None
            
            if day_of_week not in day_stats:
                day_stats[day_of_week] = {
                    'total_applications': 0,
                    'responses': 0
                }
            
            day_stats[day_of_week]['total_applications'] += 1
            if got_response:
                day_stats[day_of_week]['responses'] += 1
        
        # Calculate response rates for each day (order: Monday-Sunday)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        best_performing_day = {}
        for day in day_order:
            if day in day_stats:
                stats = day_stats[day]
                response_rate = (stats['responses'] / stats['total_applications'] * 100) if stats['total_applications'] > 0 else 0.0
                best_performing_day[day] = {
                    'total_applications': stats['total_applications'],
                    'responses': stats['responses'],
                    'response_rate': round(response_rate, 2)
                }
        
        return {
            'response_rate': round(response_rate, 2),
            'interview_conversion': interview_conversion,
            'time_to_response': time_to_response,
            'success_by_match_score': success_by_match_score,
            'best_performing_day': best_performing_day
        }
    
    def _create_time_distribution(self, response_times: List[float]) -> Dict:
        """Create distribution buckets for response times"""
        if not response_times:
            return {}
        
        buckets = {
            '0-1 days': 0,
            '2-3 days': 0,
            '4-7 days': 0,
            '8-14 days': 0,
            '15-30 days': 0,
            '30+ days': 0
        }
        
        for days in response_times:
            if days <= 1:
                buckets['0-1 days'] += 1
            elif days <= 3:
                buckets['2-3 days'] += 1
            elif days <= 7:
                buckets['4-7 days'] += 1
            elif days <= 14:
                buckets['8-14 days'] += 1
            elif days <= 30:
                buckets['15-30 days'] += 1
            else:
                buckets['30+ days'] += 1
        
        return buckets
    
    def compute_trend_analysis(
        self,
        applications: List[Application]
    ) -> Dict:
        """
        Compute trend analysis:
        - Application velocity (over time)
        - Status distribution
        - Company type analysis
        - Location insights
        - Salary range tracking
        """
        if not applications:
            return {
                'application_velocity': {},
                'status_distribution': {},
                'company_type_analysis': {},
                'location_insights': {},
                'salary_tracking': {}
            }
        
        # 1. Application Velocity: Applications created per day/week
        daily_velocity = {}
        weekly_velocity = {}
        
        for app in applications:
            created = app.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone(timedelta(hours=-5)))
            
            # Daily grouping
            date_key = created.strftime('%Y-%m-%d')
            daily_velocity[date_key] = daily_velocity.get(date_key, 0) + 1
            
            # Weekly grouping (ISO week)
            year, week, _ = created.isocalendar()
            week_key = f"{year}-W{week:02d}"
            weekly_velocity[week_key] = weekly_velocity.get(week_key, 0) + 1
        
        # Calculate cumulative daily velocity
        daily_list = sorted([{'date': k, 'count': v} for k, v in daily_velocity.items()], key=lambda x: x['date'])
        cumulative_count = 0
        daily_with_cumulative = []
        for day in daily_list:
            cumulative_count += day['count']
            daily_with_cumulative.append({
                'date': day['date'],
                'count': day['count'],
                'cumulative': cumulative_count
            })
        
        application_velocity = {
            'daily': daily_list,
            'daily_cumulative': daily_with_cumulative,
            'weekly': sorted([{'week': k, 'count': v} for k, v in weekly_velocity.items()], key=lambda x: x['week'])
        }
        
        # 2. Status Distribution: Count by status
        status_distribution = {}
        for app in applications:
            normalized_status = self._normalize_status(app.status)
            status_distribution[normalized_status] = status_distribution.get(normalized_status, 0) + 1
        
        # 3. Company Type Analysis: Response/interview rates by company type
        company_type_stats = {}
        for app in applications:
            company_type = app.company_type or 'unknown'
            
            if company_type not in company_type_stats:
                company_type_stats[company_type] = {
                    'total': 0,
                    'responses': 0,
                    'interviews': 0,
                    'offers': 0
                }
            
            company_type_stats[company_type]['total'] += 1
            
            # Check if got response
            if app.get_response_received_at() is not None:
                company_type_stats[company_type]['responses'] += 1
            
            # Check if interviewed
            normalized_status = self._normalize_status(app.status)
            if normalized_status in ['scheduled interview', 'interview notes', 'interview - follow up']:
                company_type_stats[company_type]['interviews'] += 1
            
            # Check if offered
            if normalized_status == 'offered':
                company_type_stats[company_type]['offers'] += 1
        
        # Calculate rates
        company_type_analysis = {}
        for company_type, stats in company_type_stats.items():
            company_type_analysis[company_type] = {
                'total': stats['total'],
                'response_rate': (stats['responses'] / stats['total'] * 100) if stats['total'] > 0 else 0.0,
                'interview_rate': (stats['interviews'] / stats['total'] * 100) if stats['total'] > 0 else 0.0,
                'offer_rate': (stats['offers'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
            }
        
        # 4. Location Insights: Response rates by location
        # Use location normalizer for consistent formatting and metropolitan area grouping
        # Better handle N/A by checking job descriptions for remote indicators
        # Remove work type from locations (Remote/Hybrid) - track separately
        location_stats = {}
        work_type_stats = {
            'Remote': {'total': 0, 'responses': 0, 'interviews': 0},
            'Hybrid': {'total': 0, 'responses': 0, 'interviews': 0},
            'On-site': {'total': 0, 'responses': 0, 'interviews': 0}
        }
        
        for app in applications:
            location = app.location or ''
            
            # Get job description text for better N/A handling
            job_description_text = None
            if app.job_description_path and app.job_description_path.exists():
                try:
                    job_description_text = read_text_file(app.job_description_path)
                except Exception:
                    pass
            
            # Extract work type (separate from location)
            work_type = self.location_normalizer.extract_work_type(location, job_description_text)
            work_type_stats[work_type]['total'] += 1
            
            # Track responses and interviews by work type
            if app.get_response_received_at() is not None:
                work_type_stats[work_type]['responses'] += 1
            normalized_status = self._normalize_status(app.status)
            if normalized_status in ['scheduled interview', 'interview notes', 'interview - follow up']:
                work_type_stats[work_type]['interviews'] += 1
            
            # Normalize location using LocationNormalizer (with job description for N/A handling)
            # Group by state/province/country for Location Insights
            # Remove work type from location (Remote locations will be None and skipped)
            normalized_location = self.location_normalizer.normalize(
                location, job_description_text, 
                group_by_region=True, 
                remove_work_type=True
            )
            
            # Skip if normalization returns None (invalid/empty location or Remote)
            if not normalized_location:
                continue
            
            if normalized_location not in location_stats:
                location_stats[normalized_location] = {
                    'total': 0,
                    'responses': 0,
                    'interviews': 0
                }
            
            location_stats[normalized_location]['total'] += 1
            
            # Check if got response
            if app.get_response_received_at() is not None:
                location_stats[normalized_location]['responses'] += 1
            
            # Check if interviewed
            normalized_status = self._normalize_status(app.status)
            if normalized_status in ['scheduled interview', 'interview notes', 'interview - follow up']:
                location_stats[normalized_location]['interviews'] += 1
        
        # Calculate rates
        location_insights_list = []
        for location, stats in location_stats.items():
            response_rate = (stats['responses'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
            interview_rate = (stats['interviews'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
            location_insights_list.append({
                'location': location,
                'total': stats['total'],
                'response_rate': response_rate,
                'interview_rate': interview_rate
            })
        
        # Sort by response rate descending
        location_insights_list.sort(key=lambda x: x['response_rate'], reverse=True)
        
        # Convert back to dict for compatibility
        location_insights = {}
        for item in location_insights_list:
            location_insights[item['location']] = {
                'total': item['total'],
                'response_rate': item['response_rate'],
                'interview_rate': item['interview_rate']
            }
        
        # 4.5. Work Type Distribution: Remote, Hybrid, On-site
        work_type_distribution = {}
        for work_type, stats in work_type_stats.items():
            if stats['total'] > 0:
                response_rate = (stats['responses'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
                interview_rate = (stats['interviews'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
                work_type_distribution[work_type] = {
                    'total': stats['total'],
                    'response_rate': response_rate,
                    'interview_rate': interview_rate
                }
        
        # 5. Salary Range Tracking: Extract and analyze salary data
        salary_ranges = []
        salary_values = []
        
        for app in applications:
            if app.salary_range:
                # Try to extract numeric values from salary range
                # Format might be "$120,000 - $150,000" or "$100k - $150k"
                import re
                # Extract all numbers
                numbers = re.findall(r'\$?(\d+(?:,\d+)*(?:k|K)?)', app.salary_range)
                if numbers:
                    for num_str in numbers:
                        # Remove commas and convert k to thousands
                        num_str = num_str.replace(',', '')
                        if num_str.lower().endswith('k'):
                            value = float(num_str[:-1]) * 1000
                        else:
                            try:
                                value = float(num_str)
                            except:
                                continue
                        
                        if 20000 <= value <= 500000:  # Reasonable salary range
                            salary_values.append(value)
                    
                    # If we got two numbers, average them
                    if len(numbers) >= 2:
                        try:
                            num1 = numbers[0].replace(',', '').lower().rstrip('k')
                            num2 = numbers[1].replace(',', '').lower().rstrip('k')
                            val1 = float(num1) * (1000 if numbers[0].lower().endswith('k') else 1)
                            val2 = float(num2) * (1000 if numbers[1].lower().endswith('k') else 1)
                            avg = (val1 + val2) / 2
                            if 20000 <= avg <= 500000:
                                salary_ranges.append({
                                    'range': app.salary_range,
                                    'average': avg,
                                    'min': val1,
                                    'max': val2
                                })
                        except:
                            pass
        
        # Calculate salary statistics
        salary_tracking = {
            'count': len(salary_ranges),
            'average_salary': sum(s['average'] for s in salary_ranges) / len(salary_ranges) if salary_ranges else 0.0,
            'median_salary': sorted([s['average'] for s in salary_ranges])[len(salary_ranges) // 2] if salary_ranges else 0.0,
            'min_salary': min([s['min'] for s in salary_ranges]) if salary_ranges else 0.0,
            'max_salary': max([s['max'] for s in salary_ranges]) if salary_ranges else 0.0,
            'distribution': self._create_salary_distribution([s['average'] for s in salary_ranges])
        }
        
        return {
            'application_velocity': application_velocity,
            'status_distribution': status_distribution,
            'company_type_analysis': company_type_analysis,
            'location_insights': location_insights,
            'work_type_distribution': work_type_distribution,
            'salary_tracking': salary_tracking
        }
    
    def _create_salary_distribution(self, salaries: List[float]) -> Dict:
        """Create distribution buckets for salaries (ordered ascending)"""
        if not salaries:
            return {}
        
        buckets = {
            '$0-50k': 0,
            '$50k-75k': 0,
            '$75k-100k': 0,
            '$100k-125k': 0,
            '$125k-150k': 0,
            '$150k-200k': 0,
            '$200k-220k': 0,
            '$220k-230k': 0,
            '$230k-250k': 0,
            '$250k-270k': 0,
            '$270k-300k': 0,
            '$300k+': 0
        }
        
        for salary in salaries:
            if salary < 50000:
                buckets['$0-50k'] += 1
            elif salary < 75000:
                buckets['$50k-75k'] += 1
            elif salary < 100000:
                buckets['$75k-100k'] += 1
            elif salary < 125000:
                buckets['$100k-125k'] += 1
            elif salary < 150000:
                buckets['$125k-150k'] += 1
            elif salary < 200000:
                buckets['$150k-200k'] += 1
            elif salary < 220000:
                buckets['$200k-220k'] += 1
            elif salary < 230000:
                buckets['$220k-230k'] += 1
            elif salary < 250000:
                buckets['$230k-250k'] += 1
            elif salary < 270000:
                buckets['$250k-270k'] += 1
            elif salary < 300000:
                buckets['$270k-300k'] += 1
            else:
                buckets['$300k+'] += 1
        
        # Return ordered dictionary (ascending by key)
        ordered_buckets = {}
        bucket_order = [
            '$0-50k', '$50k-75k', '$75k-100k', '$100k-125k', '$125k-150k',
            '$150k-200k', '$200k-220k', '$220k-230k', '$230k-250k',
            '$250k-270k', '$270k-300k', '$300k+'
        ]
        for key in bucket_order:
            if key in buckets:
                ordered_buckets[key] = buckets[key]
        
        return ordered_buckets
    
    def _extract_skills_from_qualifications(self, application: Application) -> Dict[str, List[str]]:
        """
        Extract skills from qualification file for an application.
        Returns dict with 'requested' (all skills from job), 'matched' (skills I have), and 'missing' (gaps).
        """
        skills_data = {
            'requested': [],
            'matched': [],
            'missing': []
        }
        
        # Check if skills are cached in application metadata
        if application.extracted_skills:
            # If cached, we need to parse qualification file to get all skills
            # For now, parse the file
            pass
        
        if not application.qualifications_path or not application.qualifications_path.exists():
            return skills_data
        
        try:
            qual_content = read_text_file(application.qualifications_path)
            
            # Extract strong matches from comma-separated list format only
            # Format: "- Strong Matches: Skill1, Skill2, Skill3" (not from tables)
            strong_matches_patterns = [
                r'(?:^|\n)[-*]\s*Strong Matches:?\s*([^\n]+?)(?=\n[-*]|\n\n|\n##|\*\*|$)',
                r'\*\*Strong Matches:\*\*\s*([^\n]+?)(?=\n[-*]|\n\n|\n##|\*\*|$)'
            ]
            
            for pattern in strong_matches_patterns:
                match = re.search(pattern, qual_content, re.MULTILINE | re.IGNORECASE)
                if match:
                    matches_text = match.group(1).strip()
                    # Skip if it looks like a table or contains pipes
                    if '|' in matches_text:
                        continue
                    
                    # This should be a comma-separated list of skill names
                    # Split by comma and clean up
                    skills = re.split(r'[,;]', matches_text)
                    for skill in skills:
                        skill = skill.strip().strip('-').strip('*').strip()
                        # Skip headers, placeholders, and full sentences
                        # Only accept clean skill names (short, no quotes, reasonable length)
                        if (skill and len(skill) > 2 and len(skill) < 80 and 
                            not skill.isdigit() and
                            not any(header in skill.lower() for header in [
                                'none mentioned', 'skill', 'job requirement', 'resume evidence', 'match level',
                                'header', 'placeholder', 'strong match', 'partial match', 'no match',
                                'not found in resume', 'important tools', 'none'
                            ]) and
                            skill.lower() not in ['match', 'level', 'evidence', 'requirement'] and
                            # Skip if it looks like a full sentence (contains quotes, too many words)
                            not ('"' in skill) and not (len(skill.split()) > 10)):
                            if skill not in skills_data['matched']:
                                skills_data['matched'].append(skill)
                    # If we found matches, break (use first pattern that matches)
                    if skills_data['matched']:
                        break
            
            # Extract missing skills from comma-separated list format only
            # Format: "- Missing Skills: Skill1, Skill2, Skill3" or "- Missing Skills: None mentioned"
            missing_skills_patterns = [
                r'(?:^|\n)[-*]\s*Missing Skills:?\s*([^\n]+?)(?=\n[-*]|\n\n|\n##|\*\*|$)',
                r'\*\*Missing Skills:\*\*\s*([^\n]+?)(?=\n[-*]|\n\n|\n##|\*\*|$)'
            ]
            
            for pattern in missing_skills_patterns:
                match = re.search(pattern, qual_content, re.MULTILINE | re.IGNORECASE)
                if match:
                    missing_text = match.group(1).strip()
                    # Skip if it says "None mentioned" or similar
                    if re.match(r'^(none mentioned|n/a|na|no missing)', missing_text, re.IGNORECASE):
                        break
                    
                    # Skip if it looks like a table or contains pipes
                    if '|' in missing_text:
                        continue
                    
                    # This should be a comma-separated list of skill names
                    skills = re.split(r'[,;]', missing_text)
                    for skill in skills:
                        skill = skill.strip().strip('-').strip('*').strip()
                        # Skip headers, placeholders, and full sentences
                        # Only accept clean skill names
                        if (skill and len(skill) > 2 and len(skill) < 80 and 
                            not skill.isdigit() and
                            not any(header in skill.lower() for header in [
                                'none mentioned', 'skill', 'job requirement', 'resume evidence', 'match level',
                                'header', 'placeholder', 'strong match', 'partial match', 'no match',
                                'not found in resume', 'important tools', 'none'
                            ]) and
                            skill.lower() not in ['match', 'level', 'evidence', 'requirement'] and
                            # Skip if it looks like a full sentence
                            not ('"' in skill) and not (len(skill.split()) > 10)):
                            if skill not in skills_data['missing']:
                                skills_data['missing'].append(skill)
                    # If we found matches, break
                    if skills_data['missing']:
                        break
            
            # All requested skills = matched + missing
            skills_data['requested'] = skills_data['matched'] + skills_data['missing']
            
        except Exception as e:
            # If parsing fails, return empty data
            pass
        
        return skills_data
    
    def compute_skills_gap_analysis(
        self,
        applications: List[Application],
        gap_period: str = 'all'  # 'daily', 'weekly', 'monthly', 'all'
    ) -> Dict:
        """
        Compute skills gap analysis:
        - Most requested skills
        - Your skill gaps
        - Learning priorities
        - Skill match trends
        """
        if not applications:
            return {
                'most_requested_skills': [],
                'skill_gaps': [],
                'skills_overlap': {
                    'distribution': {},
                    'unique_skills_count': 0,
                    'unique_skills': [],
                    'common_requested_skills': [],
                    'common_unmatched_skills': []
                },
                'learning_priorities': [],
                'skill_match_trends': {}
            }
        
        # Extract skills from all applications
        all_requested_skills = []
        all_missing_skills = []
        skill_frequency = Counter()
        missing_skill_frequency = Counter()
        skill_to_match_scores = {}  # Track which skills appear with which match scores
        skill_to_apps = {}  # Track which applications have each skill (with details)
        missing_skill_to_apps = {}  # Track which applications are missing each skill (with details)
        skill_to_job_count = {}  # Track how many jobs each skill appears in
        
        for app in applications:
            skills_data = self._extract_skills_from_qualifications(app)
            
            # Build application info for links
            app_info = {
                'id': app.id,
                'company': app.company,
                'job_title': app.job_title,
                'url': self._get_application_url(app)
            }
            
            # Track unique skills per application for overlap analysis
            app_skill_set = set(skills_data['requested'])
            
            # Count requested skills
            for skill in skills_data['requested']:
                skill_frequency[skill] += 1
                if skill not in skill_to_match_scores:
                    skill_to_match_scores[skill] = []
                if app.match_score:
                    skill_to_match_scores[skill].append(app.match_score)
                # Track applications for this skill
                if skill not in skill_to_apps:
                    skill_to_apps[skill] = []
                skill_to_apps[skill].append(app_info)
            
            # Track which skills appear in how many jobs (unique applications per skill)
            for skill in app_skill_set:
                if skill not in skill_to_job_count:
                    skill_to_job_count[skill] = set()  # Use set to avoid duplicates
                skill_to_job_count[skill].add(app.id)  # Track unique app IDs
            
            # Count missing skills (gaps)
            for skill in skills_data['missing']:
                missing_skill_frequency[skill] += 1
                all_missing_skills.append(skill)
                # Track applications missing this skill
                if skill not in missing_skill_to_apps:
                    missing_skill_to_apps[skill] = []
                missing_skill_to_apps[skill].append(app_info)
            
            all_requested_skills.extend(skills_data['requested'])
        
        # 1. Most Requested Skills: Top 20 skills appearing in job descriptions
        most_requested_skills = []
        for skill, count in skill_frequency.most_common(20):
            # Filter out header-like entries
            skill_lower = skill.lower()
            if any(header in skill_lower for header in [
                'skill', 'job requirement', 'resume evidence', 'match level',
                '---', 'header', 'placeholder'
            ]):
                continue
            avg_match_score = sum(skill_to_match_scores.get(skill, [0])) / len(skill_to_match_scores.get(skill, [1])) if skill_to_match_scores.get(skill) else 0.0
            most_requested_skills.append({
                'skill': skill,
                'frequency': count,
                'percentage': (count / len(applications) * 100) if applications else 0.0,
                'average_match_score': round(avg_match_score, 1),
                'applications': skill_to_apps.get(skill, [])[:10]  # Limit to 10 for tooltip
            })
        
        # 2. Skill Gaps: Skills appearing in 3+ jobs that I don't have
        # Filter by time period if specified (daily, weekly, monthly, or all)
        filtered_applications = applications
        if gap_period != 'all':
            # Get the most recent period based on gap_period
            now = datetime.now(timezone(timedelta(hours=-5)))
            if gap_period == 'daily':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif gap_period == 'weekly':
                # Get start of current week (Monday)
                days_since_monday = now.weekday()
                start_date = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif gap_period == 'monthly':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = None
            
            if start_date:
                filtered_applications = [app for app in applications if app.created_at >= start_date]
        
        # Calculate skill gaps for filtered applications
        filtered_missing_freq = Counter()
        filtered_missing_to_apps = {}
        
        for app in filtered_applications:
            skills_data = self._extract_skills_from_qualifications(app)
            app_info = {
                'id': app.id,
                'company': app.company,
                'job_title': app.job_title,
                'url': self._get_application_url(app)
            }
            
            for skill in skills_data['missing']:
                filtered_missing_freq[skill] += 1
                if skill not in filtered_missing_to_apps:
                    filtered_missing_to_apps[skill] = []
                filtered_missing_to_apps[skill].append(app_info)
        
        # Overall skill gaps (appearing in 1+ jobs for filtered period, 3+ for all time)
        skill_gaps = []
        for skill, count in missing_skill_frequency.items():
            if count >= 3:  # Appeared in at least 3 jobs
                # Calculate average match score impact
                avg_score_with = sum(skill_to_match_scores.get(skill, [])) / len(skill_to_match_scores.get(skill, [1])) if skill_to_match_scores.get(skill) else 0.0
                skill_gaps.append({
                    'skill': skill,
                    'frequency': count,
                    'percentage': (count / len(applications) * 100) if applications else 0.0,
                    'average_match_score_impact': round(avg_score_with, 1),
                    'applications': missing_skill_to_apps.get(skill, [])[:10]  # Limit to 10 for tooltip
                })
        
        # Sort by frequency and match score impact
        skill_gaps.sort(key=lambda x: (x['frequency'], x['average_match_score_impact']), reverse=True)
        
        # 2.5. Skills Overlap Analysis: Common vs Unique skills
        # Count how many unique jobs each skill appears in
        skill_job_count = {skill: len(app_ids) for skill, app_ids in skill_to_job_count.items()}
        
        # Track unmatched skills job count (skills that appear in missing_skill_frequency)
        unmatched_skill_job_count = {}
        for skill, count in missing_skill_frequency.items():
            # Get unique app IDs for this unmatched skill
            app_ids_for_unmatched = set()
            for app in applications:
                skills_data = self._extract_skills_from_qualifications(app)
                if skill in skills_data['missing']:
                    app_ids_for_unmatched.add(app.id)
            if app_ids_for_unmatched:
                unmatched_skill_job_count[skill] = len(app_ids_for_unmatched)
        
        # Group skills by how many jobs they appear in
        overlap_distribution = Counter()  # Key: number of jobs, Value: count of skills
        unique_skills = []  # Skills appearing in only 1 job
        common_requested_skills_data = []  # Requested skills appearing in 2+ jobs
        common_unmatched_skills_data = []  # Unmatched skills appearing in 2+ jobs
        
        # Create a map from app_id to app_info for quick lookup
        app_id_to_info = {}
        for app in applications:
            app_id_to_info[app.id] = {
                'id': app.id,
                'company': app.company,
                'job_title': app.job_title,
                'url': self._get_application_url(app)
            }
        
        for skill, job_count in skill_job_count.items():
            # Filter out header-like entries
            skill_lower = skill.lower()
            if any(header in skill_lower for header in [
                'skill', 'job requirement', 'resume evidence', 'match level',
                '---', 'header', 'placeholder'
            ]):
                continue
            
            overlap_distribution[job_count] += 1
            
            if job_count == 1:
                # Unique skill - appears in only one job
                app_ids = skill_to_job_count[skill]
                app_id = list(app_ids)[0] if app_ids else None
                unique_skills.append({
                    'skill': skill,
                    'application': app_id_to_info.get(app_id) if app_id else None
                })
            else:
                # Common requested skill - appears in multiple jobs
                app_ids = skill_to_job_count[skill]
                app_infos = [app_id_to_info.get(aid) for aid in list(app_ids)[:10] if app_id_to_info.get(aid)]
                avg_match_score = sum(skill_to_match_scores.get(skill, [0])) / len(skill_to_match_scores.get(skill, [1])) if skill_to_match_scores.get(skill) else 0.0
                common_requested_skills_data.append({
                    'skill': skill,
                    'job_count': job_count,
                    'percentage': (job_count / len(applications) * 100) if applications else 0.0,
                    'average_match_score': round(avg_match_score, 1),
                    'applications': app_infos  # Limit to 10
                })
        
        # Process unmatched skills
        for skill, job_count in unmatched_skill_job_count.items():
            # Filter out header-like entries
            skill_lower = skill.lower()
            if any(header in skill_lower for header in [
                'skill', 'job requirement', 'resume evidence', 'match level',
                '---', 'header', 'placeholder'
            ]):
                continue
            
            if job_count >= 2:  # Common unmatched skill - appears in 2+ jobs
                # Get app infos for this unmatched skill
                app_infos_for_unmatched = []
                for app in applications:
                    skills_data = self._extract_skills_from_qualifications(app)
                    if skill in skills_data['missing']:
                        app_infos_for_unmatched.append(app_id_to_info.get(app.id))
                        if len(app_infos_for_unmatched) >= 10:
                            break
                
                # Calculate average match score impact for unmatched skills
                avg_score_with = sum(skill_to_match_scores.get(skill, [])) / len(skill_to_match_scores.get(skill, [1])) if skill_to_match_scores.get(skill) else 0.0
                common_unmatched_skills_data.append({
                    'skill': skill,
                    'job_count': job_count,
                    'percentage': (job_count / len(applications) * 100) if applications else 0.0,
                    'average_match_score_impact': round(avg_score_with, 1),
                    'applications': [a for a in app_infos_for_unmatched if a]  # Filter out None values
                })
        
        # Sort unique skills alphabetically
        unique_skills.sort(key=lambda x: x['skill'].lower())
        
        # Sort common requested skills by job count
        common_requested_skills_data.sort(key=lambda x: (x['job_count'], x['average_match_score']), reverse=True)
        
        # Sort common unmatched skills by job count
        common_unmatched_skills_data.sort(key=lambda x: (x['job_count'], x['average_match_score_impact']), reverse=True)
        
        # 3. Learning Priorities: Top 20 gaps sorted by frequency * match score impact
        learning_priorities = []
        for gap in skill_gaps[:20]:  # Take top 20 gaps
            priority_score = gap['frequency'] * (gap['average_match_score_impact'] / 100.0)
            learning_priorities.append({
                'skill': gap['skill'],
                'frequency': gap['frequency'],
                'priority_score': round(priority_score, 2),
                'reason': f"Appears in {gap['frequency']} job{'s' if gap['frequency'] > 1 else ''} with avg match score impact of {gap['average_match_score_impact']:.1f}%",
                'applications': gap.get('applications', [])  # Include application links
            })
        
        learning_priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        learning_priorities = learning_priorities[:20]  # Top 20
        
        # 4. Skill Match Trends: Average match score over time (weekly), color coded by top 10 skills
        # Use top 10 skills for readability (best practice: limit to 5-10 categories for grouped bars)
        top_skills = [s['skill'] for s in most_requested_skills[:10]]
        
        # Group applications by week and track match scores by skill presence
        weekly_scores = {}
        weekly_scores_by_skill = {skill: {} for skill in top_skills}
        weekly_scores_other = {}
        skill_week_to_apps = {skill: {} for skill in top_skills}  # Track apps per skill per week
        
        for app in applications:
            if app.match_score is None:
                continue
            
            created = app.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone(timedelta(hours=-5)))
            
            # Get ISO week: YYYY-Www format (e.g., 2025-W03)
            year, week, _ = created.isocalendar()
            week_key = f"{year}-W{week:02d}"
            
            # Track overall scores
            if week_key not in weekly_scores:
                weekly_scores[week_key] = []
            weekly_scores[week_key].append(app.match_score)
            
            # Build application info
            app_info = {
                'id': app.id,
                'company': app.company,
                'job_title': app.job_title,
                'url': self._get_application_url(app)
            }
            
            # Get skills for this application
            app_skills = self._extract_skills_from_qualifications(app)
            app_requested_skills = [s.lower() for s in app_skills['requested']]
            
            # Check which top skills are in this application
            found_top_skill = False
            for skill in top_skills:
                skill_lower = skill.lower()
                # Check if this skill appears in the job description for this app
                if any(skill_lower in req_skill.lower() or req_skill.lower() in skill_lower 
                       for req_skill in app_requested_skills):
                    if week_key not in weekly_scores_by_skill[skill]:
                        weekly_scores_by_skill[skill][week_key] = []
                    weekly_scores_by_skill[skill][week_key].append(app.match_score)
                    # Track applications for this skill/week
                    if week_key not in skill_week_to_apps[skill]:
                        skill_week_to_apps[skill][week_key] = []
                    skill_week_to_apps[skill][week_key].append(app_info)
                    found_top_skill = True
            
            # If no top skill found, add to "other"
            if not found_top_skill:
                if week_key not in weekly_scores_other:
                    weekly_scores_other[week_key] = []
                weekly_scores_other[week_key].append(app.match_score)
        
        # Build trend data with top 10 skills and "other"
        skill_match_trends = {
            'overall': {},
            'by_skill': {},
            'other': {}
        }
        
        # Calculate overall averages per week (only include weeks with data)
        for week, scores in sorted(weekly_scores.items()):
            if scores and len(scores) > 0:  # Only include weeks with actual data
                skill_match_trends['overall'][week] = {
                    'average_score': round(sum(scores) / len(scores), 1),
                    'count': len(scores)
                }
        
        # Calculate averages per skill per week (only include weeks with data)
        for skill in top_skills:
            skill_match_trends['by_skill'][skill] = {}
            for week, scores in sorted(weekly_scores_by_skill[skill].items()):
                if scores and len(scores) > 0:  # Only include weeks with actual data
                    skill_match_trends['by_skill'][skill][week] = {
                        'average_score': round(sum(scores) / len(scores), 1),
                        'count': len(scores),
                        'applications': skill_week_to_apps[skill].get(week, [])[:5]  # Limit to 5 apps per week
                    }
        
        # Calculate "other" averages per week (only include weeks with data)
        for week, scores in sorted(weekly_scores_other.items()):
            if scores and len(scores) > 0:  # Only include weeks with actual data
                skill_match_trends['other'][week] = {
                    'average_score': round(sum(scores) / len(scores), 1),
                    'count': len(scores)
                }
        
        return {
            'most_requested_skills': most_requested_skills[:20],  # Top 20
            'skill_gaps': skill_gaps[:20],  # Top 20 gaps (used for "Most Unmatched Skills")
            'gap_period': gap_period,  # Include the period used for filtering
            'skills_overlap': {
                'distribution': dict(sorted(overlap_distribution.items())),  # {job_count: skill_count}
                'unique_skills_count': len(unique_skills),
                'unique_skills': unique_skills[:50],  # Top 50 unique skills
                'common_requested_skills': common_requested_skills_data[:50],  # Top 50 common requested skills
                'common_unmatched_skills': common_unmatched_skills_data[:50]  # Top 50 common unmatched skills
            },
            'learning_priorities': learning_priorities[:20],  # Top 20 priorities
            'skill_match_trends': skill_match_trends
        }
    
    def _group_applications_by_period(self, applications: List[Application], period: str) -> Dict[str, List[Application]]:
        """Group applications by time period (daily, weekly, monthly)"""
        grouped = {}
        
        for app in applications:
            created = app.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone(timedelta(hours=-5)))
            
            if period == 'daily':
                period_key = created.strftime('%Y-%m-%d')
            elif period == 'weekly':
                year, week, _ = created.isocalendar()
                period_key = f"{year}-W{week:02d}"
            elif period == 'monthly':
                period_key = created.strftime('%Y-%m')
            else:
                period_key = 'all'
            
            if period_key not in grouped:
                grouped[period_key] = []
            grouped[period_key].append(app)
        
        return grouped
    
    def _get_application_url(self, application: Application) -> str:
        """Generate URL to view application summary"""
        if application.summary_path and application.summary_path.exists():
            # URL format: /applications/{folder_name}/{summary_filename}
            folder_name = application.folder_path.name if application.folder_path else application.id
            summary_filename = application.summary_path.name
            return f"/applications/{folder_name}/{summary_filename}"
        elif application.folder_path:
            # Fallback: link to folder
            folder_name = application.folder_path.name
            return f"/applications/{folder_name}/"
        else:
            # Last resort: use application ID
            return f"/api/applications/{application.id}"
    
    def generate_analytics(
        self,
        period: str = '30days',
        gap_period: str = 'all'
    ) -> Dict:
        """
        Generate comprehensive analytics for a specified period.
        
        Args:
            period: One of 'today', '7days', '30days', 'all'
        
        Returns:
            Dictionary with all analytics data
        """
        # Calculate date range based on period
        now = datetime.now(timezone(timedelta(hours=-5)))  # EST
        
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == '7days':
            start_date = now - timedelta(days=7)
            end_date = now
        elif period == '30days':
            start_date = now - timedelta(days=30)
            end_date = now
        elif period == 'all':
            start_date = datetime(2020, 1, 1, tzinfo=timezone(timedelta(hours=-5)))
            end_date = now
        else:
            # Default to 30 days
            start_date = now - timedelta(days=30)
            end_date = now
        
        # Get applications for period
        applications = self.get_applications_for_period(start_date, end_date)
        
        # Compute all analytics
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_applications': len(applications),
            'application_analytics': self.compute_application_analytics(applications),
            'trend_analysis': self.compute_trend_analysis(applications),
            'skills_gap_analysis': self.compute_skills_gap_analysis(applications, gap_period)
        }

