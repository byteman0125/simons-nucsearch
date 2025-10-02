# Simons Nucleotide Search

A two-part project:

- Part 1: Django web app to fetch a nucleotide (NCBI EFetch API) and search for regex patterns within its sequence.
- Part 2: CLI utility to process a large nucleotide record and report regex match positions, suitable for very large inputs.

## Tech stack

- Django 5.x
- Python 3.10+
- requests

Optional (not required to run basic project):
- lxml (fallback parser; stdlib `xml.etree` is used by default)

## Setup

1) Create and activate a virtualenv (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Run Django app (Part 1)

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Open http://localhost:8000/

- Enter a regex pattern, e.g. `(AATCGA|GGCAT)` and submit.
- Results show match index (0-based), matched text, and a small context window.

EFetch request used:
- db: `nucleotide`
- id: `30271926`
- rettype: `fasta`
- retmode: `xml`

3) Run CLI (Part 2)

The CLI downloads ID `224589800` (~238MB) and streams regex matches without loading into memory.

```bash
python cli/search_nucleotide.py --id 224589800 --pattern "(AATCGA|GGCAT)" --output results.tsv
```

Options:
- `--id` NCBI nucleotide ID (default: 224589800)
- `--pattern` Python regex (required)
- `--output` path to write TSV (default: stdout)
- `--chunk-size` stream chunk size (default: 1_000_000)
- `--overlap` overlap size to catch cross-chunk matches (default: 100)

Output TSV columns:
- index (0-based)
- match

4) Tests / Quick checks

- Try different patterns: `A{5,}`, `ATG(?:...){10}TAA` (note: Python-style regex)
- For very large patterns, consider increasing `--chunk-size` and `--overlap`.

## Design notes

- EFetch client (`search/efetch.py`) centralizes network logic.
- XML parsing: attempts to extract sequence from known EFetch XML shapes (`TSeq/TSeq_sequence`, `INSDSeq/INSDSeq_sequence`). Falls back to scanning for the longest plausible ACGTN-only sequence.
- Web part caches the fetched sequence in Django local memory cache to avoid repeated downloads during a session.
- CLI streams the response and performs chunked regex matching with overlap to avoid missing cross-boundary matches.

## Limitations & future improvements

- No database is used; results are computed on demand. Could add persistence for caching and audit.
- For even larger datasets or many concurrent users, Celery can offload regex searches.
- React front-end could improve visualization (highlighting, interactive navigation).
- Add tests (pytest) and CI.

## License

MIT
