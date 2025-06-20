import os
import httpx
import config

API_KEY = os.getenv("DIFY_LEAD_CHAT_API_KEY")
URL = os.getenv("DIFY_CHAT_URL")
async def call_dify(user_message: str, conversation_id_and_session_id: list, ten_KH: str, ma_qc: list):
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
    
    conversation_id = conversation_id_and_session_id[0]
    
    session_id = conversation_id_and_session_id[1]
    #print(f"this is dify_conversation_id_and_session_id: {conversation_id_and_session_id}")
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        "Content-Type": "application/json"
    }

    data_raw = {
        "inputs": {"ten_kh": ten_KH, "ma_qc": str(ma_qc),"session_id": session_id},
        "query": user_message,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": ten_KH
    }
    #
    # print(data_raw, url, headers)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url=url, headers=headers, json=data_raw)
            response.raise_for_status()
            response_dict = response.json()
            conversation_id = response_dict.get("conversation_id", conversation_id)
            session_id = response_dict.get("session_id", session_id)
            return response_dict, conversation_id, session_id
    except httpx.HTTPStatusError as exc:
        response = {"answer": f"HTTP Status Error: {exc.response.status_code} - {exc.response.text}"}
        return response, "",""
    except httpx.RequestError as messageErr:
        response = {"answer": f"Request Error: {messageErr}"}
        return response, "",""
    except httpx.TimeoutException as timeout:
        response = {"answer": f"Timeout Error: {timeout}"}
        return response, "",""
    except httpx.ConnectError as connect_err:
        response = {"answer": f"Connect Error: {connect_err}"}
        return response, "",""
    except httpx.NetworkError as network_err:
        response = {"answer": f"Network Error: {network_err}"}
        return response, "",""
    except httpx.ProtocolError as protocol_err:
        response = {"answer": f"Protocol Error: {protocol_err}"}
        return response, "",""
    except httpx.TransportError as transport_err:
        response = {"answer": f"Transport Error: {transport_err}"}
        return response, "",""
    except httpx.HTTPError as http_err:
        response = {"answer": f"Generic HTTP Error: {http_err}"}
        return response, "",""
    except Exception as e:
        response = {"answer": f"Unexpected Error: {e}"}
        return response, "",""