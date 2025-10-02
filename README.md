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

**Standalone script:**
```bash
python cli/search_nucleotide.py --id 224589800 --pattern "(AATCGA|GGCAT)" --output results.tsv
```

**Or as Django management command:**
```bash
python manage.py search_nucleotide --id 224589800 --pattern "(AATCGA|GGCAT)" --output results.tsv
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

## Architecture & Design Decisions

### Part 1: Django Web App

**Architecture:**
- **EFetch client** (`search/efetch.py`): Centralized module for NCBI API calls with proper error handling
- **Regex search** (`search/regex_search.py`): Reusable regex matching logic shared between web and CLI
- **Caching**: Django's `LocMemCache` stores the fetched sequence (30KB) for 1 hour to avoid redundant API calls
- **Pagination**: Django's built-in paginator displays 25 results per page for better UX
- **Context display**: Shows 20bp on each side of matches for visual verification

**Why this approach:**
- Simple, stateless design suitable for the small dataset (30KB)
- No database needed for Part 1 since results are computed on-the-fly
- Caching prevents rate-limiting issues during development/testing
- Standard Django patterns make the code maintainable

**XML parsing strategy:**
- Tries known EFetch XML structures (`TSeq/TSeq_sequence`, `INSDSeq/INSDSeq_sequence`)
- Falls back to regex extraction of longest ACGTN sequence if structure changes
- Robust against API format variations

### Part 2: CLI for Large Datasets

**Architecture:**
- **Streaming**: Uses `requests.iter_lines()` to avoid loading 238MB into memory
- **Chunked processing**: Processes sequence in 1MB chunks with configurable overlap
- **Overlap buffer**: Maintains 100bp overlap between chunks to catch cross-boundary matches
- **Deduplication**: Tracks `last_match_end` position to prevent duplicate matches in overlap regions

**Why this approach:**
- Memory-efficient: Can handle arbitrarily large sequences
- Scalable: O(1) memory complexity regardless of input size
- Accurate: Overlap ensures no matches are missed at chunk boundaries
- Fast: Streams and processes simultaneously without waiting for full download

**Trade-offs:**
- Overlap size must be >= max expected match length
- For very complex regex with long matches, may need to increase overlap
- No random access to sequence (streaming only)

### Scalability Analysis

**Would Part 1 work with Part 2's dataset (238MB)?**

No, not efficiently:
- Loading 238MB into memory would be slow and wasteful
- Cache would consume significant memory
- Regex search on 238MB string could take seconds per query
- Multiple concurrent users would exhaust memory

**Improvements for production:**

1. **Database integration** (PostgreSQL):
   - Store sequences and pre-computed match indices
   - Use full-text search or trigram indexes for common patterns
   - Cache results in database for repeat queries

2. **Async processing** (Celery):
   - Offload long-running searches to background workers
   - Return task ID immediately, poll for results
   - Support email notification when complete

3. **Advanced features**:
   - React frontend with syntax highlighting and interactive navigation
   - WebSocket for real-time streaming results
   - Pattern validation and suggestions
   - Export to various formats (JSON, CSV, BED)

4. **Performance optimizations**:
   - Memcached for distributed caching
   - Multiprocessing for parallel regex search on large sequences
   - Pre-fetch and index frequently accessed sequences

5. **Testing & CI**:
   - Unit tests for regex logic, edge cases
   - Integration tests for EFetch API
   - Performance benchmarks
   - GitHub Actions CI/CD

## Limitations

- No database persistence
- No user authentication or rate limiting
- No input validation beyond basic regex compilation
- CLI doesn't handle network interruptions gracefully
- No progress indicators for long-running searches

## License

MIT
