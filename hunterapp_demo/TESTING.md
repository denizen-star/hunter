# Testing the Demo Locally

## Quick Start

### Option 1: Using the Test Script (Recommended)

```bash
cd hunterapp_demo
./test-local.sh
```

This will start a server on port 8077. Open http://localhost:8077 in your browser.

To use a different port:
```bash
./test-local.sh 3000
```

### Option 2: Using Python Directly

```bash
cd hunterapp_demo
python3 -m http.server 8077
```

Then open http://localhost:8077 in your browser.

### Option 3: Using Node.js (if you have it)

```bash
cd hunterapp_demo
npx http-server -p 8077
```

## What to Test

1. **Navigation**: Click through all menu items to ensure links work
2. **Application Pages**: Click "View Summary" on application cards to see detail pages
3. **Timeline Feature**: Check application detail pages for the timeline/updates tab
4. **Disabled Buttons**: Click disabled buttons to verify upgrade messages appear
5. **Company Names**: Verify all company names are replaced correctly
6. **Personal Info**: Check that "Jason Smith" and "jason.smith@hunterapp.com" appear throughout
7. **Research Content**: Verify research sections have scrambled placeholder text
8. **Networking Pages**: Check networking contact detail pages
9. **Reports/Analytics**: Verify CSV export is disabled and empty states show
10. **AI Status**: Click "Check AI Status" to see fake hardcoded message

## Troubleshooting

### Port Already in Use
If port 8077 is busy, use a different port:
```bash
./test-local.sh 3000
```

### Python Not Found
Install Python 3 or use Node.js option above.

### Links Not Working
- Make sure you're accessing via `http://localhost:PORT` (not `file://`)
- Check browser console for any JavaScript errors
- Verify all HTML files are in the correct locations

### Images/CSS Not Loading
- Ensure the `static/` directory was copied correctly
- Check browser console for 404 errors on static assets

## Ready for Netlify?

Once everything works locally, you're ready to deploy to Netlify:
1. Point Netlify to the `hunterapp_demo/` folder
2. Set publish directory to `hunterapp_demo` (or just deploy the folder)
3. No build step needed - it's all static HTML!
