from sqlalchemy.sql import text
from sqlalchemy import create_engine
import unittest
from report import max_changes
from models import Base

class TestReport(unittest.TestCase):

    def test_max_changes(self):
        engine=create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(engine)
        with engine.connect().execution_options(autocommit=True) as con:
            init_stmt = text("""insert into file_change values
            (9831, 561696910, 'file1', 'https://github.com/file1', 'modified', 25),
            (9832, 561696911, 'file1', 'https://github.com/file1', 'modified', 5),
            (9833, 561696912, 'file1', 'https://github.com/file1', 'modified', 10),
            (2382, 558175195, 'file2', 'https://github.com/file2', 'added', 49),
            (2383, 558175194, 'file2', 'https://github.com/file2', 'added', 4)
            """)
            con.execute(init_stmt)
            print(con.execute(text("select * from file_change")).fetchall())
            result=max_changes(con)
            print(result)
            self.assertEqual(result, (53, 'file2', 3, 'file1'), "Should equal")

if __name__ == '__main__':
    unittest.main()
