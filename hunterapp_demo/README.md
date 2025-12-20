# Hunter Demo Version

This is a static HTML demo version of the Hunter job application management tool, designed for deployment to Netlify at `hunterappdemo.kervinapps.com`.

## Structure

- **Main Pages**: All core pages (App Dash, Network Dash, Progress, Archive, Reports, Analytics, Daily Activities, Templates, New Application, Manage Resume, Guide pages)
- **Application Detail Pages**: 9 application detail pages with scrambled research content and timeline features
- **Networking Contact Pages**: 8 networking contact detail pages with scrambled names and research
- **Static Assets**: All CSS, JavaScript, and images copied from the original application

## Key Features

### Demo Data
- All data is hardcoded in `static/js/demo-data.js`
- No backend or API calls
- All navigation remains fully functional

### Company Name Replacements
- CI Financial → Capital Finance Firm
- Angi → Handy repairs
- Metropolis technologies → Hitech co
- Greystar → Superstars
- Meridianlink → Mortgage Co
- Current → Fintech A co
- Stripe → Fintect B Co
- Broadridge → Global a co
- JustTest → JustTest
- Zocdoc → Medical Network Co
- Moodys → Fortune500 Bank
- Capital One → Capital Credit Card
- Humana → Healthcare Company
- 1Password → TechPassword Co

### Personal Information Anonymization
- Kervin → Jason
- Leacock → Smith
- leacock.kervin@gmail.com → jason.smith@hunterapp.com

### Disabled Features
The following buttons are greyed out and show upgrade messages:
- Save Resume
- Analyze & Create Application
- Upgrade to Full AI
- Save Contact Details
- Update Status
- Generate Hiring Manager Intro Messages
- Generate Recruiter Intro Messages
- Generate Customized Resume
- Create Contact
- Update
- Export CSV (in Reports)

### Functional Features
- All navigation buttons and links work
- Timeline/Updates feature on application detail pages
- Menu system fully operational
- All guide pages accessible

## Deployment

This is a static site ready for Netlify deployment. Simply point Netlify to the `hunterapp_demo/` folder.

## Files Created

- 15 main HTML pages
- 9 application detail pages (with timeline features)
- 8 networking contact pages
- Demo data JavaScript file
- Upgrade handler JavaScript file
- All static assets (CSS, JS, images)

Total: 32 HTML files + supporting assets
