#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sys
from typing import Iterable
from search.efetch import fetch_fasta_text
from search.regex_search import stream_sequence_from_fasta_lines, stream_regex_matches_over_sequence_chunks


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


def main(argv=None):
    p = argparse.ArgumentParser(description='Stream regex matches over NCBI nucleotide FASTA')
    p.add_argument('--id', default='224589800', help='NCBI nucleotide ID (default: 224589800)')
    p.add_argument('--pattern', required=True, help='Python regex pattern')
    p.add_argument('--output', default='-', help='Output TSV path or - for stdout (default)')
    p.add_argument('--chunk-size', type=int, default=1_000_000, help='Streaming chunk size (chars)')
    p.add_argument('--overlap', type=int, default=100, help='Overlap size between chunks to catch boundary matches')
    args = p.parse_args(argv)

    resp = fetch_fasta_text(args.id)

    chunks = iter_sequence_chunks(resp, args.chunk_size)
    matches = stream_regex_matches_over_sequence_chunks(chunks, args.pattern, overlap=args.overlap)

    out_fh = sys.stdout if args.output == '-' else open(args.output, 'w', encoding='utf-8')
    try:
        for idx, m in matches:
            out_fh.write(f"{idx}\t{m}\n")
    finally:
        if out_fh is not sys.stdout:
            out_fh.close()

if __name__ == '__main__':
    main()
