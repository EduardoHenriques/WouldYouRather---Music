
import base64, requests
from typing import Dict, List

# Client ID : 778df54a97194827a62157c7f785a958
# Client Secret : 0129d5e5fabb4c94948d27f3cfa839ad

class SpotifyAPI:
    def __init__(self, client_id: str, client_secret: str):
        """
        Simple Spotify API client for local use
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        
        self.get_access_token()
        
    def get_access_token(self):
        """Get access token using credentials"""
        credentials = f"{self.client_id}:{self.client_secret}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {credentials_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            print("Spotify API connected!")
        else:
            print(f"Could not get token: {response.status_code}")
            
    
    def search_artists(self, query: str) -> List[Dict]:
        if not query or not self.access_token:
            return []
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        params = {
            "q": query,
            "type": "artist",
            "limit": 10
        }
        
        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            artists = response.json()["artists"]["items"]
            
            # Sort by popularity and return simplified data
            artists.sort(key=lambda x: x["popularity"], reverse=True)
            
            return [
                {
                    "id": artist["id"],
                    "name": artist["name"],
                    "popularity": artist["popularity"]
                }
                for artist in artists
            ]
        
        return []


    def get_artist_info(self, artist_id: str) -> Dict:
        """
        Get an artist's albums with year and tracks in the structure:
        {
            "albums": {
                "Album Name": {
                    "year": "YYYY",
                    "cover_url": "...",
                    "tracks": {
                        "Track Name": {
                            "duration": "mm:ss",
                            "image": "https://..."
                        }
                    }
                }
            }
        }
        """
        if not artist_id or not self.access_token:
            return {}
    
        headers = {"Authorization": f"Bearer {self.access_token}"}
    
        # Get artist info
        artist_response = requests.get(
            f"https://api.spotify.com/v1/artists/{artist_id}",
            headers=headers
        )
        if artist_response.status_code != 200:
            print(f"Error fetching artist info: {artist_response.status_code}")
            return {}
    
        artist_data = artist_response.json()
        artist_name = artist_data.get("name", "Unknown Artist")
    
        # Get artist's albums
        albums_params = {
            "include_groups": "album,single",
            "market": "US",
            "limit": 50,
            "offset": 0
        }
    
        albums_response = requests.get(
            f"https://api.spotify.com/v1/artists/{artist_id}/albums",
            headers=headers,
            params=albums_params
        )
    
        if albums_response.status_code != 200:
            print(f"Error fetching albums: {albums_response.status_code}")
            return {}
    
        albums_data = albums_response.json()["items"]
    
        artist_info = {
            "artist_id": artist_id,
            "artist_name": artist_name,
            "albums": {}
        }
    
        for album in albums_data:
            album_id = album["id"]
            album_name = album["name"]
            release_year = album["release_date"][:4] if album["release_date"] else "Unknown"
    
            # Get album cover URL
            images = album.get("images", [])
            cover_url = images[0].get("url", "") if images else ""
    
            # Get album tracks
            tracks_response = requests.get(
                f"https://api.spotify.com/v1/albums/{album_id}/tracks",
                headers=headers,
                params={"limit": 50}
            )
    
            tracks_dict = {}
            if tracks_response.status_code == 200:
                tracks_data = tracks_response.json()["items"]
                for track in tracks_data:
                    track_name = track["name"]
                    duration_ms = track["duration_ms"]
                    minutes = duration_ms // 60000
                    seconds = (duration_ms % 60000) // 1000
                    duration_str = f"{minutes}:{seconds:02d}"
    
                    # Add duration and image (album cover) to each track
                    tracks_dict[track_name] = {
                        "duration": duration_str,
                        "image": cover_url
                    }
            else:
                print(f"Error fetching tracks for album {album_name}: {tracks_response.status_code}")
    
            artist_info["albums"][album_name] = {
                "year": release_year,
                "cover_url": cover_url,
                "tracks": tracks_dict
            }
    
        return artist_info