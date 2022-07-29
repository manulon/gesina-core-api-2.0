from sqlalchemy import (
    Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
)
from sqlalchemy.orm import relationship
from src.persistance.session import Base
from src.service import file_storage_service
from src.service.exception.file_exception import FilePreSignedUrlError


class Geometry(Base):
    __tablename__ = "geometry"
    id = Column(Integer, primary_key=True, default=None)
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User")

    def __str__(self):
        return self.name

    def get_file_url(self):
        try:
            return file_storage_service.get_geometry_url(self.name)
        except FilePreSignedUrlError:
            return ""
