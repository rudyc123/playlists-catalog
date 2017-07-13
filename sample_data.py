from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Playlist, Songs, User

engine = create_engine("sqlite:///playlistcatalog.db")

# Bind engine to metadata of Base class so that declaratives
# can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()

session = DBSession()

# Create a dummy user
User1 = User(name="Rudy Klopp", email="rudeymanklopp@hotmail.co.uk",
             picture="https://placekitten/200/200")
session.add(User1)
session.commit()


# Playlist for The Big Jump
playlist1 = Playlist(user_id=1, name="The Big Jump")
session.add(playlist1)
session.commit()

song1 = Songs(playlist_id=1, user_id=1, track_name="Two Against One (feat. Jack White)",
              artist_name="Danger Mouse, Daniele Luppi, Jack White", album_name="Rome")
session.add(song1)
session.commit()

song2 = Songs(playlist_id=1, user_id=1, track_name="Lyin' (Pt. 1 - 4)",
              artist_name="Toro Y Moi", album_name="Lyin' (Pt. 1 - 4) / Would Be")
session.add(song2)
session.commit()

song3 = Songs(playlist_id=1, user_id=1, track_name="Drugs",
              artist_name="Ratatat", album_name="LP4")
session.add(song3)
session.commit()

song4 = Songs(playlist_id=1, user_id=1, track_name="Default",
              artist_name="Django Django", album_name="Django Django")
session.add(song4)
session.commit()

song5 = Songs(playlist_id=1, user_id=1, track_name="Zumm Zumm",
              artist_name="Django Django", album_name="Django Django")
session.add(song5)
session.commit()

song6 = Songs(playlist_id=1, user_id=1, track_name="Wonder Woman, Wonder Me",
              artist_name="Kishi Bashi", album_name="151a")
session.add(song6)
session.commit()


song7 = Songs(playlist_id=1, user_id=1, track_name="Es-so",
              artist_name="tUnE-yArDs", album_name="W H O K I L L")
session.add(song7)
session.commit()

song8 = Songs(playlist_id=1, user_id=1, track_name="Get Lucky - Radio Edit",
              artist_name="Daft Punk, Pharrell Williams, Nile Rodgers", album_name="Get Lucky")
session.add(song8)
session.commit()



# Playlist for Mt. Chillimanjaro
playlist2 = Playlist(user_id=1, name="Mt. Chillimanjaro")
session.add(playlist2)
session.commit()

song1 = Songs(playlist_id=2, user_id=1, track_name="Quite Buttery feat. DOOM", 
              artist_name="Count Bass D", album_name="Unexpected Guests")
session.add(song1)
session.commit()

song2 = Songs(playlist_id=2, user_id=1, track_name="Dapper", 
              artist_name="Domo Genesis, Anderson .Paak", album_name="Genesis")
session.add(song2)
session.commit()

song3 = Songs(playlist_id=2, user_id=1, track_name="Autum Fall", 
              artist_name="Gold Panda", album_name="Good Luck And Do Your Best")
session.add(song3)
session.commit()

song4 = Songs(playlist_id=2, user_id=1, track_name="Back to Me", 
              artist_name="Moonchild", album_name="Be Free")
session.add(song4)
session.commit()

song5 = Songs(playlist_id=2, user_id=1, track_name="So Far To Go", 
              artist_name="J Dilla", album_name="The Shining Instrumental")
session.add(song5)
session.commit()

song6 = Songs(playlist_id=2, user_id=1, track_name="Lite Weight", 
              artist_name="Anderson .Paak", album_name="Malibu")
session.add(song6)
session.commit()

song7 = Songs(playlist_id=2, user_id=1, track_name="Dang! (feat. Anderson .Paak)", 
              artist_name="Mac Miller, Anderson .Paak", album_name="Dang! (feat. Anderson .Paak)")
session.add(song7)
session.commit()

song8 = Songs(playlist_id=2, user_id=1, track_name="Datwhip", 
              artist_name="NxWorries", album_name="Link Up & Suede")
session.add(song8)
session.commit()

song9 = Songs(playlist_id=2, user_id=1, track_name="untitled 08 09.06.2014.", 
              artist_name="Kendrick Lamar", album_name="untitled unmastered.")
session.add(song9)
session.commit()


# Playlist for Pop Covers
playlist3 = Playlist(user_id=1, name="Pop Covers")
session.add(playlist3)
session.commit()

song1 = Songs(playlist_id=3, user_id=1, track_name="Next Door",
              artist_name="Rob Araujo", album_name="Hybrid Eyes")
session.add(song1)
session.commit()

song2 = Songs(playlist_id=3, user_id=1, track_name="Music for a Dancing Mind",
              artist_name="Matthew Halsall", album_name="On The Go (Special Edition)")
session.add(song2)
session.commit()

song3 = Songs(playlist_id=3, user_id=1, track_name="Windows",
              artist_name="Jack Wilkins", album_name="Windows")
session.add(song3)
session.commit()

song4 = Songs(playlist_id=3, user_id=1, track_name="When the World Was One",
              artist_name="Matthew Halsall, Gondwana Orchestra", album_name="When the World Was One")
session.add(song4)
session.commit()

song5 = Songs(playlist_id=3, user_id=1, track_name="Stolen Moments",
              artist_name="Ahmad Jamal Trio", album_name="The Awakening (International)")
session.add(song5)
session.commit()

song6 = Songs(playlist_id=3, user_id=1, track_name="Cherokee",
              artist_name="Kamasi Washington", album_name="The Epic")
session.add(song6)
session.commit()

song7 = Songs(playlist_id=3, user_id=1, track_name="Edge",
              artist_name="Takuya Kuroda", album_name="Edge")
session.add(song7)
session.commit()

song9 = Songs(playlist_id=3, user_id=1, track_name="The Real",
              artist_name="Derrick Hodge", album_name="Live Today")
session.add(song9)
session.commit()

song10 = Songs(playlist_id=3, user_id=1, track_name="Divine",
              artist_name="Roy Hargrove", album_name="Earfood")
session.add(song10)
session.commit()

song11 = Songs(playlist_id=3, user_id=1, track_name="All The Things You Are",
              artist_name="Gerald Clayton", album_name="Bond: The Paris Sessions")
session.add(song11)
session.commit()


