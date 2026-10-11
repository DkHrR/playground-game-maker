import app
from app import app as flask_app, init_db
import json
import os

os.environ['MOCK_MODEL'] = '1'
app.DB_FILE = 'temp_test.sqlite'
init_db()

with flask_app.test_client() as client:
    res = client.post('/api/generate', json={'players': 2, 'age': '10', 'items': 'ball', 'space': 'yard', 'minutes': 20})
    data = res.get_json()
    if data['success'] and data['source'] == 'mock' and data['game']['name'] == 'Ghost Tag':
        print('PASS: Mock generation')
    else:
        print('FAIL: Mock generation')

    res = client.post('/api/save_stats', json={
        'name': 'Ghost Tag', 'screen_seconds': 45, 'outside_minutes': 20, 'rating': 5, 'notes': 'Fun!', 'source': 'mock'
    })
    if res.get_json()['success']:
        print('PASS: Save Stats')
    else:
        print('FAIL: Save Stats')
