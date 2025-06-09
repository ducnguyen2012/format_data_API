from pydantic import BaseModel
class Request_format(BaseModel):
    '''
    format for request
    '''
    alias: str
    store_id: str
    page_id: str
    conversation_id: str
    ma_qc: str
    ten_kh: str
    session_id: str
    message: list 