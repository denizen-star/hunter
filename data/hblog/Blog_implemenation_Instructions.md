# HBLOG Implementation Instructions

## Overview
This document provides step-by-step instructions for implementing the HBLOG feature using the card-based format (format-2-card-based.html) as the template.

## Reference Files
- **Format Template**: `/data/hblog/formats/format-2-card-based.html`
- **PDF Source**: `/data/hblog/Hunterblog - _Mysteries_ of the Hiring Process.pdf`
- **PDF Source 2**: `/data/hblog/HunterBlog-Behind-the-scenes truths.pdf`

## Implementation Steps

### Phase 1: Setup Infrastructure

#### 1.1 Add Blog CSS
Create `/static/css/blog.css` with styles for:
- Blog article container
- Article title, subtitle, metadata
- Content typography (headings, paragraphs, lists, blockquotes)
- Back link styling
- Responsive adjustments

Reference the styles from `format-2-card-based.html` (lines 20-120).

#### 1.2 Add Blog to Navigation
Edit `/static/js/shared-menu.js`:
- Add `{ href: '/blog', label: 'Blog', icon: 'Blog.png' }` to the `mainItems` array (line ~21)
- Ensure Blog.png icon exists in `/static/images/icons/`

### Phase 2: Create Blog Generator Service

#### 2.1 Create PDF Converter Script
Create `/scripts/convert_hblog_pdfs.py`:
- Use PyPDF2 to extract text from PDFs in `/data/hblog/`
- Parse PDF filenames to extract titles
- Convert extracted text to clean markdown
- Generate metadata.json with:
  - title (from PDF filename or extracted)
  - date (file modification date or extracted)
  - slug (URL-friendly from title)
  - excerpt (first paragraph or first 150 chars)
  - author (default: "Hunter Team")

#### 2.2 Create Blog Generator Service
Create `/app/services/blog_generator.py`:
- `generate_blog_listing()`: Creates blog listing page showing all articles
- `generate_article_page(slug)`: Creates individual article HTML pages
- Uses Jinja2 templates based on format-2-card-based.html structure
- Reads markdown files and metadata.json from `/data/hblog/articles/YYYY-MM-DD-slug/`

### Phase 3: Create Templates

#### 3.1 Article Page Template
Create `/app/templates/web/blog/article_page.html`:
- Base structure from `format-2-card-based.html`
- Use Jinja2 variables:
  - `{{ article.title }}`
  - `{{ article.subtitle }}`
  - `{{ article.date }}`
  - `{{ article.author }}`
  - `{{ article.content }}` (rendered markdown to HTML)
- Include shared-menu.js script
- Include hero-header structure matching dashboard style
- Use container div for content

#### 3.2 Blog Listing Template
Create `/app/templates/web/blog/blog_listing.html`:
- Hero-header with "HBLOG" title and subtitle
- List of articles in reverse chronological order
- Each article shows: title, date, excerpt
- Links to individual article pages
- Total article count display

### Phase 4: Flask Routes (Optional - for future integration)

#### 4.1 Add Blog Routes
In `/app/web.py`, add routes:
```python
@app.route('/blog')
def blog_listing():
    # Generate or return blog listing page
    pass

@app.route('/blog/<slug>')
def blog_article(slug):
    # Generate or return individual article page
    pass
```

### Phase 5: Convert Existing PDFs

#### 5.1 Run PDF Converter
Execute the converter script:
```bash
python scripts/convert_hblog_pdfs.py
```

This will:
- Process PDFs in `/data/hblog/`
- Create article directories: `/data/hblog/articles/YYYY-MM-DD-slug/`
- Generate `article.md` and `metadata.json` for each

#### 5.2 Generate HTML Pages
Run the blog generator:
```bash
python -c "from app.services.blog_generator import BlogGenerator; bg = BlogGenerator(); bg.generate_all_articles()"
```

### Phase 6: File Structure

Final structure should be:
```
data/hblog/
├── articles/
│   ├── 2026-01-05-mysteries-of-hiring-process/
│   │   ├── index.html          # Generated article page
│   │   ├── article.md           # Markdown content
│   │   └── metadata.json       # Article metadata
│   └── 2026-01-05-behind-scenes-truths/
│       ├── index.html
│       ├── article.md
│       └── metadata.json
├── blog.html                    # Generated listing page
└── [PDF files]                  # Source PDFs
```

## Design Specifications

### Layout Structure
- **Sidebar**: Uses shared-menu.js (180px width, white background)
- **Hero Header**: White background, sticky, matches dashboard style
  - Title: "HBLOG"
  - Subtitle: "Lessons learned from the job hunting journey"
- **Container**: Max-width 900px, centered, padding 32px 24px

### Article Card
- White background (#ffffff)
- Border-radius: 12px
- Padding: 48px
- Box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1)
- Single card containing entire article

### Typography
- **Title**: 42px, font-weight 700, color #111827
- **Subtitle**: 18px, color #6b7280
- **Meta**: 13px, uppercase, letter-spaced, color #9ca3af
- **Body**: 17px, line-height 1.75, color #374151
- **H2**: 28px, font-weight 700, with top border divider
- **H3**: 22px, font-weight 600
- **Blockquote**: Background #f9fafb, left border #3b82f6, italic

### Colors
- Background: #f3f4f6
- Card: #ffffff
- Text primary: #111827
- Text secondary: #6b7280
- Text meta: #9ca3af
- Link: #3b82f6
- Link hover: #2563eb

## Key Requirements

1. **No changes to App Dash** - Blog is independent
2. **Uses shared-menu.js** - Sidebar navigation matches rest of app
3. **Hero-header structure** - Matches dashboard hero-header style
4. **Container div** - Content lives in container like dashboard
5. **No emojis** - Anywhere in code or content
6. **Clean typography** - YOHOMO-inspired, readable, professional

## Testing Checklist

- [ ] Blog link appears in sidebar navigation
- [ ] Blog listing page displays all articles
- [ ] Individual article pages render correctly
- [ ] Back button returns to listing
- [ ] Typography and spacing match format-2 design
- [ ] Responsive on mobile devices
- [ ] PDFs convert correctly to markdown
- [ ] Metadata is properly extracted

## Future Enhancements

- Add search functionality
- Add categories/tags
- Add article pagination
- Add RSS feed
- Add social sharing buttons
- Add reading time estimates

