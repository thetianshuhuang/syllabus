

import print as p


def print_tree(tree, tier=0):

    if tree["start_time"] is not None:
        print(
            "<{name}> {desc}".format(
                name=tree["name"], desc=tree["desc"]))

    for msg in tree["events"]:
        print(msg)

    if tree["end_time"] is not None:
        print(
            p.render("  | " * tier, p.BR + p.BLACK) +
            p.render("[todo]", p.BR + p.GREEN, p.BOLD))
