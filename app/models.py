from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Repo(Base):
  """
  This class represents GitHub repository, id is GitHub internal id.
  """
  __tablename__ = 'repo'
  id=Column(BigInteger, primary_key=True)
  url=Column(String)
  name=Column(String)
  def __repr__(self):
    return "<Repo(id='%d', url='%s', name='%s')>" % (self.id, self.url, self.name)

class FileChange(Base):
  """
  This class represents a single file changed within PullRequest. `num_changes` represents sum of changes (deletions, additions, edits)
  """
  __tablename__ = 'file_change'
  id=Column(BigInteger, primary_key=True)
  pr_id = Column(BigInteger, ForeignKey('pr.id'))
  pr=relationship('PR', back_populates='changes', cascade = "all,delete")
  filename=Column(String)
  raw_url=Column(String)
  status=Column(String)
  num_changes=Column(Integer)
  def __repr__(self):
    return "<FileChange(id='%d', pr_id='%d', filename='%s', raw_url='%s', status='%s', num_changes='%d')>" % (self.id, self.pr_id, self.filename, self.raw_url, self.status, self.num_changes)

class PR(Base):
  """
  PullRequest with a list of file changes
  """
  __tablename__ = 'pr'
  id=Column(BigInteger, primary_key=True)
  repo_id=Column(BigInteger, ForeignKey('repo.id'))
  title=Column(String) 
  state=Column(String)
  created_at=Column(DateTime)
  merged_at=Column(DateTime)
  closed_at=Column(DateTime)
  url=Column(String)
  changes = relationship("FileChange", order_by=FileChange.id, back_populates="pr", cascade = "all,delete")
  def __repr__(self):
    return "<PR(id='%d', title='%s', state='%s', url='%s')>" % (self.id, self.title, self.state, self.url)

