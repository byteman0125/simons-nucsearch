from __future__ import annotations
from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from .forms import RegexForm
from .efetch import get_sequence
from .regex_search import iter_regex_matches

NUC_ID = '30271926'
CACHE_KEY_SEQ = f'nucseq:{NUC_ID}'


def index(request: HttpRequest) -> HttpResponse:
    # Fetch or cache the nucleotide sequence for Part 1
    seq = cache.get(CACHE_KEY_SEQ)
    if not seq:
        seq = get_sequence(NUC_ID)
        cache.set(CACHE_KEY_SEQ, seq, timeout=60 * 60)  # 1 hour

    pattern = request.GET.get('pattern', '').strip()
    form = RegexForm(initial={'pattern': pattern} if pattern else None)

    results = []
    error = None
    if pattern:
        try:
            matches = list(iter_regex_matches(seq, pattern))
            # Build display tuples (index, match, left_context, right_context)
            context_radius = 20
            for idx, m in matches:
                start = max(0, idx - context_radius)
                end = min(len(seq), idx + len(m) + context_radius)
                left = seq[start:idx]
                right = seq[idx + len(m):end]
                results.append({
                    'index': idx,
                    'match': m,
                    'left': left,
                    'right': right,
                })
        except Exception as e:
            error = str(e)

    paginator = Paginator(results, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search/index.html', {
        'form': form,
        'sequence_len': len(seq),
        'page_obj': page_obj,
        'pattern': pattern,
        'error': error,
    })
