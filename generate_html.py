import re
import html
import subprocess
import os

def build_refined_report():
    md_path = 'EPAM_Concurrency_Research_Report.md'
    html_path = 'EPAM_Hardware_Concurrency_Report.html'
    pdf_path = 'EPAM_Hardware_Concurrency_Research_Report.pdf'
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    css = """
    @page {
        size: A4 portrait;
        margin: 12mm 12mm 12mm 12mm;
    }
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #0f1626;
        --bg-card: #152036;
        --text-primary: #ffffff;
        --text-secondary: #cbd5e1;
        --accent-cyan: #00e5b0;
        --accent-blue: #38bdf8;
        --accent-indigo: #818cf8;
        --accent-orange: #fb923c;
        --accent-red: #f87171;
        --border-color: #263554;
        --code-bg: #090e18;
        --table-header: #1b2845;
        --table-alt: #111a2f;
        --alert-bg: #131d33;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        line-height: 1.5;
        font-size: 13.5px;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .wrapper {
        max-width: 1000px;
        margin: 0 auto;
        padding: 1.5rem;
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
    header {
        border-bottom: 2px solid var(--accent-cyan);
        padding-bottom: 1.5rem;
        margin-bottom: 1.8rem;
    }
    .badge-bar {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.8rem;
    }
    .badge {
        background: rgba(0, 229, 176, 0.15);
        color: var(--accent-cyan);
        border: 1px solid rgba(0, 229, 176, 0.4);
        font-weight: 700;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
    }
    .badge.blue {
        background: rgba(56, 189, 248, 0.15);
        color: var(--accent-blue);
        border-color: rgba(56, 189, 248, 0.4);
    }
    h1 {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.2;
        color: #ffffff;
        margin-bottom: 0.5rem;
        break-after: avoid;
    }
    h2 {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--accent-cyan);
        margin-top: 2rem;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.4rem;
        break-after: avoid;
    }
    h3 {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--accent-blue);
        margin-top: 1.4rem;
        margin-bottom: 0.5rem;
        break-after: avoid;
    }
    h4 {
        font-size: 1rem;
        color: #ffffff;
        margin-top: 1rem;
        margin-bottom: 0.4rem;
        break-after: avoid;
    }
    p {
        color: var(--text-secondary);
        margin-bottom: 0.8rem;
        font-size: 0.95rem;
    }
    strong { color: #ffffff; font-weight: 600; }
    em { color: var(--accent-orange); font-style: normal; }
    ul, ol {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
        color: var(--text-secondary);
    }
    li {
        margin-bottom: 0.3rem;
        font-size: 0.93rem;
    }
    pre {
        background-color: var(--code-bg);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 0.8rem 1rem;
        overflow-x: auto;
        margin: 1rem 0;
        break-inside: avoid;
        page-break-inside: avoid;
    }
    code {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
        font-size: 0.86em;
        color: var(--accent-cyan);
        background-color: rgba(0, 229, 176, 0.1);
        padding: 0.15rem 0.35rem;
        border-radius: 3px;
        border: 1px solid rgba(0, 229, 176, 0.2);
    }
    pre code {
        background: transparent;
        padding: 0;
        border: none;
        color: #e2e8f0;
        font-size: 0.84rem;
        line-height: 1.45;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.2rem 0;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        overflow: hidden;
        font-size: 0.88rem;
        break-inside: avoid;
        page-break-inside: avoid;
    }
    th, td {
        padding: 0.6rem 0.8rem;
        text-align: left;
        border-bottom: 1px solid var(--border-color);
        color: #e2e8f0;
    }
    th {
        background-color: var(--table-header);
        color: #ffffff;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid var(--accent-cyan);
    }
    tr:nth-child(even) { background-color: var(--table-alt); }
    .diagram-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1.2rem auto;
        text-align: center;
        max-width: 95%;
        break-inside: avoid;
        page-break-inside: avoid;
    }
    .diagram-card img {
        max-width: 100%;
        max-height: 310px;
        width: auto;
        height: auto;
        object-fit: contain;
        display: block;
        margin: 0 auto;
        border-radius: 4px;
    }
    .diagram-caption {
        font-size: 0.82rem;
        color: var(--accent-blue);
        margin-top: 0.6rem;
        font-weight: 500;
    }
    .callout {
        background-color: var(--alert-bg);
        border-left: 3px solid var(--accent-cyan);
        border-radius: 0 6px 6px 0;
        padding: 0.8rem 1.1rem;
        margin: 1.2rem 0;
        break-inside: avoid;
        page-break-inside: avoid;
    }
    .callout.important { border-left-color: var(--accent-red); }
    .callout-title {
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--accent-cyan);
        margin-bottom: 0.3rem;
    }
    .callout.important .callout-title { color: var(--accent-red); }
    hr {
        border: 0;
        height: 1px;
        background: var(--border-color);
        margin: 1.8rem 0;
    }
    @media print {
        body { background: #0a0e17; padding: 0; }
        .wrapper { border: none; box-shadow: none; padding: 0; max-width: 100%; background: transparent; }
        .diagram-card img { max-height: 280px; }
        pre { max-height: 400px; }
    }
    """

    lines = md_text.split('\n')
    output_html = []
    
    in_code_block = False
    code_lang = ""
    code_lines = []
    
    in_table = False
    table_header = []
    table_rows = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Code fence handling
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lang = line.strip()[3:].strip()
                code_lines = []
            else:
                in_code_block = False
                code_content = html.escape('\n'.join(code_lines))
                output_html.append(f'<pre><code class="language-{code_lang}">{code_content}</code></pre>')
            i += 1
            continue
            
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
            
        # Table handling
        if '|' in line and not in_code_block:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) > 0:
                if not in_table:
                    # Check next line for separator
                    if i + 1 < len(lines) and re.match(r'^\s*\|?(\s*:?-+:?\s*\|)+\s*$', lines[i+1]):
                        in_table = True
                        table_header = parts
                        table_rows = []
                        i += 2
                        continue
                else:
                    table_rows.append(parts)
                    i += 1
                    continue
        else:
            if in_table:
                # Flush table
                in_table = False
                tbl_html = ['<table><thead><tr>']
                for th in table_header:
                    tbl_html.append(f'<th>{parse_inline(th)}</th>')
                tbl_html.append('</tr></thead><tbody>')
                for row in table_rows:
                    tbl_html.append('<tr>')
                    for td in row:
                        tbl_html.append(f'<td>{parse_inline(td)}</td>')
                    tbl_html.append('</tr>')
                tbl_html.append('</tbody></table>')
                output_html.append(''.join(tbl_html))

        # Blank line
        if not line.strip():
            i += 1
            continue
            
        # Headings
        if line.startswith('# '):
            output_html.append(f'<h1>{parse_inline(line[2:])}</h1>')
            i += 1
            continue
        elif line.startswith('## '):
            output_html.append(f'<h2>{parse_inline(line[3:])}</h2>')
            i += 1
            continue
        elif line.startswith('### '):
            output_html.append(f'<h3>{parse_inline(line[4:])}</h3>')
            i += 1
            continue
        elif line.startswith('#### '):
            output_html.append(f'<h4>{parse_inline(line[5:])}</h4>')
            i += 1
            continue
            
        # Horizontal rule
        if line.strip() in ['---', '***', '___']:
            output_html.append('<hr>')
            i += 1
            continue
            
        # Image
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line.strip())
        if img_match:
            alt_text = img_match.group(1)
            img_src = img_match.group(2)
            caption_html = ""
            if i + 1 < len(lines) and lines[i+1].strip().startswith('*Figure') and lines[i+1].strip().endswith('*'):
                caption_html = f'<div class="diagram-caption">{lines[i+1].strip()[1:-1]}</div>'
                i += 1
            output_html.append(f'<div class="diagram-card"><img src="{img_src}" alt="{alt_text}">{caption_html}</div>')
            i += 1
            continue
            
        # Blockquote / Alert
        if line.startswith('> '):
            quote_text = line[2:]
            is_important = '[!IMPORTANT]' in quote_text or '[!WARNING]' in quote_text
            clean_text = quote_text.replace('[!IMPORTANT]', '').replace('[!NOTE]', '').replace('[!TIP]', '').strip()
            title = "IMPORTANT ARCHITECTURAL AXIOM" if is_important else "ARCHITECTURE NOTE"
            alert_class = "callout important" if is_important else "callout"
            output_html.append(f'<div class="{alert_class}"><div class="callout-title">{title}</div><p>{parse_inline(clean_text)}</p></div>')
            i += 1
            continue
            
        # Lists
        if line.strip().startswith('- ') or line.strip().startswith('* ') or re.match(r'^\d+\.\s', line.strip()):
            list_tag = 'ol' if re.match(r'^\d+\.\s', line.strip()) else 'ul'
            list_items = []
            while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ') or re.match(r'^\d+\.\s', lines[i].strip())):
                item_text = re.sub(r'^([-*]|\d+\.)\s+', '', lines[i].strip())
                list_items.append(f'<li>{parse_inline(item_text)}</li>')
                i += 1
            output_html.append(f'<{list_tag}>' + ''.join(list_items) + f'</{list_tag}>')
            continue

        # Regular Paragraph
        output_html.append(f'<p>{parse_inline(line)}</p>')
        i += 1

    final_content = '\n'.join(output_html)
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EPAM Systems | Hardware Concurrency, Memory Models & Lock-Free Design</title>
    <style>{css}</style>
</head>
<body>
    <div class="wrapper">
        <header>
            <div class="badge-bar">
                <span class="badge">EPAM Systems &bull; Architecture Practice</span>
                <span class="badge blue">Hardware Concurrency Deep Dive</span>
                <span class="badge">Lock-Free Systems CoE</span>
            </div>
            <h1>Hardware Concurrency, Memory Models & Lock-Free Design</h1>
            <p style="font-size: 1.15rem; color: #ffffff; margin-top: 0.4rem; font-weight: 600;">
                Deconstructing Modern Multi-Core Processors Down to the Wire
            </p>
            <p style="margin-top: 0.5rem; font-size: 0.9rem; color: #94a3b8;">
                <strong>Author:</strong> EPAM High-Performance Architecture Practice &bull; 
                <strong>Target Platforms:</strong> x86-64 (TSO) & ARM64 (Weak Ordering) &bull; 
                <strong>Specification:</strong> C++11/C++17/C++20 Memory Model
            </p>
        </header>
        <main>
            {final_content}
        </main>
    </div>
</body>
</html>
"""
    with open(html_path, 'w', encoding='utf-8') as out_f:
        out_f.write(full_html)
    print(f"Generated {html_path} successfully!")

    # Now generate the PDF via Edge with no header/footer
    edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    abs_html = os.path.abspath(html_path)
    abs_pdf = os.path.abspath(pdf_path)
    
    cmd = [
        edge_exe,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--no-pdf-header-footer',
        f'--print-to-pdf={abs_pdf}',
        abs_html
    ]
    print("Compiling PDF with Microsoft Edge...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(abs_pdf):
        print(f"SUCCESS: {pdf_path} created! Size: {os.path.getsize(abs_pdf)} bytes")
    else:
        print(f"Failed to generate PDF. Exit code: {res.returncode}")
        print("Stderr:", res.stderr)

def parse_inline(text):
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:var(--accent-blue); text-decoration:none;">\1</a>', text)
    return text

if __name__ == '__main__':
    build_refined_report()
