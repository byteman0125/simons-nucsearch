from __future__ import annotations
import re
from typing import Iterable, Iterator, Tuple


def iter_regex_matches(seq: str, pattern: str) -> Iterator[Tuple[int, str]]:
    regex = re.compile(pattern)
    for m in regex.finditer(seq):
        yield m.start(), m.group(0)


def stream_sequence_from_fasta_lines(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        if line.startswith('>'):
            continue
        yield ''.join(ch for ch in line.strip() if ch.isalpha()).upper()


def stream_regex_matches_over_sequence_chunks(chunks: Iterable[str], pattern: str, overlap: int = 100) -> Iterator[Tuple[int, str]]:
    regex = re.compile(pattern)
    buffer = ''
    offset = 0
    for chunk in chunks:
        window = buffer + chunk
        start_pos = 0
        for m in regex.finditer(window):
            yield offset + m.start(), m.group(0)
        # prepare buffer for next chunk
        if overlap > 0:
            buffer = window[-overlap:]
        else:
            buffer = ''
        offset += len(window) - len(buffer)
    # final scan of remaining buffer (no new offset advance)
    if buffer:
        for m in regex.finditer(buffer):
            yield offset + m.start(), m.group(0)
