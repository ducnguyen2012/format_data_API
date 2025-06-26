import os
import httpx
from dotenv import load_dotenv

load_dotenv()

#! ===================================================================== get all keys in env =====================================================
API_KEY = os.getenv("DIFY_LEAD_CHAT_API_KEY")
URL = os.getenv("DIFY_CHAT_URL")
#! ===============================================================================================================================================



async def call_dify(user_message: str, conversation_id: str, session_id: str, ten_KH: str, ma_qc: list,request_conversation_id: str):
    '''
    This function will call bot api and return its response in json

    input: (format the input of Request from social) 
        - user_message: str, 
        - conversation_id_and_session_id: list (from request), 
        - ten_KH: str, 
        - ma_qc: list
    
    output: (response from bot)
        - Response from bot: str,
        - conversation_id: str (from dify),
        - session_id: str (from dify)
    '''
    url = URL
    print(f"this is my url: {url}")
    

    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        "Content-Type": "application/json"
    }
     
    data_raw = {
        "inputs": {"ten_kh": ten_KH, "ma_qc": str(ma_qc),"session_id": session_id, "request_conversation_id": request_conversation_id},
        "query": user_message,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": ten_KH
    }
    print(f"This is my dataraw: {data_raw}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url=url, headers=headers, json=data_raw)
        
        response.raise_for_status()
        response_dict = response.json()
        
        conversation_id = response_dict.get("conversation_id", conversation_id)
        session_id = response_dict.get("session_id", session_id)
        return response_dict, conversation_id, session_id
    '''
    Note: you shouldn't do exception in here because in main when i call_dify i already solve exception!
    '''