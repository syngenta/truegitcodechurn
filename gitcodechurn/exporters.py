
class ExporterFactory:

    @classmethod
    def get_exporter(cls, args):
        if args.csv:
            return CsvExporter
        return TerminalExporter


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
            
            cls.display_file_metrics_row(
                file_name, 
                "TOTAL", 
                {
                    "lines_added": added, 
                    "lines_removed": removed, 
                    "number_of_changes": number_of_changes
                }
            )
    
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


class TerminalExporter:

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
            
            cls.display_file_metrics_row(
                file_name, 
                "TOTAL", 
                {
                    "lines_added": added, 
                    "lines_removed": removed, 
                    "number_of_changes": number_of_changes
                }
            )

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

