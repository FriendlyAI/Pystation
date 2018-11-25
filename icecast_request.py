"""
requests.put('http://localhost:8000/main.mp3',
             auth=('admin', 'hackme'),
             headers={'host': 'localhost:8000',
                      'authorization': 'Basic c291cmNlOmhhY2ttZQ==',
                      'User-Agent': 'curl/7.51.0',
                      'Accept': '*/*',
                      'Transfer-Encoding': 'chunked',
                      'Content-Type': 'audio/mpeg',
                      'Ice-Public': '1',
                      'Ice-Name': 'Teststream',
                      'Ice-Description': 'This is just a simple test stream',
                      'Ice-URL': 'http://example.org',
                      'Ice-Genre': 'Rock',
                      'Expect': '100-continue'})
{'host': 'localhost:8000', 'authorization': 'Basic c291cmNlOmhhY2ttZQ==', 'User-Agent': 'curl/7.51.0', 'Accept': '*/*', 'Transfer-Encoding': 'chunked', 'Content-Type': 'audio/mpeg', 'Ice-Public': '1', 'Ice-Name': 'Teststream', 'Ice-Description': 'This is just a simple test stream', 'Ice-URL': 'http://example.org', 'Ice-Genre': 'Rock', 'Expect': '100-continue'}
"""
