/**
 * Demo Data for Hunter Application
 * All data is hardcoded for static HTML demo version
 */

// Company name mappings
const COMPANY_MAPPINGS = {
    'Capital Finance Firm': 'Capital Finance Firm',
    'Handy repairs': 'Handy repairs',
    'Hitech co': 'Hitech co',
    'Superstars': 'Superstars',
    'Mortgage-Co': 'Mortgage Co',
    'Fintech A co': 'Fintech A co',
    'Fintect B Co': 'Fintect B Co',
    'Global a co': 'Global a co',
    'JustTest': 'JustTest',
    'Medical Network Co': 'Medical Network Co',
    'Fortune500 Bank': 'Fortune500 Bank',
    'Capital Credit Card': 'Capital Credit Card',
    'Healthcare Company': 'Healthcare Company',
    'TechPassword-Co': 'TechPassword Co'
};

// Helper to get demo dates (last 5 days)
function getDemoDates() {
    const dates = [];
    for (let i = 0; i < 5; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dates.push(date.toISOString().split('T')[0]);
    }
    return dates;
}

// Applications for App Dash (9 tiles)
const DEMO_APPLICATIONS = [
    {
        id: 'capital-finance-firm-001',
        company: 'Capital Finance Firm',
        job_title: 'Senior Software Engineer',
        status: 'applied',
        match_score: 85,
        applied_at: '2025-12-15T10:30:00',
        updated_at: '2025-12-18T14:20:00',
        location: 'New York, NY',
        salary_range: '$120,000 - $150,000',
        folder_name: 'Capital-Finance-Firm-SeniorSoftwareEngineer'
    },
    {
        id: 'handy-repairs-001',
        company: 'Handy repairs',
        job_title: 'Software Engineer',
        status: 'company response',
        match_score: 78,
        applied_at: '2025-12-14T09:15:00',
        updated_at: '2025-12-19T11:45:00',
        location: 'San Francisco, CA',
        salary_range: '$100,000 - $130,000',
        folder_name: 'Handy-repairs-SoftwareEngineer'
    },
    {
        id: 'hitech-co-001',
        company: 'Hitech co',
        job_title: 'Full Stack Developer',
        status: 'scheduled interview',
        match_score: 92,
        applied_at: '2025-12-13T08:00:00',
        updated_at: '2025-12-19T16:30:00',
        location: 'Austin, TX',
        salary_range: '$110,000 - $140,000',
        folder_name: 'Hitech-co-FullStackDeveloper'
    },
    {
        id: 'superstars-001',
        company: 'Superstars',
        job_title: 'Backend Engineer',
        status: 'applied',
        match_score: 80,
        applied_at: '2025-12-16T11:20:00',
        updated_at: '2025-12-17T09:10:00',
        location: 'Seattle, WA',
        salary_range: '$115,000 - $145,000',
        folder_name: 'Superstars-BackendEngineer'
    },
    {
        id: 'mortgage-co-001',
        company: 'Mortgage Co',
        job_title: 'Senior Developer',
        status: 'pending',
        match_score: 75,
        applied_at: '2025-12-17T13:45:00',
        updated_at: '2025-12-17T13:45:00',
        location: 'Chicago, IL',
        salary_range: '$105,000 - $135,000',
        folder_name: 'Mortgage-Co-SeniorDeveloper'
    },
    {
        id: 'fintech-a-co-001',
        company: 'Fintech A co',
        job_title: 'Software Engineer',
        status: 'interview notes',
        match_score: 88,
        applied_at: '2025-12-12T10:00:00',
        updated_at: '2025-12-19T15:00:00',
        location: 'Boston, MA',
        salary_range: '$125,000 - $155,000',
        folder_name: 'Fintech-A-co-SoftwareEngineer'
    },
    {
        id: 'fintect-b-co-001',
        company: 'Fintect B Co',
        job_title: 'Senior Full Stack Engineer',
        status: 'applied',
        match_score: 82,
        applied_at: '2025-12-15T14:30:00',
        updated_at: '2025-12-18T10:15:00',
        location: 'Denver, CO',
        salary_range: '$130,000 - $160,000',
        folder_name: 'Fintect-B-Co-SeniorFullStackEngineer'
    },
    {
        id: 'global-a-co-001',
        company: 'Global a co',
        job_title: 'Lead Software Engineer',
        status: 'company response',
        match_score: 90,
        applied_at: '2025-12-11T09:00:00',
        updated_at: '2025-12-19T12:30:00',
        location: 'Remote',
        salary_range: '$140,000 - $170,000',
        folder_name: 'Global-a-co-LeadSoftwareEngineer'
    },
    {
        id: 'justtest-001',
        company: 'JustTest',
        job_title: 'QA Engineer',
        status: 'applied',
        match_score: 70,
        applied_at: '2025-12-18T15:00:00',
        updated_at: '2025-12-18T15:00:00',
        location: 'Portland, OR',
        salary_range: '$95,000 - $120,000',
        folder_name: 'JustTest-QAEngineer'
    },
];

// Archived applications (5)
const DEMO_ARCHIVED_APPLICATIONS = [
    {
        id: 'mortgage-co-archived-001',
        company: 'Mortgage Co',
        job_title: 'Senior Developer',
        status: 'rejected',
        match_score: 75,
        applied_at: '2025-11-20T10:00:00',
        updated_at: '2025-12-01T14:30:00',
        location: 'Chicago, IL',
        folder_name: 'Mortgage-Co-SeniorDeveloper-Archived'
    },
    {
        id: 'fortune500-bank-001',
        company: 'Fortune500 Bank',
        job_title: 'Software Architect',
        status: 'rejected',
        match_score: 68,
        applied_at: '2025-11-15T09:00:00',
        updated_at: '2025-11-28T16:00:00',
        location: 'New York, NY',
        folder_name: 'Fortune500-Bank-SoftwareArchitect'
    },
    {
        id: 'capital-credit-card-001',
        company: 'Capital Credit Card',
        job_title: 'Full Stack Developer',
        status: 'rejected',
        match_score: 73,
        applied_at: '2025-11-10T11:00:00',
        updated_at: '2025-11-25T13:00:00',
        location: 'McLean, VA',
        folder_name: 'Capital-Credit-Card-FullStackDeveloper'
    },
    {
        id: 'healthcare-company-001',
        company: 'Healthcare Company',
        job_title: 'Senior Software Engineer',
        status: 'rejected',
        match_score: 77,
        applied_at: '2025-11-05T08:00:00',
        updated_at: '2025-11-20T15:00:00',
        location: 'Louisville, KY',
        folder_name: 'Healthcare-Company-SeniorSoftwareEngineer'
    },
    {
        id: 'techpassword-co-001',
        company: 'TechPassword Co',
        job_title: 'Backend Engineer',
        status: 'rejected',
        match_score: 80,
        applied_at: '2025-10-30T10:00:00',
        updated_at: '2025-11-15T12:00:00',
        location: 'Toronto, ON',
        folder_name: 'TechPassword-Co-BackendEngineer'
    }
];

// Network contacts (with scrambled names)
const DEMO_NETWORK_CONTACTS = [
    {
        id: 'capital-finance-firm-contact-001',
        person_name: 'Alexandra Thompson',
        company_name: 'Capital Finance Firm',
        job_title: 'Senior Technical Recruiter',
        status: 'in conversation',
        created_at: '2025-12-10T10:00:00',
        match_score: 85
    },
    {
        id: 'recruitersstarts-001',
        person_name: 'Sarah Johnson',
        company_name: 'RecruitersStarts.com',
        job_title: 'Senior Technical Recruiter',
        status: 'in conversation',
        created_at: '2025-12-10T10:00:00',
        match_score: 85
    },
    {
        id: 'superstars-contact-001',
        person_name: 'Patricia Lee',
        company_name: 'Superstars',
        job_title: 'Engineering Manager',
        status: 'connection accepted',
        created_at: '2025-12-12T14:30:00',
        match_score: 88
    },
    {
        id: 'handy-repairs-contact-001',
        person_name: 'Marcus Williams',
        company_name: 'Handy repairs',
        job_title: 'Senior Software Engineer',
        status: 'sent email',
        created_at: '2025-12-14T09:15:00',
        match_score: 82
    },
    {
        id: 'fintech-a-contact-001',
        person_name: 'Christopher Brown',
        company_name: 'Fintech A co',
        job_title: 'Tech Lead',
        status: 'meeting scheduled',
        created_at: '2025-12-11T11:00:00',
        match_score: 90
    },
    {
        id: 'fintect-b-contact-001',
        person_name: 'Jennifer Davis',
        company_name: 'Fintect B Co',
        job_title: 'VP of Engineering',
        status: 'in conversation',
        created_at: '2025-12-13T15:20:00',
        match_score: 87
    },
    {
        id: 'global-a-contact-001',
        person_name: 'Daniel Garcia',
        company_name: 'Global a co',
        job_title: 'Director of Engineering',
        status: 'connection accepted',
        created_at: '2025-12-15T10:45:00',
        match_score: 92
    },
    {
        id: 'justtest-contact-001',
        person_name: 'Nicole Anderson',
        company_name: 'JustTest',
        job_title: 'QA Manager',
        status: 'sent email',
        created_at: '2025-12-16T13:00:00',
        match_score: 75
    },
    {
        id: 'medical-network-contact-001',
        person_name: 'Ryan Mitchell',
        company_name: 'Medical Network Co',
        job_title: 'Senior Developer',
        status: 'found contact',
        created_at: '2025-12-17T08:30:00',
        match_score: 78
    }
];

// Timeline entries for each application (3-5 entries showing progression)
const DEMO_TIMELINES = {
    'capital-finance-firm-001': [
        {
            datetime: '2025-12-18T14:20:00',
            status: 'applied',
            notes: 'Application submitted successfully. Received confirmation email from HR.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-15T10:30:00',
            status: 'pending',
            notes: 'Application created and prepared for submission.',
            type: 'status_update'
        }
    ],
    'handy-repairs-001': [
        {
            datetime: '2025-12-19T11:45:00',
            status: 'company response',
            notes: 'Received response from hiring manager. They are interested in scheduling a phone call.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-17T09:30:00',
            status: 'applied',
            notes: 'Application submitted. Confirmation received.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-14T09:15:00',
            status: 'pending',
            notes: 'Application created.',
            type: 'status_update'
        }
    ],
    'hitech-co-001': [
        {
            datetime: '2025-12-19T16:30:00',
            status: 'scheduled interview',
            notes: 'Phone screening scheduled for next week. Looking forward to discussing the role.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-16T14:00:00',
            status: 'company response',
            notes: 'Received positive response. They want to move forward with an interview.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-14T10:00:00',
            status: 'applied',
            notes: 'Application submitted successfully.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-13T08:00:00',
            status: 'pending',
            notes: 'Application created.',
            type: 'status_update'
        }
    ],
    'superstars-001': [
        {
            datetime: '2025-12-17T09:10:00',
            status: 'applied',
            notes: 'Application submitted. Waiting for response.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-16T11:20:00',
            status: 'pending',
            notes: 'Application created.',
            type: 'status_update'
        }
    ],
    'mortgage-co-001': [
        {
            datetime: '2025-12-17T13:45:00',
            status: 'pending',
            notes: 'Application created. Ready to submit.',
            type: 'status_update'
        }
    ],
    'fintech-a-co-001': [
        {
            datetime: '2025-12-19T15:00:00',
            status: 'interview notes',
            notes: '<div style="font-family: inherit;"><h3 style="font-weight: 700; font-size: 18px; margin-bottom: 8px; color: #1f2937;">Discovery Call Interview Notes with Darnell G</h3><p style="font-size: 14px; color: #6b7280; margin-bottom: 20px;">Here is an organized summary of the key information discussed:</p><div style="margin-bottom: 24px;"><h4 style="font-weight: 600; font-size: 16px; margin-bottom: 12px; color: #1f2937;">💼 Role & Team Details</h4><ul style="margin: 0; padding-left: 20px; list-style-type: disc;"><li style="margin-bottom: 8px; line-height: 1.6;"><strong>Job Title/Function:</strong> Manager, Analytics Engineering, reports to the Sr. Manager Analytics.</li><li style="margin-bottom: 8px; line-height: 1.6;"><strong>Direct Reports:</strong> Will manage <strong>2 direct reports.</strong></li><li style="margin-bottom: 8px; line-height: 1.6;"><strong>Team Composition:</strong> The broader team includes:<ul style="margin-top: 4px; padding-left: 20px; list-style-type: disc;"><li style="margin-bottom: 4px;"><strong>6 Analytics Engineers</strong></li><li style="margin-bottom: 4px;"><strong>2 Subject Matter Experts (SMEs)</strong></li></ul></li><li style="margin-bottom: 8px; line-height: 1.6;"><strong>Key Products Covered:</strong><ul style="margin-top: 4px; padding-left: 20px; list-style-type: disc;"><li style="margin-bottom: 4px;">Professional Employment</li><li style="margin-bottom: 4px;">Payroll</li><li style="margin-bottom: 4px;">International</li></ul></li></ul></div><div style="margin-bottom: 24px;"><h4 style="font-weight: 600; font-size: 16px; margin-bottom: 12px; color: #1f2937;">💰 Compensation & Location</h4><ul style="margin: 0; padding-left: 20px; list-style-type: disc;"><li style="margin-bottom: 8px; line-height: 1.6;"><strong>Total Compensation (Year 1 Target):</strong> <strong>$220,000</strong> (Base pay + Stock options)</li><li style="margin-bottom: 8px; line-height: 1.6;"><strong>Stock Option Vesting Schedule:</strong><ul style="margin-top: 4px; padding-left: 20px; list-style-type: disc;"><li style="margin-bottom: 4px;">Year 1: <strong>5%</strong></li><li style="margin-bottom: 4px;">Year 2: <strong>15%</strong></li><li style="margin-bottom: 4px;">Year 3: <strong>40%</strong></li><li style="margin-bottom: 4px;">Year 4: <strong>40%</strong></li></ul></li><li style="margin-bottom: 8px; line-height: 1.6;"><strong>Work Arrangement:</strong> <strong>2 days a week hybrid</strong> (implied 3 days remote)</li></ul></div></div>',
            type: 'status_update'
        },
        {
            datetime: '2025-12-17T10:00:00',
            status: 'scheduled interview',
            notes: 'Technical interview scheduled for this week.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-15T11:30:00',
            status: 'company response',
            notes: 'Received call from recruiter. They are interested in moving forward.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-13T09:00:00',
            status: 'applied',
            notes: 'Application submitted.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-12T10:00:00',
            status: 'pending',
            notes: 'Application created.',
            type: 'status_update'
        }
    ],
    'fintect-b-co-001': [
        {
            datetime: '2025-12-18T10:15:00',
            status: 'applied',
            notes: 'Application submitted. Received confirmation.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-15T14:30:00',
            status: 'pending',
            notes: 'Application created.',
            type: 'status_update'
        }
    ],
    'global-a-co-001': [
        {
            datetime: '2025-12-19T12:30:00',
            status: 'company response',
            notes: 'Received email from engineering manager. They are reviewing applications and will get back soon.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-15T10:00:00',
            status: 'applied',
            notes: 'Application submitted successfully.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-11T09:00:00',
            status: 'pending',
            notes: 'Application created.',
            type: 'status_update'
        }
    ],
    'justtest-001': [
        {
            datetime: '2025-12-18T15:00:00',
            status: 'applied',
            notes: 'Application submitted.',
            type: 'status_update'
        },
        {
            datetime: '2025-12-18T15:00:00',
            status: 'pending',
            notes: 'Application created.',
            type: 'status_update'
        }
    ],
    'medical-network-co-001': [
        {
            datetime: '2025-12-19T08:30:00',
            status: 'pending',
            notes: 'Application created. Preparing to submit.',
            type: 'status_update'
        }
    ]
};

// Daily activities (last 5 days)
const DEMO_DAILY_ACTIVITIES = [
    {
        date: getDemoDates()[0],
        activity_count: 4,
        activities: [
            {
                time: '14:20',
                type: 'status_update',
                company: 'Capital Finance Firm',
                position: 'Senior Software Engineer',
                activity: 'Status updated to "applied"',
                status: 'applied',
                timestamp: '14:20'
            },
            {
                time: '12:30',
                type: 'contact',
                company: 'Global a co',
                position: 'Lead Software Engineer',
                activity: 'Received response from engineering manager',
                status: 'company response',
                timestamp: '12:30',
                person: 'Robert Taylor'
            },
            {
                time: '11:45',
                type: 'status_update',
                company: 'Handy repairs',
                position: 'Software Engineer',
                activity: 'Status updated to "company response"',
                status: 'company response',
                timestamp: '11:45'
            },
            {
                time: '10:15',
                type: 'application',
                company: 'Fintect B Co',
                position: 'Senior Full Stack Engineer',
                activity: 'Application submitted',
                status: 'applied',
                timestamp: '10:15'
            }
        ]
    },
    {
        date: getDemoDates()[1],
        activity_count: 3,
        activities: [
            {
                time: '16:30',
                type: 'status_update',
                company: 'Hitech co',
                description: 'Status updated to "scheduled interview"',
                person: null
            },
            {
                time: '15:00',
                type: 'interview',
                company: 'Fintech A co',
                position: 'Software Engineer',
                activity: 'Completed technical interview',
                status: 'interview notes',
                timestamp: '15:00',
                person: 'David Kim'
            },
            {
                time: '13:00',
                type: 'contact',
                company: 'JustTest',
                position: 'QA Engineer',
                activity: 'Sent email to QA Manager',
                status: 'applied',
                timestamp: '13:00',
                person: 'Amanda Wilson'
            },
            {
                time: '10:45',
                type: 'contact',
                company: 'Global a co',
                position: 'Lead Software Engineer',
                activity: 'Connection accepted on LinkedIn',
                status: 'contacted someone',
                timestamp: '10:45',
                person: 'Robert Taylor'
            }
        ]
    },
    {
        date: getDemoDates()[2],
        activity_count: 3,
        activities: [
            {
                time: '15:00',
                type: 'application',
                company: 'JustTest',
                position: 'QA Engineer',
                activity: 'Application submitted',
                status: 'applied',
                timestamp: '15:00',
                person: null
            },
            {
                time: '14:30',
                type: 'contact',
                company: 'Fintect B Co',
                position: 'Senior Full Stack Engineer',
                activity: 'Started conversation with VP of Engineering',
                status: 'applied',
                timestamp: '14:30',
                person: 'Jessica Martinez'
            },
            {
                time: '09:10',
                type: 'status_update',
                company: 'Superstars',
                description: 'Status updated to "applied"',
                person: null
            }
        ]
    },
    {
        date: getDemoDates()[3],
        activity_count: 3,
        activities: [
            {
                time: '14:00',
                type: 'status_update',
                company: 'Hitech co',
                description: 'Status updated to "company response"',
                person: null
            },
            {
                time: '11:30',
                type: 'contact',
                company: 'Fintech A co',
                position: 'Software Engineer',
                activity: 'Received call from recruiter',
                status: 'applied',
                timestamp: '11:30',
                person: 'David Kim'
            },
            {
                time: '10:00',
                type: 'status_update',
                company: 'Global a co',
                description: 'Status updated to "applied"',
                person: null
            }
        ]
    },
    {
        date: getDemoDates()[4],
        activity_count: 2,
        activities: [
            {
                time: '15:20',
                type: 'contact',
                company: 'Fintect B Co',
                position: 'Senior Full Stack Engineer',
                activity: 'Connected with VP of Engineering on LinkedIn',
                status: 'applied',
                timestamp: '15:20',
                person: 'Jessica Martinez'
            },
            {
                time: '14:30',
                type: 'contact',
                company: 'Superstars',
                position: 'Backend Engineer',
                activity: 'Connection accepted',
                status: 'contacted someone',
                timestamp: '14:30',
                person: 'Michael Chen'
            },
            {
                time: '11:00',
                type: 'contact',
                company: 'Fintech A co',
                position: 'Software Engineer',
                activity: 'Found contact and sent connection request',
                status: 'contacted someone',
                timestamp: '11:00',
                person: 'David Kim'
            },
            {
                time: '10:00',
                type: 'contact',
                company: 'RecruitersStarts.com',
                position: 'Senior Technical Recruiter',
                activity: 'Started conversation with technical recruiter',
                status: 'applied',
                timestamp: '10:00',
                person: 'Sarah Johnson'
            }
        ]
    }
];

// Dashboard stats
const DEMO_DASHBOARD_STATS = {
    total: 10,
    pending: 2,
    applied: 5,
    contacted_someone: 0,
    company_response: 2,
    scheduled_interview: 1,
    interview_notes: 1,
    interview_follow_up: 0,
    offered: 0,
    rejected: 0,
    accepted: 0
};

// Chart data for Reports page
const DEMO_APPLICATIONS_BY_STATUS = {
    'pending': 2,
    'applied': 5,
    'company response': 2,
    'scheduled interview': 1,
    'interview notes': 1,
    'offered': 0,
    'rejected': 0,
    'accepted': 0
};

// Status changes over time (last 7 days)
const DEMO_STATUS_CHANGES = {
    '2025-12-19': { 'applied': 1, 'company response': 1 },
    '2025-12-18': { 'applied': 2, 'scheduled interview': 1 },
    '2025-12-17': { 'applied': 1, 'company response': 1 },
    '2025-12-16': { 'applied': 1 },
    '2025-12-15': { 'applied': 1, 'pending': 1 },
    '2025-12-14': { 'applied': 1, 'pending': 1 },
    '2025-12-13': { 'pending': 1 }
};

// Daily activities by status (for line chart)
const DEMO_DAILY_ACTIVITIES_BY_STATUS = {
    'applied': [
        { date: '2025-12-19', count: 1 },
        { date: '2025-12-18', count: 2 },
        { date: '2025-12-17', count: 1 },
        { date: '2025-12-16', count: 1 },
        { date: '2025-12-15', count: 1 },
        { date: '2025-12-14', count: 1 },
        { date: '2025-12-13', count: 0 }
    ],
    'company response': [
        { date: '2025-12-19', count: 1 },
        { date: '2025-12-18', count: 0 },
        { date: '2025-12-17', count: 1 },
        { date: '2025-12-16', count: 0 },
        { date: '2025-12-15', count: 0 },
        { date: '2025-12-14', count: 0 },
        { date: '2025-12-13', count: 0 }
    ],
    'scheduled interview': [
        { date: '2025-12-19', count: 0 },
        { date: '2025-12-18', count: 1 },
        { date: '2025-12-17', count: 0 },
        { date: '2025-12-16', count: 0 },
        { date: '2025-12-15', count: 0 },
        { date: '2025-12-14', count: 0 },
        { date: '2025-12-13', count: 0 }
    ],
    'pending': [
        { date: '2025-12-19', count: 0 },
        { date: '2025-12-18', count: 0 },
        { date: '2025-12-17', count: 0 },
        { date: '2025-12-16', count: 0 },
        { date: '2025-12-15', count: 1 },
        { date: '2025-12-14', count: 1 },
        { date: '2025-12-13', count: 1 }
    ]
};

// Cumulative activities by status (running totals)
const DEMO_CUMULATIVE_ACTIVITIES_BY_STATUS = {
    'applied': [
        { date: '2025-12-13', count: 0 },
        { date: '2025-12-14', count: 1 },
        { date: '2025-12-15', count: 2 },
        { date: '2025-12-16', count: 3 },
        { date: '2025-12-17', count: 4 },
        { date: '2025-12-18', count: 6 },
        { date: '2025-12-19', count: 7 }
    ],
    'company response': [
        { date: '2025-12-13', count: 0 },
        { date: '2025-12-14', count: 0 },
        { date: '2025-12-15', count: 0 },
        { date: '2025-12-16', count: 0 },
        { date: '2025-12-17', count: 1 },
        { date: '2025-12-18', count: 1 },
        { date: '2025-12-19', count: 2 }
    ],
    'scheduled interview': [
        { date: '2025-12-13', count: 0 },
        { date: '2025-12-14', count: 0 },
        { date: '2025-12-15', count: 0 },
        { date: '2025-12-16', count: 0 },
        { date: '2025-12-17', count: 0 },
        { date: '2025-12-18', count: 1 },
        { date: '2025-12-19', count: 1 }
    ],
    'pending': [
        { date: '2025-12-13', count: 1 },
        { date: '2025-12-14', count: 2 },
        { date: '2025-12-15', count: 2 },
        { date: '2025-12-16', count: 2 },
        { date: '2025-12-17', count: 2 },
        { date: '2025-12-18', count: 2 },
        { date: '2025-12-19', count: 2 }
    ]
};

// Demo templates (anonymized)
const DEMO_TEMPLATES = [
    {
        id: 'template-001',
        title: 'Initial Connection Request',
        delivery_method: 'LinkedIn',
        content: 'Hello [Name],\n\nI came across your profile and was impressed by your experience in [Industry]. I would love to connect and learn more about your work at [Company].\n\nBest regards,\nJason Smith',
        created_at: '2025-12-10T10:00:00',
        updated_at: '2025-12-10T10:00:00'
    },
    {
        id: 'template-002',
        title: 'Follow-up After Application',
        delivery_method: 'Email',
        content: 'Dear Hiring Manager,\n\nI wanted to follow up on my application for the [Position] role at [Company]. I am very interested in this opportunity and would welcome the chance to discuss how my skills align with your needs.\n\nThank you for your consideration.\n\nBest regards,\nJason Smith',
        created_at: '2025-12-08T14:30:00',
        updated_at: '2025-12-08T14:30:00'
    },
    {
        id: 'template-003',
        title: 'Thank You After Interview',
        delivery_method: 'Email',
        content: 'Dear [Interviewer Name],\n\nThank you for taking the time to speak with me today about the [Position] role. I enjoyed our conversation and learning more about [Company] and the team.\n\nI am very interested in this opportunity and look forward to hearing from you.\n\nBest regards,\nJason Smith',
        created_at: '2025-12-05T09:00:00',
        updated_at: '2025-12-05T09:00:00'
    },
    {
        id: 'template-004',
        title: 'Networking Introduction',
        delivery_method: 'LinkedIn',
        content: 'Hi [Name],\n\nI noticed we have mutual connections in the [Industry] space. I would love to connect and potentially collaborate or share insights.\n\nLooking forward to connecting!\n\nBest,\nJason Smith',
        created_at: '2025-12-03T11:20:00',
        updated_at: '2025-12-03T11:20:00'
    }
];

// Export for use in HTML pages
if (typeof window !== 'undefined') {
    window.DEMO_DATA = {
        applications: DEMO_APPLICATIONS,
        archived: DEMO_ARCHIVED_APPLICATIONS,
        contacts: DEMO_NETWORK_CONTACTS,
        timelines: DEMO_TIMELINES,
        dailyActivities: DEMO_DAILY_ACTIVITIES,
        stats: DEMO_DASHBOARD_STATS,
        companyMappings: COMPANY_MAPPINGS,
        templates: DEMO_TEMPLATES,
        // Chart data for Reports
        applicationsByStatus: DEMO_APPLICATIONS_BY_STATUS,
        statusChanges: DEMO_STATUS_CHANGES,
        dailyActivitiesByStatus: DEMO_DAILY_ACTIVITIES_BY_STATUS,
        cumulativeActivitiesByStatus: DEMO_CUMULATIVE_ACTIVITIES_BY_STATUS,
        // Real data from hunter app (loaded separately to keep file size manageable)
        // These will be populated by separate script tags if needed
        analytics: null,
        reports: null
    };
}

// Load real analytics and reports data if available (from separate files or inline)
// For demo purposes, we'll load them on demand in the respective pages
