import argparse
import os

from gitcodechurn.exporters import ExporterFactory
from gitcodechurn.git import Git
from gitcodechurn.churn import calculate_statistics


def main():
    parser = argparse.ArgumentParser(
        description = 'Compute true git code churn to understand tech debt.',
        usage       = 'python [*/]gitcodechurn.py after="YYYY[-MM[-DD]]" before="YYYY[-MM[-DD]]" author="flacle" dir="[*/]path" [-exdir="[*/]path"]',
        epilog      = 'Feel free to fork at or contribute on: https://github.com/Scoppio/truegitcodechurn'
    )
    parser.add_argument(
        'dir',
        type = dir_path,
        default = '',
        help = 'the Git repository root directory to be included'
    )
    parser.add_argument(
        '--after',
        default = '1970-01-01',
        required=False,
        type = str,
        help = 'search after a certain date, in YYYY[-MM[-DD]] format'
    )
    parser.add_argument(
        '--before',
        default = '9999-01-01',
        required=False,
        type = str,
        help = 'search before a certain date, in YYYY[-MM[-DD]] format'
    )
    parser.add_argument(
        '--author',
        required=False,
        type = str,
        default = '',
        help = 'an author (non-committer), leave blank to scope all authors'
    )
    parser.add_argument(
        '-exdir',
        metavar='',
        type = str,
        default = '',
        help = 'the Git repository subdirectory to be excluded'
    )
    parser.add_argument(
        "--show-file-data",
        action="store_true",
        help="Display LINE change information for the analyzed file(s)"
    )
    parser.add_argument(
        "--aggregate-file-data",
        action="store_true",
        help="Display FILE change information for the analyzed file(s)"
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="prints output as csv"
    )
    args = parser.parse_args()

    after  = args.after
    before = args.before
    author = args.author
    project_dir = args.dir
    exdir  = args.exdir

    commits = Git.get_commits(before, after, author, project_dir)

    files, contribution, churn = calculate_statistics(commits, project_dir, exdir)

    # if author is empty then print a unique list of authors
    if len(author.strip()) == 0:
        print('# authors: \t', Git.authors(before, after, author, project_dir))
    else:
        print('# author: \t', author)
    
    print('# contribution: \t', contribution)
    print('# churn: \t\t', -churn)
    
    if args.show_file_data:
        ExporterFactory.get_exporter(args).display_file_metrics(files)

    if args.aggregate_file_data:
        ExporterFactory.get_exporter(args).display_file_aggregate_metrics(files)


# https://stackoverflow.com/a/54547257
def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(path + " is not a valid path.")


if __name__ == '__main__':
    main()
