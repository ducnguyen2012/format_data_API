from pydantic import BaseModel
class Request_format(BaseModel):
    '''
    format for request
    '''
    alias: str
    store_id: str
    page_id: str
    conversation_id: str
    session_id: str
    message: list 