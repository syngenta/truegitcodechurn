# True Git Code Churn
A Python script to compute "true" code churn of a Git repository. Useful for software teams to openly help manage technical debt.

Code churn has several definitions, the one that to me provides the most value as a metric is:

> "Code churn is when an engineer rewrites their own code in a short period of time."

*Reference: https://www.pluralsight.com/blog/teams/why-code-churn-matters*

Solutions that I've found online looked at changes to files irrespective whether these are new changes or edits to existing lines of code (LOC) within existing files. Hence this solution that segments line-of-code edits (churn) with new code changes (contribution).

*Tested with Python version 3.5.3 and Git version 2.20.1*

# How it works
This lightweight script looks at a range of commits per author. For each commit it bookkeeps the files that were changed along with the LOC for each file. LOC are kept in a sparse structure and changes per LOC are taken into account as the program loops. When a change to the same LOC is detected it updates this separately to bookkeep the true code churn.
Result is a print with aggregated contribution and churn per author for a given time period.

***Note:*** This includes the `--no-merges` flag as it assumes that merge commits with or without merge conflicts are not indicative of churn.

# Usage
Positional (required) arguments:
- **after**        after a certain date, in YYYY[-MM[-DD]] format
- **before**     before a certain date, in YYYY[-MM[-DD]] format
- **author**     author string (not committer)
- **dir**            include Git repository directory

Optional arguments:
- **-h, --h, --help**    show this help message and exit
- **-exdir**                   exclude Git repository subdirectory

## Example
```bash
python ./gitcodechurn.py after="2018-11-29" before="2019-03-01" author="an author" dir="/Users/myname/myrepo" -exdir="excluded-directory"
```
## Output
```bash
author:       an author
contribution: 844
churn:        -28
```
Outputs can be used as part of a pipeline that generates bar charts for reports:
![contribution vs churn example chart](/chart.png)
