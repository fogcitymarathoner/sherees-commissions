from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from rrg.models import Base


class DownloadFile(Base):
    __tablename__ = 'jos_downloads_files'

    id = Column(Integer, primary_key=True)

    blobs = relationship("DownloadBlob", back_populates="file")

    chunkcount = Column(Integer)

    filetitle = Column(String(20))
    realname = Column(String(20))

    isblob = Column(Boolean)

    def __repr__(self):
        return "<DownloadFile(id='%s', filetitle='%s', realname='%s')>" % (
            self.id, self.filetitle, self.realname)


class DownloadBlob(Base):
    __tablename__ = 'jos_downloads_blob'

    id = Column(Integer, primary_key=True)

    fileid = Column(Integer, ForeignKey('jos_downloads_files.id'))
    file = relationship("DownloadFile")
    chunkid = Column(Integer)
    bloblength = Column(Integer)
    datachunk = Column(MEDIUMBLOB)

    def __repr__(self):
        return "<DownloadBlob(id='%s', chunkid='%s')>" % (
            self.id, self.chunkid)