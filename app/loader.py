from github import Github
from sqlalchemy.orm import sessionmaker
from models import Repo, PR, FileChange, Base
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
import sys
import db

class Loader():
    """
    This class helps to load pull requests from a specific repository into database instance
    """
    def __init__(self, gh_api_key):
        self.gh = Github(gh_api_key)
        self.gh.per_page=100 # max perpage limit by github is 100
        print("GitHub current rate limit (remaining, limit): {}".format(self.gh.rate_limiting))

    def init_schema(self):
        Base.metadata.create_all(db.engine)

    def drop_schema(self):
        Base.metadata.drop_all(db.engine)

    def load_repo(self, repo_name):
        """Fetches pull requests page-by-page (100 items each), running api calls in parallel within page. Commits to db every page."""
        repo = self.gh.get_repo(repo_name)
        Session = sessionmaker(bind = db.engine)
        session = Session()
        session.add(Repo(id=repo.id, url=repo.url, name=repo.name))
        session.commit()
        pulls=repo.get_pulls(state="all") # state="open"
        total=pulls.totalCount
        print('Total prs {}'.format(total))
        p = 0
        page=pulls.get_page(p)
        while(page):
            p+=1
            print('Reading page #{}, {}/{}'.format(p, min(total, p*self.gh.per_page), total))
            start_time = time.time()
            (prs, files) = ([], [])
            # here max workers corresponds to number of items in page
            with ThreadPoolExecutor(max_workers=self.gh.per_page) as executor:
                def read_pr(pull):
                    #print('Reading pull {}'.format(pull))
                    pr=PR(id=pull.id, title=pull.title, state=pull.state, url=pull.url, repo_id=repo.id,
                          created_at=pull.created_at, merged_at=pull.merged_at, closed_at=pull.closed_at)
                    prs.append(pr)
                    for file in pull.get_files():
                        fc=FileChange(pr_id=pull.id, filename=file.filename, raw_url=file.raw_url, status=file.status, num_changes=file.changes)
                        files.append(fc)
                    #print('read pr {}'.format(pull.id))
                futures = {executor.submit(read_pr, (pull)) for pull in page}
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    print('exception: %s' % (exc))
            print("--- %s seconds to read page from github ---" % (time.time() - start_time))
            session.add_all(prs)
            session.add_all(files)
            page=pulls.get_page(p)         
            session.commit()

if __name__ == '__main__':
    gh_api_key = sys.argv[1]
    repo_name = sys.argv[2]
    loader = Loader(gh_api_key)
    loader.drop_schema()
    loader.init_schema()
    loader.load_repo(repo_name)
