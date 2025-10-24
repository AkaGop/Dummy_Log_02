# parser_utils.py
import re

def tokenize(text):
    """
    A robust tokenizer that uses a general pattern to find value-tags,
    then a second pattern to extract the value from the tag.
    """
    token_specification = [
        ('LIST_START', r'<\s*L\s*\[\d+\]'),
        ('LIST_END',   r'>'),
        # A general regex to find any value-like tag (e.g., <A...>, <B...>, <U4...>)
        ('VALUE',      r"<\s*[A-Z]\d*\s*\[\d+\]\s*.*?>"),
        ('SKIP',       r'[\s\n]+'),
    ]

    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        if kind == 'SKIP':
            continue

        if kind == 'VALUE':
            # After matching a general value-tag, extract the actual value,
            # which is either a quoted string or an unquoted value near the end.
            value_text = mo.group(kind)
            val_match = re.search(r"'(.*)'\s*>$|([^\s>]+)\s*>$", value_text)
            if val_match:
                # Group 1 is the quoted string, group 2 is the unquoted value.
                yield 'VALUE', val_match.group(1) or val_match.group(2)
        else: # LIST_START or LIST_END
            yield kind, mo.group(kind)

def build_tree(tokens):
    """Builds a nested Python list from a stream of tokens."""
    stack = [[]]
    for kind, value in tokens:
        if kind == 'LIST_START':
            new_list = []
            stack[-1].append(new_list)
            stack.append(new_list)
        elif kind == 'LIST_END':
            if len(stack) > 1:
                stack.pop()
        elif kind == 'VALUE':
            stack[-1].append(value)
    return stack[0]
