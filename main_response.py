
import json
from fastapi import FastAPI, status


import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from request_format import Request_format
from call_dify import call_dify
from getContent_and_tenKH_maqc import getContent_and_tenKH_maqc



# ===================== define redis variable ==============================

import redis

redis_client = redis.Redis(host='localhost',port=6379,db=0,decode_responses=True)


app = FastAPI()
@app.post("/lead-chatbot")
async def response(request: Request_format):
    # print(f"this is my request: {request}")
    '''
    json.loads(request.model_dump_json()) to ensure data is json
    return: request data. type: json
    '''

    '''
    Idea for save map variable request_conversation_id : dify conversation_id:
    1. redis_client.get(request_conversation_id) or "": get value assign by request.conversation_id 
    and assigned it to dify_conversation_id. If it is first time, it will be ""
    2. update_dify_conversation_id with call_dify. 
    3. if (updated_dify_conversation_id and not dify_conversation_id): if update_dify_conversation_id not None and dify_conversation_id is None:
        3.1. map request_conversation_id with updated_dify_conversation_id
        3.2. assign dify_conversation_id = updated_dify_conversation_id

    '''
   # print(f"This is my request format: {json.loads(request.model_dump_json())}")
    request_content,ten_KH,ma_qc = getContent_and_tenKH_maqc(json.loads(request.model_dump_json()))
    request_conversation_id = f"{request.conversation_id}"
    dify_conversation_id = redis_client.get(request_conversation_id) or ""


    bot_response, updated_dify_conversation_id = await call_dify(request_content,dify_conversation_id,ten_KH,ma_qc)

    if (updated_dify_conversation_id and not dify_conversation_id):
        redis_client.setex(request_conversation_id, 86400,updated_dify_conversation_id)
        dify_conversation_id = updated_dify_conversation_id
    
    final_response = format_response(bot_response)


    # print(f"this is my request conversation id: {request_conversation_id}")
    # print(f"This is my dify conversation id: {dify_conversation_id}")
    return {"message": final_response}

def format_response(bot_response):
    '''
    format to response
    response = {"state": str, "code": int, "message": str, "product": list, "faq_photos": list, "tags": list}
    '''

    response = {"state": "", "code": 200, "message": "", "product": [], "faq_photos": [], "tags": []}

    # print(f"this is bot response: {bot_response}")
    response["message"] = bot_response["answer"]
    

    return response


    
