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

Tested with Python version 3.5.3 up to 3.13 and Git version 2.20.1 up to git 2.39.3