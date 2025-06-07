import asyncio
from dotenv import load_dotenv
import os
import httpx

load_dotenv()


API_KEY = os.getenv("API_KEY")
URL = os.getenv("URL")
async def call_dify(user_message: str, conversation_id: str, ten_KH: str):
    url = URL

    headers = {
        'Authorization': API_KEY,
        "Content-Type": "application/json"
    }

    data_raw = {
        "inputs": {},
        "query": user_message,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": ten_KH
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url=url, headers=headers, json=data_raw,)
            print(f"This is my response: {response}")
            response.raise_for_status()  # Raise exception for HTTP 4xx/5xx
            response_dict = response.json()
            conversation_id = response_dict.get("conversation_id", conversation_id)
            return response_dict, conversation_id
    except httpx.HTTPStatusError as exc:
        response = {"answer": f"HTTP Status Exception: {exc.response.status_code} - {exc.response.text}"}
        return response, ""
    except httpx.RequestError as messageErr:
        response = {"answer": f"Request Exception: {messageErr}"}
        return response, ""
    except httpx.TimeoutException as timeout:
        response = {"answer": f"Timeout Exception: {timeout}"}
        return response, ""
    except httpx.ConnectError as connect_err:
        response = {"answer": f"Connect Error: {connect_err}"}
        return response, ""
    except httpx.NetworkError as network_err:
        response = {"answer": f"Network Error: {network_err}"}
        return response, ""
    except httpx.ProtocolError as protocol_err:
        response = {"answer": f"Protocol Error: {protocol_err}"}
        return response, ""
    except httpx.TransportError as transport_err:
        response = {"answer": f"Transport Exception: {transport_err}"}
        return response, ""
    except httpx.HTTPError as http_err:
        response = {"answer": f"Generic HTTP Error: {http_err}"}
        return response, ""
    except Exception as e:
        response = {"answer": f"Unexpected error: {e}"}
        return response, ""