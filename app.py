import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from call_dify import call_dify
from getContent_and_tenKH_maqc import getContent_and_tenKH_maqc
import os
import redis
from push_lead_DB import push_log_and_lead_information_to_DB

#! ======================================================== call redis client in env ==========================================================================
#redis_client = redis.Redis(host=os.getenv("REDIS_HOST"),port=os.getenv("REDIS_PORT"),db=os.getenv("REDIS_DB"),decode_responses=True)
redis_client = redis.Redis(host='localhost',port=6379,db=0,decode_responses=True)
#! ============================================================================================================================================================



#! ======================================================== get all keys from env =============================================================================
app = FastAPI()
DB_NAME=os.getenv("DB_NAME"),
USER_NAME=os.getenv("USER_NAME"),
HOST_IP=os.getenv("HOST_IP"),
PASSWORD=os.getenv("PASSWORD"),
PORT=os.getenv("PORT")
#! ============================================================================================================================================================

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

    #! if token is invalid
    if not token or token != f"{os.getenv('AI_API_KEY')}": 
        print(f"this is my token: {token}")
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
    
    #! convert request to json
    json_request = await request.json()
    
    #! get content, tenKH, maqc in request
    request_content,ten_KH,ma_qc = getContent_and_tenKH_maqc(json_request)
    
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
        bot_response, updated_dify_conversation_id, updated_dify_session_id = await call_dify(request_content, dify_conversation_id_and_session_id, ten_KH, ma_qc)
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
        bot_response, updated_dify_conversation_id, updated_dify_session_id = await call_dify(request_content, dify_conversation_id_and_session_id, ten_KH, ma_qc)
        print(response)
    except Exception as e:
        response = {"answer": f"Unexpected Error: {e}"}
        dify_conversation_id_and_session_id = ["",""]
        bot_response, updated_dify_conversation_id, updated_dify_session_id = await call_dify(request_content, dify_conversation_id_and_session_id, ten_KH, ma_qc)
        print(response)
    
        
        
    '''
    Handle the case update 
    '''
    if (updated_dify_conversation_id and not dify_conversation_id_and_session_id[0]):
        new_session_info = [updated_dify_conversation_id, updated_dify_session_id]
        redis_client.set(request_conversation_id_and_session_id, json.dumps(new_session_info))
        dify_conversation_id_and_session_id = new_session_info
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
    response = {"state": str, "code": int, "message": str, "product": list, "faq_photos": list, "tags": list, "role": }
    {
   "code":200,
   "role":"bot",
   "tags":[],
   "state":"done",
   "message":[
      {
         "content":"Chào Bạn! Shop có ba loại hoa đang còn hàng để Bạn lựa chọn:\n\n1. Hoa len - Giá: 100.000 VNĐ\n",
         "products":[
            {
               "product_id":"41144568",
               "product_name":"Hoa len",
               "send_product":false,
               "product_photos":[
                  "https://bizweb.dktcdn.net/100/553/514/products/images.jpg?v=1740386609000"
               ]
            }
         ]
      }
   ],
   "faq_photos":[]
}
    '''
    
    #! if bot response contains "chuyển cho nhân viên" -> role is staff
    role = "bot"
    if ("chuyển cho nhân viên" in bot_response["answer"]):
        role = "staff"
    response = {"code": 200,"role": role,"state": "done", "messages": [{"content": bot_response["answer"], "products": []}], "faq_photos": [], "tags": []}
    return response


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
    

