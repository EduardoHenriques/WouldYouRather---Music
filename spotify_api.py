
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