'''
We can use request_format to test pydantic baseModel request in fastAPI, if we dont use we can use curl to test in postman
'''

# from pydantic import BaseModel
# class Request_format(BaseModel):
#     '''
#     format for request
#     '''
#     alias: str
#     store_id: str
#     page_id: str
#     conversation_id: str
#     ads_ids: list
#     conversation_name: str
#     session_id: str
#     message: list 