import nikola


def patch_module(module, processor_fn):
    with open(module.__file__, encoding='utf-8') as f:
        in_lines = f.readlines()

    with open(module.__file__, 'w', encoding='utf-8') as f:
        f.writelines(processor_fn(in_lines))


def process_utils(lines):
    in_func = False
    out_lines = []

    for line in lines:
        out_lines.append(line)
        if line.startswith('def to_datetime('):
            in_func = True
        elif line.startswith('def '):
            in_func = False

        if not in_func:
            continue

        if line.strip() == 'try:':
            out_lines.extend([
                '        if isinstance(value, datetime.date):\n',
                '            value = datetime.datetime.combine(value, datetime.datetime.min.time())\n',
            ])

    return out_lines


if __name__ == '__main__':
    patch_module(nikola.utils, process_utils)
