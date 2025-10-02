from __future__ import annotations
import re
from typing import Iterable, Iterator, Tuple


def iter_regex_matches(seq: str, pattern: str) -> Iterator[Tuple[int, str]]:
    regex = re.compile(pattern, re.IGNORECASE)
    for m in regex.finditer(seq):
        yield m.start(), m.group(0)


def stream_sequence_from_fasta_lines(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        if line.startswith('>'):
            continue
        yield ''.join(ch for ch in line.strip() if ch.isalpha()).upper()


def stream_regex_matches_over_sequence_chunks(chunks: Iterable[str], pattern: str, overlap: int = 100) -> Iterator[Tuple[int, str]]:
    regex = re.compile(pattern, re.IGNORECASE)
    buffer = ''
    offset = 0
    last_match_end = 0
    
    for chunk in chunks:
        window = buffer + chunk
        buffer_len = len(buffer)
        
        for m in regex.finditer(window):
            abs_pos = offset + m.start()
            if abs_pos >= last_match_end:
                yield abs_pos, m.group(0)
                last_match_end = abs_pos + len(m.group(0))
        
        if overlap > 0 and len(window) > overlap:
            buffer = window[-overlap:]
            offset += len(window) - overlap
        else:
            buffer = ''
            offset += len(window)
