"""Convierte INFORME_PERU_2026.md a PDF con estilo institucional."""
import markdown
from xhtml2pdf import pisa
from pathlib import Path
from datetime import datetime

MD_PATH  = Path("d:/DemocracIA/INFORME_PERU_2026.md")
PDF_PATH = Path("d:/DemocracIA/INFORME_PERU_2026.pdf")

md_text = MD_PATH.read_text(encoding="utf-8")

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
)

CSS = """
@page {
  size: A4;
  margin: 2.2cm 2cm 2.5cm 2cm;
  @frame footer_frame {
    -pdf-frame-content: footer_content;
    left: 2cm; width: 17cm;
    bottom: 1cm; height: 1cm;
  }
}
body {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 10pt;
  line-height: 1.45;
  color: #1a1a1a;
}
h1 {
  color: #0a0e17;
  font-size: 22pt;
  border-bottom: 2pt solid #00796b;
  padding-bottom: 6pt;
  margin-top: 6pt;
  margin-bottom: 14pt;
  page-break-after: avoid;
}
h2 {
  color: #004d40;
  font-size: 15pt;
  border-bottom: 1pt solid #b0bec5;
  padding-bottom: 3pt;
  margin-top: 18pt;
  margin-bottom: 8pt;
  page-break-after: avoid;
}
h3 {
  color: #00695c;
  font-size: 12pt;
  margin-top: 12pt;
  margin-bottom: 6pt;
  page-break-after: avoid;
}
h4 {
  color: #00695c;
  font-size: 11pt;
  margin-top: 10pt;
  margin-bottom: 4pt;
  font-weight: bold;
}
p { margin: 6pt 0; text-align: justify; }
ul, ol { margin: 6pt 0; padding-left: 20pt; }
li { margin: 2pt 0; }
strong { color: #000; }
em { color: #37474f; }
blockquote {
  border-left: 3pt solid #00796b;
  background: #f0f7f6;
  margin: 8pt 0;
  padding: 6pt 12pt;
  font-style: italic;
  color: #263238;
}
code {
  font-family: Courier, monospace;
  background: #f5f5f5;
  padding: 1pt 4pt;
  border-radius: 2pt;
  font-size: 9pt;
}
pre {
  background: #f5f5f5;
  padding: 8pt;
  border-left: 2pt solid #607d8b;
  font-size: 9pt;
  white-space: pre-wrap;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 8pt 0;
  font-size: 9pt;
}
th, td {
  border: 0.5pt solid #90a4ae;
  padding: 4pt 6pt;
  text-align: left;
  vertical-align: top;
}
th {
  background: #eceff1;
  color: #0a0e17;
  font-weight: bold;
}
tr:nth-child(even) td { background: #fafafa; }
a { color: #00695c; text-decoration: underline; }
hr { border: none; border-top: 1pt dashed #b0bec5; margin: 14pt 0; }
.footer {
  font-size: 8pt;
  color: #78909c;
  text-align: center;
}
"""

now = datetime.now().strftime("%Y-%m-%d %H:%M")
html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>{CSS}</style>
</head>
<body>
{html_body}
<div id="footer_content" class="footer">
DEMOCRAC.IA / PEIRS — Informe Perú 2026 v1.0 — Generado {now} — Página <pdf:pagenumber/> de <pdf:pagecount/>
</div>
</body>
</html>"""

with open(PDF_PATH, "wb") as out:
    result = pisa.CreatePDF(html, dest=out, encoding="utf-8")

if result.err:
    print(f"ERROR: {result.err}")
else:
    print(f"OK: {PDF_PATH}  ({PDF_PATH.stat().st_size // 1024} KB)")
