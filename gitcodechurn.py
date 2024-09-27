'''
Author: Francis Laclé
License: MIT
Version: 1.0.1

Script to compute "true" code churn of a Git repository.

Code churn has several definitions, the one that to me provides the
most value as a metric is:

"Code churn is when an engineer rewrites their own code in a short time period."

Reference: https://blog.gitprime.com/why-code-churn-matters/

This lightweight script looks at commits per author for a given date range on
the default branch. For each commit it bookkeeps the files that were changed
along with the lines of code (LOC) for each file. LOC are kept in a sparse
structure and changes per LOC are taken into account as the program loops. When
a change to the same LOC is detected it updates this separately to bookkeep the
true code churn.

Result is a print with aggregated contribution and churn per author for a
given time period.

Tested with Python version 3.5.3 and Git version 2.20.1

'''

import argparse
import datetime
import os
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description = 'Compute true git code churn to understand tech debt.',
        usage       = 'python [*/]gitcodechurn.py after="YYYY[-MM[-DD]]" before="YYYY[-MM[-DD]]" author="flacle" dir="[*/]path" [-exdir="[*/]path"]',
        epilog      = 'Feel free to fork at or contribute on: https://github.com/flacle/truegitcodechurn'
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
        '--since-last-year',
        type = str,
        help = 'automatically only checks the last 12 months of commits'
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
        help="Display line change information for the analyzed file(s)"
    )
    parser.add_argument(
        "--aggregate-file-data",
        action="store_true",
        help="Display file change information for the analyzed file(s)"
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
    project_dir    = args.dir
    exdir  = args.exdir
    
    if args.since_last_year:
        after = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')

    commits = get_commits(before, after, author, project_dir)

    files, contribution, churn = calculate_statistics(commits, project_dir, exdir)

    # if author is empty then print a unique list of authors
    if len(author.strip()) == 0:
        authors = set(get_commits(before, after, author, project_dir, '%an')).__str__()
        authors = authors.replace('{', '').replace('}', '').replace("'","")
        print('# authors: \t', authors)
    else:
        print('# author: \t', author)
    print('# contribution: \t', contribution)
    print('# churn: \t\t', -churn)
    # print files in case more granular results are needed
    #print('files: ', files)

    if args.show_file_data:
        ExporterFactory.get_exporter(args.csv).display_file_metrics(files)

    if args.aggregate_file_data:
        ExporterFactory.get_exporter(args.csv).display_file_aggregate_metrics(files)


class ExporterFactory:

    @classmethod
    def get_exporter(cls, csv):
        if csv:
            return CsvExporter
        return Exporter


class CsvExporter:

    @classmethod
    def display_file_metrics(cls, files):
        cls.display_file_metrics_header()
        for file_name, line_change_info in files.items():
            for line_number, line_diff_stats in line_change_info.items():
                cls.display_file_metrics_row(file_name, line_number, line_diff_stats)
    
    @classmethod
    def display_file_aggregate_metrics(cls, files):
        cls.display_file_metrics_header()
        for file_name, line_change_info in files.items():
            added = 0
            removed = 0
            number_of_changes = 0
            for _, line_diff_stats in line_change_info.items():
                added += line_diff_stats.get("lines_added")
                removed += line_diff_stats.get("lines_removed")
                number_of_changes += 1
            cls.display_file_metrics_row(file_name, "TOTAL", {"lines_added": added, "lines_removed": removed, "number_of_changes": number_of_changes})
    
    @classmethod
    def display_file_metrics_header(cls):
        print("FILE NAME,LINE #,ADDED,REMOVED,LINES CHANGED")
    
    @classmethod
    def display_file_metrics_row(cls, file_name, line_number, line_diff_stats):
        added = line_diff_stats.get("lines_added")
        removed = line_diff_stats.get("lines_removed")
        changes = line_diff_stats.get("number_of_changes", 1)
        if added == 0 and removed == 0:
            return
        print(
            "{file},{ln},{lines_added},{lines_removed},{number_of_changes}".format(
                file=file_name,
                ln=line_number,
                lines_added=added,
                lines_removed=removed,
                number_of_changes=changes
            )
        )


class Exporter:

    @classmethod
    def display_file_metrics(cls, files):
        cls.display_file_metrics_header()
        for file_name, line_change_info in files.items():
            for line_number, line_diff_stats in line_change_info.items():
                cls.display_file_metrics_row(file_name, line_number, line_diff_stats)


    @classmethod
    def display_file_aggregate_metrics(cls, files):
        cls.display_file_metrics_header()
        for file_name, line_change_info in files.items():
            added = 0
            removed = 0
            number_of_changes = 0
            for _, line_diff_stats in line_change_info.items():
                added += line_diff_stats.get("lines_added")
                removed += line_diff_stats.get("lines_removed")
                number_of_changes += 1
            cls.display_file_metrics_row(file_name, "TOTAL", {"lines_added": added, "lines_removed": removed, "number_of_changes": number_of_changes})

    @classmethod
    def display_file_metrics_header(cls):
        print("-" * 79)
        print(
            "{file}|{line_number}|{lines_added}|{lines_removed}|{number_of_changes}".format(
                file=cls.format_column("FILE NAME", 34),
                line_number=cls.format_column("LINE #", 10),
                lines_added=cls.format_column("ADDED", 10),
                lines_removed=cls.format_column("REMOVED", 10),
                number_of_changes=cls.format_column("LINES CHANGED", 15)
            )
        )

    @classmethod
    def display_file_metrics_row(cls, file_name, line_number, line_diff_stats):
        added = line_diff_stats.get("lines_added")
        removed = line_diff_stats.get("lines_removed")
        changes = line_diff_stats.get("number_of_changes", "-")
        if added == 0 and removed == 0:
            return
        print("-" * 79)
        print(
            "{file}|{ln}|{lines_added}|{lines_removed}|{number_of_changes}".format(
                file=cls.format_column(file_name, 34),
                ln=cls.format_column(str(line_number), 10),
                lines_added=cls.format_column(str(added), 10),
                lines_removed=cls.format_column(str(removed), 10),
                number_of_changes=cls.format_column(str(changes), 10)
            )
        )

    @classmethod
    def format_column(cls, text, width):
        text_length = len(text)
        total_pad = width - text_length
        pad_left = total_pad // 2
        pad_right = total_pad - pad_left
        return (" " * pad_left) + text + (" " * pad_right)


def calculate_statistics(commits, project_dir, exdir):
    # structured like this: files -> LOC
    files = {}

    contribution = 0
    churn = 0

    for commit in commits:
        [files, contribution, churn] = get_loc(
            commit,
            project_dir,
            files,
            contribution,
            churn,
            exdir
        )

    return files, contribution, churn
    
def get_commit_results(command, project_dir):
    return get_proc_out(command, project_dir).splitlines()

def get_loc(commit, project_dir, files, contribution, churn, exdir):
    # git show automatically excludes binary file changes
    command = 'git show --format= --unified=0 --no-prefix ' + commit
    if len(exdir) > 1:
        # https://stackoverflow.com/a/21079437
        command += ' -- . ":(exclude,icase)'+exdir+'"'
    results = get_commit_results(command, project_dir) 
    file = ''
    loc_changes = ''

    # loop through each row of output
    for result in results:
        new_file = is_new_file(result, file)
        if file != new_file:
            file = new_file
            if file not in files:
                files[file] = {}
        else:
            new_loc_changes = is_loc_change(result, loc_changes)
            if loc_changes != new_loc_changes:
                loc_changes = new_loc_changes
                (removal, addition) = get_loc_change(loc_changes)

                files, contribution, churn = merge_operations(removal, addition, files, contribution, churn, file)
            else:
                continue
    return [files, contribution, churn]


def merge_operations(removal, addition, files, contribution, churn, file):
    # Ensure all required data is in place
    ensure_file_exists(files, file)

    file_line_churn_dict = files[file]

    if is_noop(removal, addition):
        # In the case of a noop, it's not counted in change metrics, but should
        # be marked as changed to accurately include future churn metrics
        # An example of this is a diff like:
        #   "diff --git README.md README.md",
        #   "index bedbc85..bb033cd 100644",
        #   "--- README.md",
        #   "+++ README.md",
        #   "@@ -8 +8 @@ Code churn has several definitions, the one that to me provides the most value a",
        #   "-*Reference: https://www.pluralsight.com/blog/teams/why-code-churn-matters*",
        #   "+*Reference: http://web.archive.org/web/20220312170931/https://www.pluralsight.com/blog/teams/why-code-churn-matters*"
        # In this example, we deleted the line, and then added the line by updating the link
        # This repo would consider this a "No-Op" as it nets to no change
        # However, we want to mark line 8 as changed so that all subsequent
        # changes to line 8 are marked as churn
        # The thinking behind this is the other updates should have been made
        # while this change was being made.
        remove_line_number = removal[0]
        ensure_line_exists(file_line_churn_dict, remove_line_number)
        return files, contribution, churn

    for (line_number, lines_removed, lines_added) in compute_changes(removal, addition):
        # Churn check performed before line modification changes
        is_churn = is_this_churn(file_line_churn_dict, line_number)

        ensure_line_exists(file_line_churn_dict, line_number)
        line_count_change_metrics = file_line_churn_dict[line_number]

        line_count_change_metrics["lines_removed"] += lines_removed
        line_count_change_metrics["lines_added"] += lines_added

        if is_churn:
            churn += abs(lines_removed) + abs(lines_added)
        else:
            contribution += abs(lines_removed) + abs(lines_added)

    return files, contribution, churn


def compute_changes(removal, addition):
    # If both removal and addition affect the same line, net out the change
    # Returns a list of tuples of type (line_number, lines_removed, lines_added)
    removed_line_number, lines_removed = removal
    added_line_number, lines_added = addition

    if removed_line_number == added_line_number:
        if lines_added >= lines_removed:
            return [(removed_line_number, 0, (lines_added - lines_removed))]
        else:
            return [(removed_line_number, (lines_removed - lines_added), 0)]
    else:
        return [
            (removed_line_number, lines_removed, 0),
            (added_line_number, 0, lines_added),
        ]


def is_this_churn(file_line_churn_dict, line_number):
    # The definition of churn is any change to a line
    # after the first time the line has been changed
    # This is detected by a line operation logged in the file_line_churn_dict
    return line_number in file_line_churn_dict


def ensure_line_exists(file_line_churn_dict, line_number):
    if line_number not in file_line_churn_dict:
        file_line_churn_dict[line_number] = {"lines_removed": 0, "lines_added": 0}


def ensure_file_exists(files, file):
    if file not in files:
        files[file] = {}


def is_noop(removal, addition):
    # A noop event occurs when a change indicates one delete and one add on the same line
    return removal == addition


# arrives in a format such as -13 +27,5 (no commas mean 1 loc change)
# this is the chunk header where '-' is old and '+' is new
# it returns a dictionary where left are removals and right are additions
# if the same line got changed we subtract removals from additions
def get_loc_change(loc_changes):
    # removals
    left = loc_changes[:loc_changes.find(' ')]
    left_dec = 0
    if left.find(',') > 0:
        comma = left.find(',')
        left_dec = int(left[comma+1:])
        left = int(left[1:comma])
    else:
        left = int(left[1:])
        left_dec = 1

    removal = (left, left_dec)

    # additions
    right = loc_changes[loc_changes.find(' ')+1:]
    right_dec = 0
    if right.find(',') > 0:
        comma = right.find(',')
        right_dec = int(right[comma+1:])
        right = int(right[1:comma])
    else:
        right = int(right[1:])
        right_dec = 1

    addition = (right, right_dec)

    return (removal, addition)


def is_loc_change(result, loc_changes):
    # search for loc changes (@@ ) and update loc_changes variable
    if result.startswith('@@'):
        loc_change = result[result.find(' ')+1:]
        loc_change = loc_change[:loc_change.find(' @@')]
        return loc_change
    else:
        return loc_changes


def is_new_file(result, file):
    # search for destination file (+++ ) and update file variable
    if result.startswith('+++'):
        return result[result.rfind(' ')+1:]
    else:
        return file


# use format='%an' to get a list of author names
def get_commits(before, after, author, project_dir, format='%h'):
    # note --no-merges flag (usually we coders do not overhaul contrib commits)
    # note --reverse flag to traverse history from past to present
    command = f'git log --author="{author}" --format="{format}" --no-abbrev'
    command += f' --before="{before}" --after="{after}" --no-merges --reverse'
    return get_proc_out(command, project_dir).splitlines()

# issue #6: append to date if it's missing month or day values
def format_date(d):
    d = d[:-1] if d.endswith('-') else d
    if len(d) < 6:
            # after is interpreted as 'after the year YYYY'
            return d[0:4]+'-12-31'
    elif len(d) < 8:
        # here we need to check on which day a month ends
        dt = datetime.datetime.strptime(d, '%Y-%m')
        dt_day = get_month_last_day(dt)
        dt_month = str('{:02d}'.format(dt.month))
        return d[0:4]+'-'+dt_month+'-'+dt_day
    else:
        dt = datetime.datetime.strptime(d, '%Y-%m-%d')
        dt_day = str('{:02d}'.format(dt.day))
        dt_month = str('{:02d}'.format(dt.month))
        return d[0:4]+'-'+dt_month+'-'+dt_day


# https://stackoverflow.com/a/43088
def get_month_last_day(date):
    if date.month == 12:
        return date.replace(day=31)
    ld = date.replace(month=date.month+1, day=1)-datetime.timedelta(days=1)
    return str(ld.day)


# not used but still could be of value in the future
def get_files(commit, project_dir):
    # this also works in case --no-merges flag is ommitted prior
    command = 'git show --numstat --pretty="" ' + commit
    results = get_proc_out(command, project_dir).splitlines()
    for i in range(len(results)):
        # remove the tabbed stats from --numstat
        results[i] = results[i][results[i].rfind('\t')+1:]
    return(results)


def get_proc_out(command, project_dir):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=project_dir,
        shell=True
    )
    try:
        resp = process.communicate()
        return resp[0].decode('utf-8')
    except Exception as e:
        resp = process.communicate()
        return resp[0].decode("latin-1")

# https://stackoverflow.com/a/54547257
def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(path + " is not a valid path.")

#https://stackoverflow.com/a/16891418
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

if __name__ == '__main__':
    main()
