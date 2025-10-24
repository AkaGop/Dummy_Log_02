# log_parser.py
import re
from io import StringIO
from config import CEID_MAP, RPTID_MAP
from parser_utils import tokenize, build_tree

def _find_ceid(tree):
    """Recursively search for the first valid CEID in the tree."""
    if isinstance(tree, str) and tree.isdigit():
        ceid_candidate = int(tree)
        if ceid_candidate in CEID_MAP:
            return ceid_candidate
    if isinstance(tree, list):
        for item in tree:
            result = _find_ceid(item)
            if result is not None:
                return result
    return None

def _find_values(tree, rptid_val=None):
    """
    Recursively search the parsed tree for a specific RPTID and return its
    corresponding value list (payload).
    """
    if isinstance(tree, list):
        if len(tree) > 1 and tree[0] == str(rptid_val):
            return tree[1]
        for item in tree:
            result = _find_values(item, rptid_val)
            if result is not None:
                return result
    return None

def _parse_s6f11_report(full_text: str) -> dict:
    """
    Parses an S6F11 message by tokenizing, building a tree, and then
    safely traversing the tree to find the CEID, RPTID, and data payload.
    """
    data = {}
    try:
        tokens = tokenize(full_text)
        tree = build_tree(tokens)
        if not tree: return {}

        ceid = _find_ceid(tree)

        if ceid:
            data['CEID'] = ceid
            if "Alarm" in CEID_MAP.get(ceid, ''): data['AlarmID'] = ceid

            for rptid_val in RPTID_MAP:
                payload = _find_values(tree, rptid_val)
                if payload:
                    data['RPTID'] = rptid_val
                    field_names = RPTID_MAP.get(rptid_val, [])
                    for i, name in enumerate(field_names):
                        if i < len(payload): data[name] = payload[i]
                    break

    except (IndexError, ValueError, TypeError):
        pass
    return data

def _parse_s2f49_command(full_text: str) -> dict:
    data = {}
    rcmd = re.search(r"<\s*A\s*\[\d+\]\s*'([A-Z_]{5,})'", full_text)
    if rcmd: data['RCMD'] = rcmd.group(1)
    lotid = re.search(r"'LOTID'\s*>\s*<A\[\d+\]\s*'([^']*)'", full_text, re.IGNORECASE)
    if lotid: data['LotID'] = lotid.group(1)
    panels = re.search(r"'LOTPANELS'\s*>\s*<L\s*\[(\d+)\]", full_text, re.IGNORECASE)
    if panels: data['PanelCount'] = int(panels.group(1))
    return data

def parse_log_file(uploaded_file):
    events = []
    if not uploaded_file: return events
    try: lines = StringIO(uploaded_file.getvalue().decode("utf-8")).readlines()
    except: lines = StringIO(uploaded_file.getvalue().decode("latin-1", errors='ignore')).readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        header = re.match(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+),\[([^\]]+)\],(.*)", line)
        if not header: i += 1; continue
        ts, log_type, msg_part = header.groups()
        msg_match = re.search(r"MessageName=(\w+)|Message=.*?:\'(\w+)\'", msg_part)
        msg_name = (msg_match.group(1) or msg_match.group(2)) if msg_match else "N/A"
        event = {"timestamp": ts, "msg_name": msg_name}
        if ("Core:Send" in log_type or "Core:Receive" in log_type) and i+1 < len(lines) and lines[i+1].strip().startswith('<'):
            j = i + 1; block = []
            while j < len(lines) and lines[j].strip() != '.': block.append(lines[j]); j += 1
            i = j
            if block:
                text = "".join(block)
                details = {}
                if msg_name == 'S6F11': details = _parse_s6f11_report(text)
                elif msg_name == 'S2F49': details = _parse_s2f49_command(text)
                if details: event['details'] = details
        if 'details' in event: events.append(event)
        i += 1
    return events
