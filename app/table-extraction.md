For table extraction i want you to implement the bellow module so that we can extract table in a better and with accuracy. 

## 0  Install & set up the toolbox

```bash
# system deps
ghostscript poppler-utils tesseract-ocr

# Python
pip install "camelot-py[cv]" pdfplumber gmft \
            pymupdf pillow pytesseract torch torchvision tqdm
```

*Camelot* needs **Ghostscript** for its lattice engine; *gmft* bundles Microsoft’s **Table Transformer** weights and will CUDA-accelerate automatically if a GPU is present. ([camelot-py.readthedocs.io][1], [GitHub][2])

---

## 1  High-level flow

```mermaid
graph TD
  subgraph Stage 1  Vector PDF?
    A[PDF file] -->|has extractable text?| B[Rule-based pass]
    A -->|scanned / none| C[DL fallback]
  end
  B --> D[Merge & normalise]
  C --> D
  D --> E[Post-process<br>(row/col spans, HTML/CSV)]
```

---

## 2  Rule-based pass (fast, cheap)

1. **Detect tables with Camelot twice**

   ```python
   import camelot
   tables_lat = camelot.read_pdf(pdf, flavor="lattice", pages="all")
   tables_str = camelot.read_pdf(pdf, flavor="stream", pages="all")
   ```

   *If* `tables_lat` returns ≥1 table with ≥2 rows → keep; else fall back to `tables_str`.

   * **Lattice** excels when ruling lines are present.
   * **Stream** works when only whitespace separates columns. ([Medium][3])

2. **Repair ugly cell breaks with pdfplumber** (optional)

   ```python
   import pdfplumber, itertools
   with pdfplumber.open(pdf) as pdf_doc:
       page = pdf_doc.pages[0]
       table = page.extract_table({
           "vertical_strategy": "text",
           "horizontal_strategy": "lines"  # tweak per layout
       })
   ```

   pdfplumber exposes raw char geometry so you can merge split words or detect rowspan manually.

3. **Quick quality gate**
   Drop any table where the median cell length is < 2 characters *and* column count < 2 – those are usually false positives.

---

## 3  Deep-learning fallback (robust on scans & “drawn” tables)

### 3.1 Use GMFT (Table Transformer wrapper)

```bash
gmft extract tables my.pdf --out out/tables.json \
     --format csv  # also supports json, df, md
```

Behind the scenes GMFT:

* rasterises each page,
* runs **Table Transformer** DETR-based detectors to get table boxes & cell grid,
* OCRs each cell (Tesseract) when text is missing,
* outputs a *logical* table including `rowspan`/`colspan`. ([codesphere.com][4], [GitHub][5])

## 4  Merge everything into one canonical schema for markdown

```python
from pathlib import Path, PurePath
import pandas as pd, json, uuid, itertools

def canonise(camelot_table):
    df = camelot_table.df
    bbox = camelot_table._bbox  # (x1,y1,x2,y2)
    return {"id": uuid.uuid4().hex,
            "source": "camelot",
            "page": camelot_table.page,
            "bbox": bbox,
            "cells": df.fillna("").values.tolist()}

def canonise_gmft(record):
    return {"id": record["table_id"],
            "source": "gmft",
            "page": record["page"],
            "bbox": record["bbox"],
            "cells": record["cells"]}

canon = []
for t in tables_lat + tables_str: canon.append(canonise(t))
for rec in json.load(open("out/tables.json")): canon.append(canonise_gmft(rec))

# de-dupe: IoU > 0.6 → keep the higher-resolution version
def iou(b1, b2):
    x1,y1,x2,y2 = b1; a1,b1,a2,b2 = b2
    # compute intersection/union …
```

---

## 5  Post-process for perfect structure

1. **Row/col spans**
   *Camelot* gives flat data; GMFT gives structural spans.

   * For Camelot tables: detect identical neighbouring cell text → merge horizontally; detect identical column values across rows → merge vertically.
   * Add pseudo-HTML `<td rowspan="…">` / `<td colspan="…">` attributes in the canonical dict.

2. **Export**

   ```python
   pd.DataFrame(table["cells"]).to_csv("table-01.csv", index=False)
   # or
   import markdown_table
   markdown_table.write_table(table["cells"], "table-01.md")
   ```

3. **Embed back into your doc-parser**

   * Save JSON with page, bbox and HTML so you can surface the *exact* location in a front-end viewer.
   * Store the cleaned CSV beside the raw‐text chunk in your RAG store so the LLM can decide whether to answer from prose or structured data.

---

## 6  Confidence scoring & fallback logic

| Scenario                                        | What you keep                             | Why                                       |
| ----------------------------------------------- | ----------------------------------------- | ----------------------------------------- |
| Camelot **and** GMFT agree on cell count ±5 %   | Camelot (faster)                          | vector data is reliable                   |
| Camelot finds ≤1 table or high empty-cell ratio | GMFT                                      | Camelot probably missed borderless/B-scan |
| Both low quality                                | Trigger manual review or LLM-based re-OCR |                                           |

---

## 7  Evaluate & iterate

```bash
# GriTS metric (Table-Transformer)
python -m tatr_grits --pred tables.json --gt ground_truth.json
# Quick eyeball
gmft viz my.pdf --pred tables.json --out viz/
```

*Aim for > 0.9 GriTS on native PDFs and > 0.8 on scans.*

---

### Recap

* **Camelot → pdfplumber** gives you lightning-fast, high-precision extraction on well-formed, vector PDFs.
* **GMFT (Table Transformer)** fills the gap on scans, photos, vector-as-image tables and deeply nested grids.
* A thin **de-duplication & span-repair layer** unifies both outputs, so downstream code sees a single, clean schema.

With this hybrid stack we can throw *any* table—line-ruled, borderless, multi-rowspan, or even photographed—into the pipe and get back faithful CSV/HTML in seconds. 
