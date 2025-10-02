# Simons Nucleotide Search

Django web app and CLI for searching nucleotide sequences using regex patterns via NCBI EFetch API.

## Requirements

- Python 3.10+
- Django 5.x
- requests

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://localhost:8000 and enter a regex pattern like `(AATCGA|GGCAT)`.

## Part 1: Web App

- Fetches nucleotide ID `30271926` (30KB) from NCBI
- EFetch params: `db=nucleotide`, `rettype=fasta`, `retmode=xml`
- Shows paginated results with context windows
- Caches sequence for 1 hour

## Part 2: CLI

Process large sequences (e.g., ID `224589800`, 238MB) with streaming:

```bash
python cli/search_nucleotide.py --id 224589800 --pattern "(AATCGA|GGCAT)" --output results.tsv
```

Or as Django management command:

```bash
python manage.py search_nucleotide --id 224589800 --pattern "(AATCGA|GGCAT)"
```

Options: `--id`, `--pattern`, `--output`, `--chunk-size`, `--overlap`

## Design

**Part 1:**
- Caches 30KB sequence in memory for 1 hour
- Parses XML from EFetch (tries `TSeq/TSeq_sequence` and `INSDSeq/INSDSeq_sequence`)
- Paginated results with 20bp context windows

**Part 2:**
- Streams FASTA data in 1MB chunks with 100bp overlap
- Prevents duplicate matches in overlap regions
- O(1) memory usage regardless of sequence size

## Scalability

Part 1 won't scale to 238MB datasets:
- Would load entire sequence into memory
- Slow regex search on large strings
- Memory exhaustion with concurrent users

**Production improvements:**
- PostgreSQL for sequence storage and indexing
- Celery for async background processing
- React frontend with real-time results
- Memcached for distributed caching
- Unit tests and CI/CD
