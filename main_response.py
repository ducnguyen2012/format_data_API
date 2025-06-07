
import json
from fastapi import FastAPI, status


import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from request_format import Request_format
from call_dify import call_dify
from getContent_and_tenKH import getContent_and_tenKH



# ===================== load keys from ENV ==============================



conversation_id = "" #! first conversation only

app = FastAPI()
@app.post("/lead-chatbot")
async def response(request: Request_format):
    '''
    json.loads(request.model_dump_json()) to ensure data is json
    return: request data. type: json


    '''
    request_content,ten_KH = getContent_and_tenKH(json.loads(request.model_dump_json()))
    global conversation_id
    bot_response, conversation_id = await call_dify(request_content,conversation_id,ten_KH)
    final_response = format_response(bot_response)
    return {"message": final_response}

def format_response(bot_response):
    '''
    format to response
    response = {"state": str, "code": int, "message": str, "product": list, "faq_photos": list, "tags": list}
    '''
    response = {"state": "", "code": 200, "message": "", "product": [], "faq_photos": [], "tags": []}
    print(f"this is bot response: {bot_response}")
    response["message"] = bot_response["answer"]
    

    return response


    

