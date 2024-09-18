# True Git Code Churn

A Python script to compute "true" code churn of a Git repository. Useful for software teams to openly help manage technical debt.

Code churn has several definitions, the one that to me provides the most value as a metric is:

> "Code churn is when an engineer rewrites their own code in a short period of time."

Solutions that I've found online looked at changes to files irrespective whether these are new changes or edits to existing lines of code (LOC) within existing files. Hence this solution that segments line-of-code edits (churn) with new code changes (contribution).

# How it works
This lightweight script looks at commits per author for a given date range on the **current branch**. For each commit it bookkeeps the files that were changed along with the LOC for each file. LOC are kept in a sparse structure and changes per LOC are taken into account as the program loops. When a change to the same LOC is detected it updates this separately to bookkeep the true code churn.
Result is a print with aggregated contribution and churn per author for a given period in time.

***Note:*** This includes the `--no-merges` flag as it assumes that merge commits with or without merge conflicts are not indicative of churn.

# Usage
Positional (required) arguments:
- **dir**        include Git repository directory (specified as an absolute path)

Optional arguments:
- **--after**      after a certain date, in YYYY[-MM[-DD]] format
- **--before**     before a certain date, in YYYY[-MM[-DD]] format
- **--author**     author string (not a committer), leave blank to scope all authors
- **-exdir**                exclude Git repository subdirectory
- **--show-file-data**      show results per line per file result
- **--aggregate_file_data** show results per file aggregated
- **--csv**                 the resulting output is printed to the terminal formatted as CSV
- **-h, --h, --help**       show this help message and exit

## Usage example with a specific author
```bash
python ./gitcodechurn.py /Users/myname/myrepo --after 2018-11-29 --before 2019-03-01 --author "an author"
```

## Usage example without specifying an author
```bash
python ./gitcodechurn.py /Users/myname/myrepo --after 2018-11-29 --before "2019-03-01  -exdir excluded-directory
```

## Usage example without specifying anything other than the folder of the repo
```bash
python ./gitcodechurn.py /Users/myname/myrepo 
```


Outputs can be used as part of a pipeline (not included) that generates bar charts for reports.
