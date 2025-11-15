#!/usr/bin/env python3
"""
Media Center Pro Service
Comprehensive music/video library management on 256GB storage
Port: 9500
"""

import os
import sys
import threading
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.media.database import MediaDatabase
from services.media.scanner import MediaScanner
from services.media.metadata import MetadataExtractor
from services.media.player import PlayerIntegration

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'media-center-secret-key')
CORS(app)

db = MediaDatabase()
scanner = MediaScanner()
metadata_extractor = MetadataExtractor()
player = PlayerIntegration(db)

scan_in_progress = False
scan_progress = {'current': 0, 'total': 0, 'file': ''}


@app.route('/')
def index():
    """Serve the main media center UI."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('MEDIA_PORT', 9500))
    stats = db.get_stats()
    
    return jsonify({
        'ok': True,
        'service': 'media_center_pro',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'library_stats': stats
    })


@app.route('/api/library/scan', methods=['POST'])
def scan_library():
    """Scan library for music and video files."""
    global scan_in_progress, scan_progress
    
    if scan_in_progress:
        return jsonify({'ok': False, 'error': 'Scan already in progress'}), 400
    
    data = request.json or {}
    scan_type = data.get('type', 'both')
    
    def scan_worker():
        global scan_in_progress, scan_progress
        scan_in_progress = True
        
        try:
            if scan_type in ['music', 'both']:
                scan_progress = {'current': 0, 'total': 0, 'file': 'Scanning music...'}
                music_files = scanner.scan_music()
                
                for i, file_data in enumerate(music_files):
                    scan_progress = {
                        'current': i + 1,
                        'total': len(music_files),
                        'file': file_data['file_name']
                    }
                    
                    metadata = metadata_extractor.extract_music_metadata(file_data['file_path'])
                    file_data.update(metadata)
                    
                    track_id = db.add_music_track(file_data)
                    
                    if metadata_extractor.mock_mode:
                        file_data['album_art_path'] = metadata_extractor.extract_album_art(
                            file_data['file_path'], track_id
                        )
                        if file_data['album_art_path']:
                            db.add_music_track({'file_path': file_data['file_path'], 
                                              'album_art_path': file_data['album_art_path']})
            
            if scan_type in ['video', 'both']:
                scan_progress = {'current': 0, 'total': 0, 'file': 'Scanning videos...'}
                video_files = scanner.scan_videos()
                
                for i, file_data in enumerate(video_files):
                    scan_progress = {
                        'current': i + 1,
                        'total': len(video_files),
                        'file': file_data['file_name']
                    }
                    
                    metadata = metadata_extractor.extract_video_metadata(file_data['file_path'])
                    file_data.update(metadata)
                    
                    video_id = db.add_video_file(file_data)
                    
                    if metadata_extractor.mock_mode:
                        file_data['thumbnail_path'] = metadata_extractor.generate_video_thumbnail(
                            file_data['file_path'], video_id
                        )
                        if file_data['thumbnail_path']:
                            db.add_video_file({'file_path': file_data['file_path'],
                                             'thumbnail_path': file_data['thumbnail_path']})
            
            storage_stats = scanner.get_storage_usage()
            db.update_storage_stats(storage_stats)
            
        finally:
            scan_in_progress = False
            scan_progress = {'current': 0, 'total': 0, 'file': ''}
    
    thread = threading.Thread(target=scan_worker, daemon=True)
    thread.start()
    
    return jsonify({
        'ok': True,
        'message': f'Library scan started ({scan_type})',
        'scan_type': scan_type
    })


@app.route('/api/library/scan/progress')
def scan_progress_status():
    """Get scan progress."""
    return jsonify({
        'ok': True,
        'scanning': scan_in_progress,
        'progress': scan_progress
    })


@app.route('/api/library/stats')
def library_stats():
    """Get library statistics."""
    stats = db.get_stats()
    storage_stats = db.get_latest_storage_stats()
    
    return jsonify({
        'ok': True,
        'stats': stats,
        'storage': storage_stats
    })


@app.route('/api/music/all')
def get_all_music():
    """Get all music tracks."""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    tracks = db.get_all_music(limit, offset)
    
    return jsonify({
        'ok': True,
        'tracks': tracks,
        'count': len(tracks)
    })


@app.route('/api/music/search')
def search_music():
    """Search music tracks."""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 100))
    
    if not query:
        return jsonify({'ok': False, 'error': 'Query parameter required'}), 400
    
    results = db.search_music(query, limit)
    
    return jsonify({
        'ok': True,
        'results': results,
        'count': len(results)
    })


@app.route('/api/music/artists')
def get_artists():
    """Get all artists."""
    artists = db.get_artists()
    
    return jsonify({
        'ok': True,
        'artists': artists
    })


@app.route('/api/music/albums')
def get_albums():
    """Get all albums."""
    artist = request.args.get('artist')
    albums = db.get_albums(artist)
    
    return jsonify({
        'ok': True,
        'albums': albums,
        'artist': artist
    })


@app.route('/api/music/genres')
def get_genres():
    """Get all genres."""
    genres = db.get_genres()
    
    return jsonify({
        'ok': True,
        'genres': genres
    })


@app.route('/api/videos/all')
def get_all_videos():
    """Get all video files."""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    videos = db.get_all_videos(limit, offset)
    
    return jsonify({
        'ok': True,
        'videos': videos,
        'count': len(videos)
    })


@app.route('/api/playlists')
def get_playlists():
    """Get all playlists."""
    playlists = db.get_playlists()
    
    return jsonify({
        'ok': True,
        'playlists': playlists
    })


@app.route('/api/playlists/create', methods=['POST'])
def create_playlist():
    """Create a new playlist."""
    data = request.json or {}
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'ok': False, 'error': 'Playlist name required'}), 400
    
    playlist_id = db.create_playlist(name, description)
    
    return jsonify({
        'ok': True,
        'playlist_id': playlist_id,
        'message': f'Playlist "{name}" created'
    })


@app.route('/api/playlists/<int:playlist_id>/tracks')
def get_playlist_tracks(playlist_id):
    """Get tracks in a playlist."""
    tracks = db.get_playlist_tracks(playlist_id)
    
    return jsonify({
        'ok': True,
        'playlist_id': playlist_id,
        'tracks': tracks
    })


@app.route('/api/playlists/<int:playlist_id>/add', methods=['POST'])
def add_to_playlist(playlist_id):
    """Add track to playlist."""
    data = request.json or {}
    track_id = data.get('track_id')
    
    if not track_id:
        return jsonify({'ok': False, 'error': 'track_id required'}), 400
    
    success = db.add_to_playlist(playlist_id, track_id)
    
    if success:
        return jsonify({
            'ok': True,
            'message': 'Track added to playlist'
        })
    else:
        return jsonify({
            'ok': False,
            'error': 'Track already in playlist or error occurred'
        }), 400


@app.route('/api/playlists/smart/recently-added')
def smart_playlist_recent():
    """Get recently added tracks."""
    limit = int(request.args.get('limit', 50))
    tracks = db.get_recently_added(limit)
    
    return jsonify({
        'ok': True,
        'playlist_name': 'Recently Added',
        'tracks': tracks
    })


@app.route('/api/playlists/smart/most-played')
def smart_playlist_most_played():
    """Get most played tracks."""
    limit = int(request.args.get('limit', 50))
    tracks = db.get_most_played(limit)
    
    return jsonify({
        'ok': True,
        'playlist_name': 'Most Played',
        'tracks': tracks
    })


@app.route('/api/playlists/smart/favorites')
def smart_playlist_favorites():
    """Get favorite tracks."""
    tracks = db.get_favorites()
    
    return jsonify({
        'ok': True,
        'playlist_name': 'Favorites',
        'tracks': tracks
    })


@app.route('/api/playlists/smart/genre/<genre>')
def smart_playlist_genre(genre):
    """Get tracks by genre."""
    limit = int(request.args.get('limit', 100))
    tracks = db.get_by_genre(genre, limit)
    
    return jsonify({
        'ok': True,
        'playlist_name': f'{genre} Music',
        'tracks': tracks
    })


@app.route('/api/player/play', methods=['POST'])
def player_play():
    """Play a track."""
    data = request.json or {}
    track_id = data.get('track_id')
    
    if not track_id:
        return jsonify({'ok': False, 'error': 'track_id required'}), 400
    
    result = player.play_track(track_id)
    
    return jsonify({
        'ok': result['success'],
        'result': result
    })


@app.route('/api/player/pause', methods=['POST'])
def player_pause():
    """Pause playback."""
    result = player.pause()
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/player/resume', methods=['POST'])
def player_resume():
    """Resume playback."""
    result = player.resume()
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/player/stop', methods=['POST'])
def player_stop():
    """Stop playback."""
    result = player.stop()
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/player/next', methods=['POST'])
def player_next():
    """Skip to next track."""
    result = player.next_track()
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/player/previous', methods=['POST'])
def player_previous():
    """Go to previous track."""
    result = player.previous_track()
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/player/now-playing')
def player_now_playing():
    """Get now playing info."""
    now_playing = player.get_now_playing()
    
    return jsonify({
        'ok': True,
        'now_playing': now_playing
    })


@app.route('/api/player/queue')
def player_get_queue():
    """Get play queue."""
    queue = player.get_queue()
    
    return jsonify({
        'ok': True,
        'queue': queue
    })


@app.route('/api/player/queue/add', methods=['POST'])
def player_add_to_queue():
    """Add tracks to queue."""
    data = request.json or {}
    track_ids = data.get('track_ids', [])
    
    if not track_ids:
        return jsonify({'ok': False, 'error': 'track_ids required'}), 400
    
    result = player.add_to_queue(track_ids)
    
    return jsonify({
        'ok': result['success'],
        'result': result
    })


@app.route('/api/player/queue/clear', methods=['POST'])
def player_clear_queue():
    """Clear queue."""
    result = player.clear_queue()
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/player/shuffle', methods=['POST'])
def player_shuffle():
    """Set shuffle mode."""
    data = request.json or {}
    enabled = data.get('enabled', False)
    
    result = player.set_shuffle(enabled)
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/player/repeat', methods=['POST'])
def player_repeat():
    """Set repeat mode."""
    data = request.json or {}
    mode = data.get('mode', 'off')
    
    result = player.set_repeat(mode)
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/player/playlist/<int:playlist_id>', methods=['POST'])
def player_play_playlist(playlist_id):
    """Play a playlist."""
    result = player.play_playlist(playlist_id)
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/player/album', methods=['POST'])
def player_play_album():
    """Play an album."""
    data = request.json or {}
    artist = data.get('artist')
    album = data.get('album')
    
    if not artist or not album:
        return jsonify({'ok': False, 'error': 'artist and album required'}), 400
    
    result = player.play_album(artist, album)
    return jsonify({'ok': result['success'], 'result': result})


@app.route('/api/duplicates')
def get_duplicates():
    """Get duplicate tracks."""
    resolved = request.args.get('resolved', 'false').lower() == 'true'
    duplicates = db.get_duplicates(resolved)
    
    return jsonify({
        'ok': True,
        'duplicates': duplicates
    })


@app.route('/api/duplicates/scan', methods=['POST'])
def scan_duplicates():
    """Scan for duplicate tracks."""
    tracks = db.get_all_music(limit=10000)
    duplicates = scanner.find_duplicates(tracks)
    
    for dup in duplicates:
        db.record_duplicate(
            dup['track1']['id'],
            dup['track2']['id'],
            dup['similarity_score'],
            dup['match_type']
        )
    
    return jsonify({
        'ok': True,
        'duplicates_found': len(duplicates),
        'message': f'Found {len(duplicates)} potential duplicates'
    })


@app.route('/api/storage')
def get_storage_info():
    """Get storage information."""
    storage_stats = db.get_latest_storage_stats()
    current_stats = scanner.get_storage_usage()
    
    return jsonify({
        'ok': True,
        'current': current_stats,
        'historical': storage_stats
    })


@app.route('/api/metadata/update', methods=['POST'])
def update_metadata():
    """Update track metadata."""
    data = request.json or {}
    track_id = data.get('track_id')
    updates = data.get('updates', {})
    
    if not track_id:
        return jsonify({'ok': False, 'error': 'track_id required'}), 400
    
    success = metadata_extractor.update_metadata(
        updates.get('file_path', ''),
        updates
    )
    
    if success:
        db.add_music_track({**updates, 'file_path': updates.get('file_path')})
    
    return jsonify({
        'ok': success,
        'message': 'Metadata updated' if success else 'Update failed'
    })


if __name__ == '__main__':
    port = int(os.environ.get('MEDIA_PORT', 9500))
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║             Media Center Pro - Version 1.0.0                 ║
╠══════════════════════════════════════════════════════════════╣
║  Comprehensive Music & Video Library Management              ║
║  Port: {port}                                                    ║
║  Storage: 256GB                                              ║
║                                                              ║
║  Features:                                                   ║
║  • Music Library Management                                  ║
║  • Video Library Organization                                ║
║  • Smart Playlists & AI Recommendations                      ║
║  • Android Player Integration                                ║
║  • Metadata Extraction & Editing                             ║
║  • Duplicate Detection                                       ║
║  • Storage Management                                        ║
║                                                              ║
║  Access: http://localhost:{port}                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False)
