import base64, requests
from .config import Settings

def create_post(title, content_html, status='publish', categories=None, tags=None):
    s = Settings()
    endpoint = s.wp_base_url2 + '/wp-json/wp/v2/posts'
    headers = {
        'Authorization':'Basic '+base64.b64encode(f"{s.wp_user}:{s.wp_app_password}".encode()).decode(),
        'Content-Type':'application/json'
    }
    payload = {'title': title, 'content': content_html, 'status': status}
    if categories: payload['categories'] = categories
    if tags: payload['tags'] = tags
    r = requests.post(endpoint, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    return r.json()
