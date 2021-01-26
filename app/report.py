from sqlalchemy.orm import sessionmaker
from sqlalchemy import Interval, Integer, String
from sqlalchemy.sql import text
from sqlalchemy.engine.base import Connection
import db

def time_to_merge(connection):
    time_to_merge_stm = text(
        """select min(pr_time) as min, avg(pr_time) as avg, max(pr_time) as max from ("""
        """  select merged_at-created_at as pr_time from pr where merged_at is not null) A;""")
    time_to_merge_stm.columns(min=Interval, avg=Interval, max=Interval)
    time_to_merge_result=connection.execute(time_to_merge_stm).fetchall()
    return (str(time_to_merge_result[0][0]), str(time_to_merge_result[0][1]), str(time_to_merge_result[0][2]))

def max_changes(connection):
    max_changes = text("""select max(line_changes) as line_changes, max(file_changes) as file_changes from ("""
                       """  select sum(num_changes) as line_changes, count(*) as file_changes, filename from file_change group by filename) A""")
    max_changes.columns(line_changes=Integer, file_changes=Integer)
    (max_line_changes, max_file_changes) = connection.execute(max_changes).fetchall()[0]

    max_line_changes_file_smt = text("select filename from file_change group by filename having sum(num_changes) = :line_changes")
    max_line_changes_file_smt.columns(filename=String)
    max_line_changes_file = connection.execute(max_line_changes_file_smt, line_changes=max_line_changes).fetchall()
    if max_line_changes_file:
        max_line_changes_file = max_line_changes_file[0][0]

    max_file_changes_file_smt = text("select filename from file_change group by filename having count(*) = :file_changes")
    max_file_changes_file_smt.columns(filename=String)
    max_file_changes_file = connection.execute(max_file_changes_file_smt, file_changes=max_file_changes).fetchall()
    if max_file_changes_file:
        max_file_changes_file = max_file_changes_file[0][0]

    return (max_line_changes, max_line_changes_file, max_file_changes, max_file_changes_file)

def report():
    with db.engine.connect() as con:
        (min, max, avg) = time_to_merge(con)
        print("""min / avg / max time to merge PR: {} / {} / {}""".format(min, max, avg))
        (line_changes, line_changes_file, file_changes, file_changes_file) = max_changes(con)
        print("""file {} has been changed maximum number of {} times""".format(file_changes_file, file_changes))
        print("""file {} has maximum sum of line changes {}""".format(line_changes_file, line_changes))


if __name__ == '__main__':
    report()
