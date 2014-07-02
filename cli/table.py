def menu(title, *items, **options):
    """
    Creates a menu, asking the user to select an option, then returns that
    option.

    title: string, the title of the menu.
    *items: list, the menu items to display; multiple lists are acceptable.
    **headers: list, column headers for each column in items.
    **footer: string, the footer to display before the prompt at the bottom.
    **input_range: list, a list of acceptable inputs; if user input string is
                   not in this list, input is rejected.
    """
    headers = options["headers"] if "headers" in options.keys() else None
    footer = options["footer"] if "footer" in options.keys() else None
    input_range = [str(i) for i in options["input_range"]] if "input_range"   \
                   in options.keys() else None

    table(title, *items, headers=headers, footer=footer)

    choice = raw_input(">> ")
    while input_range and not choice in input_range:
        choice = raw_input(">> ")

    return choice


def table(title, *columns, **options):
    """
    Creates a table.
    title: string, the title of the table.
    *columns: tuples, with each tuple representing a column (and each item in
              each tuple representing a cell in the table).
    **headers: list, column headers for each column in items.
    **footer: string, the footer to display before the prompt at the bottom.
    """
    headers = options["headers"] if "headers" in options.keys() else None
    footer = options["footer"] if "footer" in options.keys() else None

    column_widths = [max(max([len(str(item)) for item in c]), 1) for c in
                     columns]
    if headers:
        column_widths = [max(w) for w in zip(column_widths, [len(h) for h in
                         headers])]

    total_width = sum(column_widths) + (3 * (len(column_widths) - 1))
    if total_width < len(title):
        diff = len(title) - total_width
        column_widths[0] += diff
        total_width += diff

    rows = zip(*columns)

    print "+{}+".format("-" * (total_width + 2))
    print "| {:^{}} |".format(title, total_width)

    dividers = ["-" * (w + 2) for w in column_widths]
    print "+{}+".format("+".join(dividers))

    if headers:
        cells = [" {:{}} |".format(*column_width) for column_width in
                 zip(headers, column_widths)]
        print "".join(["|"] + cells)
        print "+{}+".format("+".join(dividers))

    for row in rows:
        cells = [" {:{}} |".format(*column_width) for column_width in zip(row,
                 column_widths)]
        print "".join(["|"] + cells)

    print "+{}+".format("+".join(dividers))

    if footer:
        print footer


