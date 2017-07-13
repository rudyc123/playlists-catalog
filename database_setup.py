from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))


class Playlist(Base):
    __tablename__ = "playlist"

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)
    # Delete cascade to ensure integrity of db is maintained
    songs = relationship("Songs", cascade="all, delete")

    @property
    def serialize(self):
        # Returns object data in a JSON format
        return {
            "id": self.id,
            "name": self.name,
        }


class Songs(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key = True)
    track_name = Column(String(250), nullable = False)
    artist_name = Column(String(250))
    album_name = Column(String(250))
    playlist_id = Column(Integer, ForeignKey("playlist.id"))
    playlist = relationship(Playlist)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @property 
    def serialize(self):
        # Returns object data in a JSON format
        return {
            "id": self.id,
            "track_name": self.track_name,
            "artist_name": self.artist_name,
            "album_name": self.album_name,
        }


engine = create_engine("sqlite:///playlistcatalog.db")

Base.metadata.create_all(engine)
