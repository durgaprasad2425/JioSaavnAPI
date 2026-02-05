from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import jiosaavn
import os
from traceback import print_exc
import logging

# Configure logging: default to WARNING to suppress fetch logs
logging.basicConfig(level=logging.WARNING)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def home():
    return RedirectResponse(url="https://cyberboysumanjay.github.io/JioSaavnAPI/")


@app.get('/song/')
async def search(
    query: str = Query(None),
    lyrics: str = Query(None),
    songdata: str = Query(None),
    limit: int = Query(None)
):
    lyrics_flag = False
    songdata_flag = True
    
    if lyrics and lyrics.lower() != 'false':
        lyrics_flag = True
    if songdata and songdata.lower() != 'true':
        songdata_flag = False
    
    if query:
        songs = jiosaavn.search_for_song(query, lyrics_flag, songdata_flag)
        if limit and isinstance(songs, list):
            songs = songs[:limit]
        return songs
    else:
        return {
            "status": False,
            "error": 'Query is required to search songs!'
        }


@app.get('/song/get/')
async def get_song(
    id: str = Query(None),
    lyrics: str = Query(None)
):
    lyrics_flag = False
    
    if lyrics and lyrics.lower() != 'false':
        lyrics_flag = True
    
    if id:
        resp = jiosaavn.get_song(id, lyrics_flag)
        if not resp:
            return {
                "status": False,
                "error": 'Invalid Song ID received!'
            }
        else:
            return resp
    else:
        return {
            "status": False,
            "error": 'Song ID is required to get a song!'
        }


@app.get('/playlist/')
async def playlist(
    query: str = Query(None),
    lyrics: str = Query(None),
    limit: int = Query(None)
):
    lyrics_flag = False
    
    if lyrics and lyrics.lower() != 'false':
        lyrics_flag = True
    
    if query:
        id = jiosaavn.get_playlist_id(query)
        songs = jiosaavn.get_playlist(id, lyrics_flag)
        if limit and isinstance(songs, dict) and 'songs' in songs:
            songs['songs'] = songs['songs'][:limit]
        elif limit and isinstance(songs, list):
            songs = songs[:limit]
        return songs
    else:
        return {
            "status": False,
            "error": 'Query is required to search playlists!'
        }


@app.get('/album/')
async def album(
    query: str = Query(None),
    lyrics: str = Query(None),
    limit: int = Query(None)
):
    lyrics_flag = False
    
    if lyrics and lyrics.lower() != 'false':
        lyrics_flag = True
    
    if query:
        id = jiosaavn.get_album_id(query)
        songs = jiosaavn.get_album(id, lyrics_flag)
        if limit and isinstance(songs, dict) and 'songs' in songs:
            songs['songs'] = songs['songs'][:limit]
        elif limit and isinstance(songs, list):
            songs = songs[:limit]
        return songs
    else:
        return {
            "status": False,
            "error": 'Query is required to search albums!'
        }


@app.get('/lyrics/')
async def get_lyrics(query: str = Query(None)):
    if query:
        try:
            if 'http' in query and 'saavn' in query:
                id = jiosaavn.get_song_id(query)
                lyrics_result = jiosaavn.get_lyrics(id)
            else:
                lyrics_result = jiosaavn.get_lyrics(query)
            response = {
                "status": True,
                "lyrics": lyrics_result
            }
            return response
        except Exception as e:
            return {
                "status": False,
                "error": str(e)
            }
    else:
        return {
            "status": False,
            "error": 'Query containing song link or id is required to fetch lyrics!'
        }


@app.get('/result/')
async def result(
    query: str = Query(None),
    lyrics: str = Query(None),
    # limit: int = Query(None)
):
    lyrics_flag = False
    
    if lyrics and lyrics.lower() != 'false':
        lyrics_flag = True

    if 'saavn' not in query:
        songs = jiosaavn.search_for_song(query, lyrics_flag, True)
        # if limit and isinstance(songs, list):
        #     songs = songs[:limit]
        return songs
    
    try:
        if '/song/' in query:
            # debug log kept for diagnostics
            logging.debug("Result: Song link detected")
            song_id = jiosaavn.get_song_id(query)
            song = jiosaavn.get_song(song_id, lyrics_flag)
            return song

        elif '/album/' in query:
            logging.debug("Result: Album link detected")
            id = jiosaavn.get_album_id(query)
            songs = jiosaavn.get_album(id, lyrics_flag)
            return songs

        elif '/playlist/' in query or '/featured/' in query:
            logging.debug("Result: Playlist link detected")
            id = jiosaavn.get_playlist_id(query)
            songs = jiosaavn.get_playlist(id, lyrics_flag)
            return songs

    except Exception as e:
        logging.exception("Error processing result query")
        return {
            "status": True,
            "error": str(e)
        }
    return None


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5100, reload=True)