from __future__ import annotations
import re
import requests
from xml.etree import ElementTree as ET

EFETCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'


def fetch_nucleotide_xml_fasta(nuc_id: str) -> str:
    params = {
        'db': 'nucleotide',
        'id': nuc_id,
        'rettype': 'fasta',
        'retmode': 'xml',
    }
    r = requests.get(EFETCH_URL, params=params, timeout=60)
    r.raise_for_status()
    return r.text


def parse_sequence_from_efetch_xml(xml_text: str) -> str:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        root = None

    seq = ''
    if root is not None:
        tseq_seq = root.find('.//TSeq/TSeq_sequence')
        if tseq_seq is not None and (tseq_seq.text or '').strip():
            seq = tseq_seq.text.strip()
        else:
            insd_seq = root.find('.//INSDSeq/INSDSeq_sequence')
            if insd_seq is not None and (insd_seq.text or '').strip():
                seq = insd_seq.text.strip()

    if not seq:
        m = max(re.findall(r'[ACGTNacgtn]+', xml_text), key=len, default='')
        seq = m

    return re.sub(r'\s+', '', seq).upper()


def get_sequence(nuc_id: str) -> str:
    xml_text = fetch_nucleotide_xml_fasta(nuc_id)
    return parse_sequence_from_efetch_xml(xml_text)


def fetch_fasta_text(nuc_id: str) -> requests.Response:
    params = {
        'db': 'nucleotide',
        'id': nuc_id,
        'rettype': 'fasta',
        'retmode': 'text',
    }
    r = requests.get(EFETCH_URL, params=params, timeout=180, stream=True)
    r.raise_for_status()
    return r
