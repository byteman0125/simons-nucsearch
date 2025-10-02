from __future__ import annotations
from django.core.management.base import BaseCommand, CommandParser
import sys
from typing import Iterable
from search.efetch import fetch_fasta_text
from search.regex_search import (
    stream_sequence_from_fasta_lines,
    stream_regex_matches_over_sequence_chunks,
)


def iter_sequence_chunks(resp, chunk_size: int) -> Iterable[str]:
    buf = ''
    for raw in resp.iter_lines(decode_unicode=True):
        if raw is None:
            continue
        line = raw + '\n'
        buf += line
        if len(buf) >= chunk_size:
            yield from stream_sequence_from_fasta_lines(buf.splitlines())
            buf = ''
    if buf:
        yield from stream_sequence_from_fasta_lines(buf.splitlines())


class Command(BaseCommand):
    help = 'Stream regex matches over NCBI nucleotide FASTA (EFetch)'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--id', default='224589800', help='NCBI nucleotide ID (default: 224589800)')
        parser.add_argument('--pattern', required=True, help='Python regex pattern')
        parser.add_argument('--output', default='-', help='Output TSV path or - for stdout (default)')
        parser.add_argument('--chunk-size', type=int, default=1_000_000, help='Streaming chunk size (chars)')
        parser.add_argument('--overlap', type=int, default=100, help='Overlap between chunks to catch boundary matches')

    def handle(self, *args, **options):
        nuc_id = options['id']
        pattern = options['pattern']
        output = options['output']
        chunk_size = options['chunk_size']
        overlap = options['overlap']

        resp = fetch_fasta_text(nuc_id)
        chunks = iter_sequence_chunks(resp, chunk_size)
        matches = stream_regex_matches_over_sequence_chunks(chunks, pattern, overlap=overlap)

        out_fh = sys.stdout if output == '-' else open(output, 'w', encoding='utf-8')
        try:
            for idx, m in matches:
                out_fh.write(f"{idx}\t{m}\n")
        finally:
            if out_fh is not sys.stdout:
                out_fh.close()
