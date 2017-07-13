import random
import string
import httplib2
import json
import requests

from flask import Flask, render_template, make_response, request, flash
from flask import redirect, jsonify, url_for, session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Playlist, Songs, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps


client_id = json.loads(open("client_secrets.json", "r").read())["web"]["client_id"]
application_name = "Playlist Catalog App"

app = Flask(__name__)

# Connect to database and create session
engine = create_engine("sqlite:///playlistcatalog.db")
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# User helper functions
def createUser(login_session):
    newUser = User(name=login_session["username"], email=login_session["email"], 
            picture=login_session["picture"])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session["email"]).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in login_session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Show all playlists
@app.route("/")
@app.route("/playlists/")
def showPlaylist():
    playlists = session.query(Playlist).order_by(asc(Playlist.name))
    if "user_id" not in login_session:
        return render_template("publicplaylists.html", playlists=playlists)
    else:
        return render_template("playlists.html", playlists=playlists)


# Add new playlist
@app.route("/playlist/new/", methods=["GET", "POST"])
@login_required
def newPlaylist():
    if request.method == "POST":
        newPlaylist = Playlist(
            name=request.form["name"], user_id=login_session["user_id"])
        session.add(newPlaylist)
        flash("New playlist %s has been successfully created!" %newPlaylist.name)
        session.commit()
        return redirect(url_for("showPlaylist"))
    return render_template("newPlaylist.html")


# Edit an existing playlist
@app.route("/playlist/<int:playlist_id>/edit/", methods=["GET", "POST"])
@login_required
def editPlaylist(playlist_id):
    # retrieve existing playlist from db
    editedPlaylist = session.query(Playlist).filter_by(id=playlist_id).one()
    playlists = session.query(Playlist).order_by(asc(Playlist.name))

    if request.method == "POST":
        # change editedPlaylist to val of form["name"]
        if request.form["name"]:
            editedPlaylist.name = request.form["name"]
            session.commit()
            flash("Playlist %s has been sucessfully edited!" %editedPlaylist.name)
            return redirect(url_for("showPlaylist"))

    # Ensures that user matches the original user 
    if editedPlaylist.user_id != login_session["user_id"]:
        flash("You are not authorised to edit this playlist. \
            Please create your own playlist for that functionality!")
        return render_template("edit-popup.html", playlists=playlists)
    else:
        return render_template("editPlaylist.html", playlist=editedPlaylist)


# Delete an existing playlist
@app.route("/playlist/<int:playlist_id>/delete/", methods=["GET", "POST"])
@login_required
def deletePlaylist(playlist_id):
    playlistToDelete = session.query(Playlist).filter_by(id=playlist_id).one()
    playlists = session.query(Playlist).order_by(asc(Playlist.name))

    if playlistToDelete.user_id != login_session["user_id"]:
        flash("You are not authorised to delete this playlist. \
            Please create your own playlist for that functionality!")
        return render_template("delete-popup.html", playlists=playlists)
    if request.method == "POST":
        session.delete(playlistToDelete)
        flash("%s has been successfully deleted." %playlistToDelete.name)
        session.commit()
        return redirect(url_for("showPlaylist"))
    else:
        return render_template("deletePlaylist.html", playlist=playlistToDelete)


# Show songs in playlist
@app.route("/playlist/<int:playlist_id>/")
@app.route("/playlist/<int:playlist_id>/songs/")
def showSongs(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    creator = getUserInfo(playlist.user_id)
    songs = session.query(Songs).filter_by(playlist_id=playlist_id).all()
    if "user_id" not in login_session or creator.id != login_session["user_id"]:
        return render_template("publicsongs.html", songs=songs, 
                                playlist=playlist, creator=creator)
    else:
        return render_template("songs.html", songs=songs, 
                                playlist=playlist, creator=creator)


# Add a new song to existing playlist
@app.route("/playlist/<int:playlist_id>/song/new/", methods=["GET", "POST"])
@login_required
def newSong(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    songs = session.query(Songs).filter_by(playlist_id=playlist_id).all()
    creator = getUserInfo(playlist.user_id)
    
    if login_session["user_id"] != playlist.user_id:
        flash("You are not authorised to add a song to this playlist. \
            Please create your own playlist for that functionality!")
        return render_template("newSong-popup.html", songs=songs, 
                                playlist=playlist, creator=creator)

    if request.method == "POST":
        newSong = Songs(track_name=request.form["track_name"], 
                        artist_name=request.form["artist_name"],
                        album_name=request.form["album_name"],
                        playlist_id=playlist_id,
                        user_id=playlist.user_id)
        session.add(newSong)
        session.commit()
        flash("New song %s has been sucessfully added!" %newSong.track_name)
        return redirect(url_for("showSongs", playlist_id=playlist_id))
    else:
        return render_template("newSong.html", playlist_id=playlist_id)


# Edit a song from an existing playlist
@app.route("/playlist/<int:playlist_id>/song/<int:song_id>/edit/", 
        methods=["GET", "POST"])
@login_required
def editSong(playlist_id, song_id):
    songs = session.query(Songs).filter_by(playlist_id=playlist_id).all()
    editedSong = session.query(Songs).filter_by(id=song_id).one()
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    creator = getUserInfo(playlist.user_id)

    if login_session["user_id"] != playlist.user_id:
        flash("You are not authorised to edit this song. \
            Please create your own playlist for that functionality!")
        return render_template("newSong-popup.html", songs=songs,
                                playlist=playlist, creator=creator)

    if request.method == "POST":
        if request.form["track_name"]:
            editedSong.track_name = request.form["track_name"]
        if request.form["artist_name"]:
            editedSong.artist_name = request.form["artist_name"]
        if request.form["album_name"]:
            editedSong.album_name = request.form["album_name"]

        session.add(editedSong)
        session.commit()
        flash("The song %s from %s has been successfully edited!" %(
            editedSong.track_name, playlist.name))
        return redirect(url_for('showSongs', playlist_id=playlist_id))
    else:
        return render_template("editSong.html", playlist_id=playlist_id, 
                                song=editedSong)


# Delete a song from an existing playlist
@app.route("/playlist/<int:playlist_id>/song/<int:song_id>/delete/", 
    methods=["GET", "POST"])
@login_required
def deleteSong(playlist_id, song_id):
    songToDelete = session.query(Songs).filter_by(id=song_id).one()
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    creator = getUserInfo(playlist.user_id)
    songs = session.query(Songs).filter_by(playlist_id=playlist_id).all()

    if login_session["user_id"] != playlist.user_id:
        flash("You are not authorised to delete songs from this playlist. \
            Please create your own playlist for that functionality!")
        return render_template("newSong-popup.html", songs=songs,
                                playlist=playlist, creator=creator)

    if request.method == "POST":
        session.delete(songToDelete)
        session.commit()
        flash("The song %s has been successfully deleted from the %s playlist." 
                %(songToDelete.track_name, playlist.name))
        return redirect(url_for('showSongs', playlist_id=playlist_id))
    else:
        return render_template("deleteSong.html", playlist_id=playlist_id, 
                                song=songToDelete)


# JSON endpoints
@app.route("/playlist/json/")
@app.route("/playlists/json/")
def playlistsJSON():
    playlists = session.query(Playlist).all()
    return jsonify(playlists = [i.serialize for i in playlists])


@app.route("/playlist/<int:playlist_id>/song/json/")
@app.route("/playlist/<int:playlist_id>/json/")
def playlistsongsJSON(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    songs = session.query(Songs).filter_by(playlist_id=playlist_id).all()
    return jsonify(songs = [i.serialize for i in songs])


@app.route("/playlist/<int:playlist_id>/song/<int:song_id>/json/")
def songJSON(playlist_id, song_id):
    songs = session.query(Songs).filter_by(id=song_id).one()
    return jsonify(songs = songs.serialize)


# Anti-Forgery State Tokens
@app.route("/login/")
def showLogin():
    state = "".join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session["state"] = state 
    # return "The current session state is %s" %login_session["state"]
    return render_template("login.html", STATE=state)



# Google+ Signin
@app.route("/gconnect", methods=["POST"])
def gconnect():
    # Validate random state token
    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps("Invalid state parameter"), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    # Obtain authorisation code
    code = request.data

    try:
        # Upgrade the authorisation code into a credentials object
        oauth_flow = flow_from_clientsecrets("client_secrets.json", scope="")
        oauth_flow.redirect_uri = "postmessage"
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("Failed to upgrade the authorisation code."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Check if access token is valid
    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s" 
        %access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, "GET")[1])
    # If an error in access token, abort
    if result.get("error") is not None:
        response = make_response(json.dumps(result.get("error")), 500)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token["sub"]
    if result["user_id"] != gplus_id:
        response = make_response(
            json.dumps("Token's client ID does not match the app's."), 401)
        print("Token's client ID does not match the app's.")
        response.headers["Content-Type"] = "application/json"
        return response

    stored_credentials = login_session.get("credentials")
    stored_gplus_id = login_session.get("gplus_id")
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Success! You are now logged in as %s." % login_session['username'])
    print("Done!")
    return output


# Google+ Signout
@app.route("/gdisconnect/")
def gdisconnect():
    # Disconnect connected user only
    # credentials = login_session.get("credentials")
    credentials = login_session["access_token"]
    print("gdisconnect access token is %s" %credentials)
    print("user name is: ")
    print(login_session["username"])
    if credentials is None:
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    # access_token = credentials.access_token
    # creds = int(credentials["access_token"])
    h = httplib2.Http()
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" %login_session[
    "access_token"]
    result = h.request(url, "GET")[0]

    if result["status"] == "200":
        # Reset user's session
        # del login_session["credentials"]
        del login_session["access_token"]
        del login_session["gplus_id"]
        del login_session["username"]
        # del login_session["email"]
        # del login_session["picture"]
        response = make_response(json.dumps("Successfully disconnected. "), 200)
        response.headers["Content-Type"] = "application/json"

        return response

    elif result["status"] != "200":
        # In case the given token is invalid
        response = make_response(
            json.dumps("Failed to revoke token for given user."), 400)
        response.headers["Content-Type"] = "application/json"
        return response


# Facebook Signin
@app.route("/fbconnect", methods=["POST"])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    #exchange client token for long-lived server-side token with GET
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.8/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    # token = 'access_token=' + data['access_token']
    token = "access_token=" + data.get("access_token")
    # see: https://discussions.udacity.com/t/
    #   issues-with-facebook-oauth-access-token/233840?source_topic_id=174342

    # Use token to get user info from API
    # make API call with new token
    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email,picture'%token

   #new: put the "picture" here, it is now part of the default "public_profile"

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['picture'] = data['picture']["data"]["url"]
    login_session['access_token'] = access_token

    #see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1><img src="'
    output += login_session['picture']
    output += ' ">'

    flash("Now logged in as %s." % login_session['username'])
    return output

# Facebook Signout
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' %(
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out."


# Disconnect according to social media provider
@app.route("/disconnect")
def disconnect():
    if "provider" in login_session:
        if login_session["provider"] == "google":
            gdisconnect()
            # del login_session["user_id"]
            # del login_session["credentials"]
        if login_session["provider"] == "facebook":
            fbdisconnect()
            del login_session["facebook_id"]
        # del login_session["username"]
        del login_session["user_id"]
        del login_session["email"]
        del login_session["picture"]
        del login_session["provider"]
        flash("You've been successfully logged out.")
        return redirect(url_for("showPlaylist"))
    else:
        flash("You were not logged in.")
        return redirect(url_for("showPlaylist"))
        



if __name__ == "__main__":
    app.secret_key = "debugging_secret_key"
    app.debug = True
    app.run(host = "0.0.0.0", port = 5000)
