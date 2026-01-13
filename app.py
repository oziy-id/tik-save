from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import time
import urllib.parse
import glob

app = Flask(__name__)

# Buat folder downloads jika belum ada
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    tiktok_url = data.get('url')

    if not tiktok_url:
        return jsonify({'error': 'URL tidak boleh kosong'}), 400

    print(f"🔍 Menganalisa Info: {tiktok_url}")

    try:
        # Tahap 1: Cuma ambil Info (Judul, Thumbnail) - Jangan download dulu
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tiktok_url, download=False)
            
            # Kita kirim LINK ASLI TIKTOK (bukan link CDN) ke rute download kita
            # Supaya nanti rute download bisa memproses ulang dengan yt-dlp
            encoded_url = urllib.parse.quote_plus(tiktok_url)
            local_download_link = f"/process_download?url={encoded_url}"

            video_data = {
                'success': True,
                'data': {
                    'title': info.get('title', 'Video TikTok'),
                    'author': info.get('uploader', 'Unknown'),
                    'avatar': 'https://ui-avatars.com/api/?name=User&background=random',
                    'cover': info.get('thumbnail', ''),
                    'download_url': local_download_link 
                }
            }
            return jsonify(video_data)

    except Exception as e:
        print(f"❌ Error Analyze: {e}")
        return jsonify({'success': False, 'error': 'Gagal mengambil info video.'}), 500


@app.route('/process_download')
def process_download():
    # Ambil URL Asli TikTok
    raw_url = request.args.get('url')
    if not raw_url:
        return "URL Error", 400
        
    tiktok_url = urllib.parse.unquote_plus(raw_url)
    
    # Nama file unik berdasarkan waktu agar tidak bentrok
    filename = f"video_{int(time.time())}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    print("⬇️  Sedang mendownload ke server...")

    try:
        # Bersihkan file lama dulu (Opsional: agar harddisk tidak penuh)
        files = glob.glob(os.path.join(DOWNLOAD_FOLDER, '*'))
        for f in files:
            try:
                os.remove(f)
            except:
                pass

        # KONFIGURASI DOWNLOADER FISIK
        ydl_opts = {
            'format': 'best',             # Kualitas terbaik
            'outtmpl': filepath,          # Simpan ke folder downloads/
            'quiet': True,
            'no_warnings': True,
            # User Agent Topeng
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }

        # EKSEKUSI DOWNLOAD KE DISK
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tiktok_url])

        print("✅ Download Selesai! Mengirim ke user...")

        # Kirim file fisik tersebut ke browser user
        return send_file(filepath, as_attachment=True, download_name='TikSave_Video.mp4')

    except Exception as e:
        print(f"❌ Gagal Download: {e}")
        return f"Gagal mendownload video: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
