import requests

class Result:
    def __init__(self, response):
        try:
            self.response = response.json()
            self.data = self.response.get('data')
            self.error = self.response.get("error")
            self.trace_id = self.response.get("traceId")
            self.meta = self.response.get("meta")
            if self.error:
                self.data = None
                self.success = False
            else:
                self.success = True
        except:
            self.data = None
            self.error = response.text
            self.success = False

    def __str__(self) -> str:
        return f"CarthooksResult(success={self.success}, data={self.data}, error={self.error}, trace_id={self.trace_id}, meta={self.meta})"

class Client:
    def __init__(self, base_url="https://api.carthooks.com"):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
        }

    def set_access_token(self, access_token):
        self.headers['Authorization'] = f'Bearer {access_token}'

    def get_items(self, app_id, collection_id, limit=20, page=1, **options):
        options['pagination[page]'] = page
        options['pagination[pageSize]'] = limit
        response = requests.get(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items', headers=self.headers, params=options)
        return Result(response)
    
    def get_item_by_id(self, app_id, collection_id, item_id, fields):
        response = requests.get(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}', headers=self.headers, params={'fields': fields})
        return Result(response)
    
    def get_submission_token(self, app_id, collection_id, options):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/submission-token', headers=self.headers, json=options)
        return Result(response)
    
    def update_submission_token(self, app_id, collection_id, item_id, options):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/update-token', headers=self.headers, json=options)
        return Result(response)
    
    def create_item(self, app_id, collection_id, data):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items', headers=self.headers, json={'data': data})
        return Result(response)
    
    def update_item(self, app_id, collection_id, item_id, data):
        response = requests.put(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}', headers=self.headers, json={'data': data})
        return Result(response)
    
    def lock_item(self, app_id, collection_id, item_id, lock_timeout=600, lock_id=None, subject=None):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/lock', 
                                 headers=self.headers, json={'lockTimeout': lock_timeout, 'lockId': lock_id, 'lockSubject': subject}) 
        return Result(response)
    
    def unlock_item(self, app_id, collection_id, item_id, lock_id=None):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/unlock', headers=self.headers, json={'lockId': lock_id})
        return Result(response)
    
    def delete_item(self, app_id, collection_id, item_id):
        response = requests.delete(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}', headers=self.headers)
        return Result(response)
    
    def get_upload_token(self):
        response = requests.post(f'{self.base_url}/v1/uploads/token', headers=self.headers)
        return Result(response)
    
