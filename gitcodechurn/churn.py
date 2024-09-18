from gitcodechurn.git import Git


class Churn:
    @classmethod
    def calculate_statistics(cls, commits, project_dir, exdir):
        # structured like this: files -> LOC
        files = {}

        contribution = 0
        churn = 0

        for commit in commits:
            [files, contribution, churn] = cls.get_loc(
                commit,
                project_dir,
                files,
                contribution,
                churn,
                exdir
            )

        return files, contribution, churn
    
    @classmethod
    def get_loc(cls, commit, project_dir, files, contribution, churn, exdir):
        results = Git.get_commit_results(commit, project_dir, exdir) 
        file = ''
        loc_changes = ''

        # loop through each row of output
        for result in results:
            new_file = Git.is_new_file(result, file)
            if file != new_file:
                file = new_file
                if file not in files:
                    files[file] = {}
            else:
                new_loc_changes = Git.is_loc_change(result, loc_changes)
                if loc_changes != new_loc_changes:
                    loc_changes = new_loc_changes
                    (removal, addition) = cls.get_loc_change(loc_changes)

                    files, contribution, churn = cls.merge_operations(
                        removal, addition, files, contribution, churn, file)
                else:
                    continue
        return [files, contribution, churn]

    @classmethod
    def merge_operations(cls, removal, addition, files, contribution, churn, file):
        # Ensure all required data is in place
        cls.ensure_file_exists(files, file)

        file_line_churn_dict = files[file]

        if cls.is_noop(removal, addition):
            # In the case of a noop, it's not counted in change metrics, but should
            # be marked as changed to accurately include future churn metrics
            remove_line_number = removal[0]
            cls.ensure_line_exists(file_line_churn_dict, remove_line_number)
            return files, contribution, churn

        for (line_number, lines_removed, lines_added) in cls.compute_changes(removal, addition):
            # Churn check performed before line modification changes
            is_churn = cls.is_this_churn(file_line_churn_dict, line_number)

            cls.ensure_line_exists(file_line_churn_dict, line_number)
            line_count_change_metrics = file_line_churn_dict[line_number]

            line_count_change_metrics["lines_removed"] += lines_removed
            line_count_change_metrics["lines_added"] += lines_added

            if is_churn:
                churn += abs(lines_removed) + abs(lines_added)
            else:
                contribution += abs(lines_removed) + abs(lines_added)

        return files, contribution, churn

    @classmethod
    def compute_changes(cls, removal, addition):
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

    @classmethod
    def is_this_churn(cls, file_line_churn_dict, line_number):
        # The definition of churn is any change to a line after the first time the line has been changed
        # This is detected by a line operation logged in the file_line_churn_dict
        return line_number in file_line_churn_dict


    @classmethod
    def ensure_line_exists(cls, file_line_churn_dict, line_number):
        if line_number not in file_line_churn_dict:
            file_line_churn_dict[line_number] = {"lines_removed": 0, "lines_added": 0}


    @classmethod
    def ensure_file_exists(cls, files, file):
        if file not in files:
            files[file] = {}


    @classmethod
    def is_noop(cls, removal, addition):
        # A noop event occurs when a change indicates one delete and one add on the same line
        return removal == addition


    @classmethod
    def get_loc_change(cls, loc_changes):
        # arrives in a format such as -13 +27,5 (no commas mean 1 loc change)
        # this is the chunk header where '-' is old and '+' is new
        # it returns a dictionary where left are removals and right are additions
        # if the same line got changed we subtract removals from additions

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
