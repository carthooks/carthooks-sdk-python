import requests
import os

class Result:
    def __init__(self, response):
        self.trace_id = None
        self.meta = None
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

    def __getitem__(self, key):
        return self.data.get(key)

    def __str__(self) -> str:
        return f"CarthooksResult(success={self.success}, data={self.data}, error={self.error})"

class Client:
    def __init__(self):
        self.base_url = os.getenv('CARTHOOKS_API_URL')
        if self.base_url == None:
            self.base_url = "https://api.carthooks.com"
        self.headers = {
            'Content-Type': 'application/json',
        }

    def setAccessToken(self, access_token):
        self.headers['Authorization'] = f'Bearer {access_token}'

    def getItems(self, app_id, collection_id, limit=20, page=1, **options):
        options['pagination[page]'] = page
        options['pagination[pageSize]'] = limit
        url = f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items'
        print(options)
        response = requests.get(url, headers=self.headers, params=options)
        return Result(response)
    
    def getItemById(self, app_id, collection_id, item_id, fields=None):
        response = requests.get(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}', headers=self.headers)
        return Result(response)
    

# POST    /open/api/v1/apps/:app_id/collections/:entity_id/items/:row_id/subform/:field_id/     OpenAPI.CreateSubItem
# PUT     /open/api/v1/apps/:app_id/collections/:entity_id/items/:row_id/subform/:field_id/items/:sub_row_id/:sub_row_id     OpenAPI.UpdateSubItem
# DELETE  /open/api/v1/apps/:app_id/collections/:entity_id/items/:row_id/subform/:field_id/items/:sub_row_id/:sub_row_id     OpenAPI.DeleteSubItem
    def createSubItem(self, app_id, collection_id, item_id, field_id, data):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/subform/{field_id}', headers=self.headers, json={'data': data})
        return Result(response)
    
    def updateSubItem(self, app_id, collection_id, item_id, field_id, sub_item_id, data):
        print("data", data)
        response = requests.put(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/subform/{field_id}/items/{sub_item_id}', headers=self.headers, json={'data': data})
        return Result(response)
    
    def deleteSubItem(self, app_id, collection_id, item_id, field_id, sub_item_id):
        response = requests.delete(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/subform/{field_id}/items/{sub_item_id}', headers=self.headers)
        return Result(response)
    
    def getSubmissionToken(self, app_id, collection_id, options):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/submission-token', headers=self.headers, json=options)
        return Result(response)
    
    def updateSubmissionToken(self, app_id, collection_id, item_id, options):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/update-token', headers=self.headers, json=options)
        return Result(response)
    
    def createItem(self, app_id, collection_id, data):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items', headers=self.headers, json={'data': data})
        return Result(response)
    
    def updateItem(self, app_id, collection_id, item_id, data):
        response = requests.put(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}', headers=self.headers, json={'data': data})
        return Result(response)
    
    def lockItem(self, app_id, collection_id, item_id, lock_timeout=600, lock_id=None, subject=None):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/lock', 
                                 headers=self.headers, json={'lockTimeout': lock_timeout, 'lockId': lock_id, 'lockSubject': subject}) 
        return Result(response)
    
    def unlockItem(self, app_id, collection_id, item_id, lock_id=None):
        response = requests.post(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/unlock', headers=self.headers, json={'lockId': lock_id})
        return Result(response)
    
    def deleteItem(self, app_id, collection_id, item_id):
        response = requests.delete(f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}', headers=self.headers)
        return Result(response)
    
    def get_upload_token(self):
        response = requests.post(f'{self.base_url}/v1/uploads/token', headers=self.headers)
        return Result(response)
    
