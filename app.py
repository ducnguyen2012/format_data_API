import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
# from request_format import Request_format
from call_dify import call_dify
from getContent_and_tenKH_maqc import getContent_and_tenKH_maqc
import os
import redis
from push_lead_DB import push_log_and_lead_information_to_DB
#redis_client = redis.Redis(host=os.getenv("REDIS_HOST"),port=os.getenv("REDIS_PORT"),db=os.getenv("REDIS_DB"),decode_responses=True)
redis_client = redis.Redis(host='localhost',port=6379,db=0,decode_responses=True)


app = FastAPI()

DB_NAME=os.getenv("DB_NAME"),
USER_NAME=os.getenv("USER_NAME"),
HOST_IP=os.getenv("HOST_IP"),
PASSWORD=os.getenv("PASSWORD"),
PORT=os.getenv("PORT")
@app.post("/api/lead/chat/completions")
async def response(request: Request):
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
    token = request.headers.get('Bot-Api-Token')
    token = "f16dbaef3aa33238b9697758fd816ce2"
    if not token or token != f"{os.getenv('AI_API_KEY')}": 
        print(f"this is my token: {token}")
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
    json_request = await request.json()
    
    request_content,ten_KH,ma_qc = getContent_and_tenKH_maqc(json_request)
    
    #! let the conversation_id and session_id as key for retrieve 
    request_conversation_id_and_session_id = json.dumps([json_request.get("conversation_id"),json_request.get("session_id")])
    
    redis_value = redis_client.get(request_conversation_id_and_session_id) or ""
    if redis_value:
        dify_conversation_id_and_session_id = json.loads(redis_value)
    else:
        dify_conversation_id_and_session_id = ["",""]
    try:
        bot_response, updated_dify_conversation_id, updated_dify_session_id = await call_dify(request_content, dify_conversation_id_and_session_id, ten_KH, ma_qc)
        print(f"this is bot response: {bot_response}")
    except Exception as e:
        '''
        Để là Exception chung để reset conversation_id và session_id với mọi lỗi
        '''
        print(f"Error in call_dify in app.py: {e}")
        dify_conversation_id_and_session_id = ["",""]
        bot_response, updated_dify_conversation_id, updated_dify_session_id = await call_dify(request_content, dify_conversation_id_and_session_id, ten_KH, ma_qc)
    

    if (updated_dify_conversation_id and not dify_conversation_id_and_session_id[0]):
        new_session_info = [updated_dify_conversation_id, updated_dify_session_id]
        redis_client.set(request_conversation_id_and_session_id, json.dumps(new_session_info))
        dify_conversation_id_and_session_id = new_session_info
    #print(f"This is updated_dify_conversation_id and updated_dify_session_id: {updated_dify_conversation_id} and {updated_dify_session_id}")
    '''
    If there are some bugs while calling api, it gonna reset conversation id and call dify again
    '''
    

    #! ============================================== push all information to database ============================================
    json_data_add_conversationID_and_sessionID_to_bot = {
        "botResponse": bot_response,
        "conversation_id": updated_dify_conversation_id,
        "session_id": updated_dify_session_id
    }
    final_response = format_response(bot_response)

    responseStatus = {
        'statusCode': 200
    }
    push_log_and_lead_information_to_DB(socialRequest=json_request,json_data_add_conversationID_and_sessionID_to_bot=json_data_add_conversationID_and_sessionID_to_bot, responseStatus=responseStatus)
    return JSONResponse(content = final_response, status_code=200)

def format_response(bot_response):
    '''
    format to response
    response = {"state": str, "code": int, "message": str, "product": list, "faq_photos": list, "tags": list}
    '''
    response = {"state": "", "code": 200, "messages": [{"content": bot_response["answer"], "products": []}], "faq_photos": [], "tags": []}
    return response

    
import logging
logger = logging.getLogger("uvicorn.error")
from starlette.responses import Response

@app.middleware("http")
async def log_errors(request: Request, call_next):
    body = await request.body()

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(
            f"Request: {request.method} {request.url}\n"
            f"Headers: {dict(request.headers)}\n"
            f"Body: {body.decode()}\n"
            f"Exception in log_errors: {str(e)}"
        )
        return Response("Internal Server Error", status_code=500)

    if response.status_code >= 400:
        logger.error(
            f"Request: {request.method} {request.url} - {response.status_code}\n"
            f"Headers: {dict(request.headers)}\n"
            f"Body: {body.decode()}\n"
        )
    return response
    

