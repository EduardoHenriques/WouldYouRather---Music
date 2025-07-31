import base64, requests, random, string
import threading  # NEW: Added for background song generation
from queue import Queue, Empty  # NEW: Added for song queue management
from typing import Dict, List
from difflib import SequenceMatcher
from would_you_rather import TrackInfo

# Client ID : 778df54a97194827a62157c7f785a958
# Client Secret : 0129d5e5fabb4c94948d27f3cfa839ad

# Search Queries for random songs
search_queries = ['%25a%25', 'a%25', '%25e%25', 'e%25', '%25i%25', 'i%25', '%25o%25', 'o%25']

# Auxiliary Similarity Finder foi Text Query
def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

class SpotifyAPI:
    def __init__(self, client_id: str, client_secret: str):
        """
        Simple Spotify API client for local use
        """
        self.client_id = client_id
        self.client_secret = client_secret
        
        self.access_token = None
        
        self.used_endless_mode_tracks = set()
        
        # NEW: Threading system for background song generation
        self.song_queue = Queue(maxsize=3)  # Keep 2-3 songs ready
        self.generation_lock = threading.Lock()  # For thread safety
        self.keep_generating = True  # Flag to control background thread
        self.generation_thread = None  # Reference to background thread
        
        self.get_access_token()
        
        # NEW: Start background generation if API connection successful
        if self.access_token:
            self.start_background_generation()
    
    # NEW: Method to start background song generation
    def start_background_generation(self):
        """Start background thread to continuously generate songs"""
        def generation_worker():
            while self.keep_generating:
                try:
                    if not self.song_queue.full():
                        print("🎵 Generating song in background...")
                        song = self._generate_song_sync()  # The actual API call
                        if song:
                            self.song_queue.put(song)
                            print(f"✅ Background generated: {song.track_name}")
                    else:
                        # Queue is full, wait a bit
                        threading.Event().wait(0.5)
                except Exception as e:
                    print(f"❌ Background generation error: {e}")
                    threading.Event().wait(1)  # Wait longer on error
        
        self.generation_thread = threading.Thread(target=generation_worker, daemon=True)
        self.generation_thread.start()
        print("🚀 Background song generation started!")
        
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
        if not query or not self.access_token or len(query) <=3 :
            return []

        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "q": query,
            "type": "artist",
            "limit": 50
        }

        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            return []

        # Get artists
        all_artists = response.json().get("artists", {}).get("items", [])

        # Filter for valid artist entries with a proper ID
        valid_artists = [
            artist for artist in all_artists
            if isinstance(artist.get("id"), str) and artist["id"].strip() != ""
        ]

        query_lower = query.lower()

        def score(artist):
            name = artist["name"]
            name_lower = name.lower()
            popularity = artist.get("popularity", 0)

            # Boosts
            if name_lower == query_lower or name_lower.strip() == query_lower.strip():
                return 10000 + popularity

            if name_lower.startswith(query_lower):
                return 8000 + popularity

            query_words = query_lower.split()
            if len(query_words) > 1 and all(word in name_lower for word in query_words):
                return 6000 + popularity

            if query_lower in name_lower:
                return 4000 + popularity

            # Fallback: similarity + popularity
            name_similarity = similarity(name_lower, query_lower)
            return name_similarity * 100 + popularity * 0.5

        # Remove duplicates
        seen_ids = set()
        unique_valid_artists = []
        for artist in valid_artists:
            artist_id = artist["id"]
            if artist_id not in seen_ids:
                seen_ids.add(artist_id)
                unique_valid_artists.append(artist)

        # Sort by score
        unique_valid_artists.sort(key=score, reverse=True)

        return [
            {
                "id": artist["id"],
                "name": artist["name"],
                "popularity": artist["popularity"]
            }
            for artist in unique_valid_artists[:10]
        ]
        

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
    
    # CHANGED: endless_mode now uses queue system for instant responses
    def endless_mode(self) -> TrackInfo:
        """
        Returns a TrackInfo object from a semi-famous artist (popularity ≥ 50),
        ensuring the track hasn't been returned before.
        
        NEW: Now tries to get from preloaded queue first for instant response,
        falls back to direct generation if queue is empty.
        """
        try:
            # NEW: Try to get from preloaded queue (instant!)
            song = self.song_queue.get_nowait()
            print(f"⚡ Instant song from queue: {song.track_name}")
            return song
        except Empty:
            # NEW: Queue empty, generate directly (slower fallback)
            print("🐌 Queue empty, generating song directly...")
            return self._generate_song_sync()
    
    # NEW: Extracted the original endless_mode logic into separate method
    def _generate_song_sync(self) -> TrackInfo:
        """
        The actual song generation logic (moved from original endless_mode).
        This is the method that makes the actual API call to Spotify.
        """
        random_query = random.choice(search_queries)
        
        random_offset = random.randint(1,1000)
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
            }
        params = {
        "query": random_query,
        "offset": random_offset,
        "limit": 1,
        "type": "track",
        "market": "US"
        }

        response = requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params=params
        )
        
        
        if response.status_code == 200:
            data = response.json()
            tracks = data.get('tracks', {}).get('items', [])

            if tracks:
                track = tracks[0]

                # Ensure the artist has decent popularity
                artist_info = track['artists'][0]
                artist_name = artist_info['name']
                
                # Format duration as "mm:ss"
                duration_ms = track['duration_ms']
                minutes = duration_ms // 60000
                seconds = (duration_ms % 60000) // 1000
                duration_str = f"{minutes}:{seconds:02d}"

                #  Get image URL (if available)
                image_url = track['album']['images'][0]['url'] if track['album']['images'] else None

                # Return TrackInfo
                return TrackInfo(
                track_id=track['id'],
                track_name=track['name'],
                artist_name=track['artists'][0]['name'],
                album_name=track['album']['name'],
                release_year=track['album']['release_date'][:4],
                duration=duration_str,
                image_url=image_url
                )

            else:
                print("No tracks found.")
                return None
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
            return None
    
    # NEW: Utility methods for monitoring queue status
    def get_queue_size(self) -> int:
        """Get current number of songs in queue"""
        return self.song_queue.qsize()
    
    def is_queue_ready(self) -> bool:
        """Check if queue has songs ready"""
        return not self.song_queue.empty()
    
    def shutdown(self):
        """Clean shutdown of background generation"""
        print("🛑 Shutting down background generation...")
        self.keep_generating = False
        if self.generation_thread and self.generation_thread.is_alive():
            self.generation_thread.join(timeout=2)
        print("✅ Background generation stopped")