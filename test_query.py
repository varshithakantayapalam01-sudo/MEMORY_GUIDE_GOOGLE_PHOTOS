import urllib.request
import urllib.error
import json

base_url = 'https://memoryguidegooglephotos-production.up.railway.app/api/v1'

# 1. Create session
req = urllib.request.Request(f'{base_url}/sessions', data=json.dumps({'mode': 'research'}).encode('utf-8'), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    session_id = res['data']['sessionId']
    print('Created session:', session_id)

# 2. Upload photo
url = f'{base_url}/sessions/{session_id}/upload'
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body_parts = [
    f'--{boundary}',
    'Content-Disposition: form-data; name="files"; filename="cake_photo.jpg"',
    'Content-Type: image/jpeg',
    '',
    'fakejpegbytes1234567890',
    f'--{boundary}--',
    ''
]
body = '\r\n'.join(body_parts).encode('utf-8')

upload_req = urllib.request.Request(url, data=body, headers={
    'Content-Type': f'multipart/form-data; boundary={boundary}'
})

with urllib.request.urlopen(upload_req) as resp:
    print('Upload Status:', resp.status)
    print('Upload Body:', resp.read().decode('utf-8'))

# 3. Check profiles
profiles_url = f'{base_url}/sessions/{session_id}/profiles'
with urllib.request.urlopen(profiles_url) as resp:
    print('Profiles:', resp.read().decode('utf-8'))

# 4. Query
query_url = f'{base_url}/sessions/{session_id}/query'
query_req = urllib.request.Request(query_url, data=json.dumps({'query': 'cake'}).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(query_req) as resp:
        print('Query Status:', resp.status)
        print('Query Response:', resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP Error on Query:', e.code)
    print('Error Body:', e.read().decode('utf-8'))
