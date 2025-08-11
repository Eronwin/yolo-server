import argparse
from multiprocessing.spawn import freeze_support

from backend.cmd.start import setup_start_cmd
from backend.cmd.version import setup_version_cmd


def main():
    parser = argparse.ArgumentParser(
        conflict_handler="resolve",
        add_help=True,
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=55, indent_increment=2, width=200
        ),
    )
    subparsers = parser.add_subparsers(
        help="sub-command help", metavar="{start,version}"
    )

    setup_start_cmd(subparsers)
    setup_version_cmd(subparsers)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    freeze_support()
    main()
