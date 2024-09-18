from gitcodechurn.processes import Process


class Git:

    @classmethod
    def get_commits(cls, before, after, author, project_dir, format='%h'):
        # use format='%an' to get a list of author names
        # note --no-merges flag (usually we coders do not overhaul contrib commits)
        # note --reverse flag to traverse history from past to present
        command = f'git log --author="{author}" --format="{format}" --no-abbrev'
        command += f' --before="{before}" --after="{after}" --no-merges --reverse'
        return Process.get_proc_out(command, project_dir).splitlines()

    @classmethod
    def get_commit_results(cls, commit, project_dir, exdir):
        # git show automatically excludes binary file changes
        command = 'git show --format= --unified=0 --no-prefix ' + commit
        if len(exdir) > 1:
            # https://stackoverflow.com/a/21079437
            command += ' -- . ":(exclude,icase)'+exdir+'"'
        return Process.get_proc_out(command, project_dir).splitlines()
    
    @classmethod
    def is_new_file(cls, result, file):
        # search for destination file (+++ ) and update file variable
        if result.startswith('+++'):
            return result[result.rfind(' ')+1:]
        else:
            return file
    
    @classmethod
    def is_loc_change(cls, result, loc_changes):
        # search for loc changes (@@ ) and update loc_changes variable
        if result.startswith('@@'):
            loc_change = result[result.find(' ')+1:]
            loc_change = loc_change[:loc_change.find(' @@')]
            return loc_change
        else:
            return loc_changes


    @classmethod
    def authors(cls, before, after, author, project_dir):
        authors = set(Git.get_commits(before, after, author, project_dir, '%an')).__str__()
        authors = set(authors.replace('{', '').replace('}', '').replace("'",""))
        return authors