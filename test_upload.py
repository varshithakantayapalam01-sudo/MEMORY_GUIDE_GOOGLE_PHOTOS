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
    'Content-Disposition: form-data; name="files"; filename="test.jpg"',
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

try:
    with urllib.request.urlopen(upload_req) as resp:
        print('Upload Status:', resp.status)
        print('Upload Body:', resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, e.read().decode('utf-8'))
except Exception as e:
    print('Error:', e)
