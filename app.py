import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from call_dify import call_dify
from DifyAPI.get_content_ten_maqc import get_content_ten_maqc
import os
import redis


#! ======================================================== call redis client in env ==========================================================================
#redis_client = redis.Redis(host=os.getenv("REDIS_HOST"),port=os.getenv("REDIS_PORT"),db=os.getenv("REDIS_DB"),decode_responses=True)
redis_client = redis.Redis(host='localhost',port=6379,db=0,decode_responses=True)
#! ============================================================================================================================================================



#! ======================================================== get all keys from env =============================================================================
app = FastAPI()

#! ============================================================================================================================================================

@app.post("/api/lead/chat/completions")
async def response(request: Request):
    '''
    json.loads(request.model_dump_json()) to ensure data is json
    return: request data. type: json
    '''

    '''
    Idea for save map variable request_conversation_id : dify conversation_id:
    1. redis_client.get([json_request.get("conversation_id"),json_request.get("session_id")]) or "": get value assign by a list of request.conversation_id and request.session_id
    and assigned it to dify_conversation_id. If it is first time, it will be ""
    2. update_dify_conversation_id with call_dify. 
    3. if (updated_dify_conversation_id and not dify_conversation_id): if update_dify_conversation_id not None and dify_conversation_id is None:
        3.1. map request_conversation_id with updated_dify_conversation_id
        3.2. assign dify_conversation_id = updated_dify_conversation_id

    '''
    token = request.headers.get('Bot-Api-Token')
    

    #! if token is invalid
    if not token or token != f"{os.getenv('AI_API_KEY')}": 
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
    
    #! convert request to json
    json_request = await request.json()
    
    #! get content, tenKH, maqc in request
    request_content,ten_KH,ma_qc = get_content_ten_maqc(json_request)
    
    #! let the conversation_id and session_id as key for retrieve 
    request_conversation_id_and_session_id = json.dumps([json_request.get("conversation_id"),json_request.get("session_id")])
    
    #! if that key already exist, then get it, else let it be ""
    redis_value = redis_client.get(request_conversation_id_and_session_id) or ""

    #! if redis_value != None -> return it
    if redis_value:
        dify_conversation_id_and_session_id = json.loads(redis_value)
    else:
        '''
        If there is no redis_value -> reset conversation_id and session id
        '''
        dify_conversation_id_and_session_id = ["",""]


    #! ================================================== call dify ============================================================================
    updated_dify_conversation_id, updated_dify_session_id,bot_response = "","",""
    try:
        conversation_id = dify_conversation_id_and_session_id[0]
        session_id = dify_conversation_id_and_session_id[1]
        bot_response, updated_dify_conversation_id, updated_dify_session_id = await call_dify(request_content, conversation_id, session_id, ten_KH, ma_qc,json_request.get("conversation_id"))

    except httpx.HTTPStatusError as exc:
        response = {"answer": f"HTTP Status Error: {exc.response.status_code} - {exc.response.text}"}
        print(response)
    except httpx.RequestError as messageErr:
        response = {"answer": f"Request Error: {messageErr}"}
        print(response)
    except httpx.TimeoutException as timeout:
        response = {"answer": f"Timeout Error: {timeout}"}
        print(response)
    except httpx.ConnectError as connect_err:
        response = {"answer": f"Connect Error: {connect_err}"}
        print(response)
    except httpx.NetworkError as network_err:
        response = {"answer": f"Network Error: {network_err}"}
        print(response)
    except httpx.ProtocolError as protocol_err:
        response = {"answer": f"Protocol Error: {protocol_err}"}
        print(response)
    except httpx.TransportError as transport_err:
        response = {"answer": f"Transport Error: {transport_err}"}
        print(response)
    except httpx.HTTPError as http_err:
        response = {"answer": f"Generic HTTP Error: {http_err}. Reset conversation_id, session_id and call_dify again"}
        dify_conversation_id_and_session_id = ["",""]
        bot_response, updated_dify_conversation_id, updated_dify_session_id = await call_dify(request_content, conversation_id, session_id, ten_KH, ma_qc,json_request.get("conversation_id"))
        print(response)
    except Exception as e:
        response = {"answer": f"Unexpected Error: {e}"}
        dify_conversation_id_and_session_id = ["",""]
        bot_response, updated_dify_conversation_id, updated_dify_session_id = await call_dify(request_content, conversation_id, session_id, ten_KH, ma_qc,json_request.get("conversation_id"))
        print(response)
    
        
        
    # handle case update
    if (updated_dify_conversation_id and not conversation_id):
        '''
        If there is an error, it will reset both conversation_id and session_id
        '''
        new_session_info = [updated_dify_conversation_id, updated_dify_session_id]
        redis_client.set(request_conversation_id_and_session_id, json.dumps(new_session_info))
        dify_conversation_id_and_session_id = new_session_info
    
    #If there are some bugs while calling api, it gonna reset conversation id and call dify again
    
    

    #! ============================================== push all information to database ============================================
    final_response = format_response(bot_response, updated_dify_conversation_id, updated_dify_session_id)

    return JSONResponse(content = final_response, status_code=200)

def format_response(bot_response, updated_dify_conversation_id, updated_dify_session_id):
    #! setup for parameter: 
    code = 200
    tags = [] #! we will handle case push tag in api tag in dify
    state = "done"
    #! if bot response contains "chuyển cho nhân viên" -> role is staff
    role = "bot"
    if ("chuyển cho nhân viên" in bot_response["answer"]):
        role = "staff"
    bot_response["dify_conversation_id"] = updated_dify_conversation_id
    bot_response["dify_session_id"] = updated_dify_session_id
    bot_response["role"] = role
    bot_response["code"] = code
    bot_response["tags"] = tags
    bot_response["state"] = state
    bot_response["message"] = {"content": bot_response["answer"], "products": []}
    bot_response["faq_photos"] = []

    return bot_response


#! =============================================================== log error =========================================================
    
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
            # f"Request: {request.method} {request.url}\n"
            # f"Headers: {dict(request.headers)}\n"
            # f"Body: {body.decode()}\n"
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
    

