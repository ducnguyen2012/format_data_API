import json
import os
import psycopg2
from dotenv import load_dotenv

#! ======================================================= load env keys ========================================================

load_dotenv()

DB_NAME=os.getenv("DB_NAME")
USER_NAME=os.getenv("USER_NAME")
HOST_IP=os.getenv("HOST_IP")
PASSWORD=os.getenv("PASSWORD")
PORT=os.getenv("PORT")

#! ==============================================================================================================================


def push_log_and_lead_information_to_DB(socialRequest: dict, final_response: dict):
    '''
    This function will save all information from API, social information, dify information

    input:
        - socialRequest: json
        - Dify response: (which is json_data_add_converstaionID_and_sessionID_to_bot): json
        - responseStatus: json
    return: 
        push all data to postgresSQL
    '''
    #! ============================= setup login database ===============================
    #print(f"This is my database: {DB_NAME} and user: {USER_NAME} and host_IP: {HOST_IP} and password: {PASSWORD} and port: {PORT}")
    conn = psycopg2.connect(
        database=DB_NAME,
        user=USER_NAME,
        host=HOST_IP,
        password=PASSWORD,
        port=PORT
    )

    myCursor = conn.cursor()

    #! ==================== extract data from socialRequest =====================

    alias = socialRequest["alias"]
    store_id = socialRequest["store_id"]
    page_id = socialRequest["page_id"]
    conversation_id = socialRequest["conversation_id"]
    session_id = socialRequest["session_id"]
    ads_ids = socialRequest["ads_ids"]
    conversation_name = socialRequest["conversation_name"]
    status_code = final_response["code"]


        
        
    #! ==================== extract data from botMessage ======================
    


    #! becasue social gonna past a list of message, so i need to use for to get all message, each with a line in database. 
    #! note: socialRequest is a list!
    request_input = json.dumps(socialRequest, ensure_ascii=False)
    msg = socialRequest["message"][0]
    message_id = msg.get("id")
    message_role = msg.get("role")
    message_content = msg.get("content")
    message_type = msg.get("message_type")
    message_channel_sender_id = msg.get("channel_sender_id")
    message_is_send_by_page = msg.get("is_send_by_page")
    message_channel_created_on = msg.get("channel_created_on")
    message_post_id = msg.get("post_id")
    message_post_type = msg.get("post_type")
    message_post_image_urls = msg.get("post_image_urls")
    
    '''
    Because bot always responses to the first message appear in social request
    '''
    
    bot_task_id = final_response.get("task_id")
    bot_message_id = final_response.get("message_id")
    bot_role = final_response.get("role")
    bot_status_code = final_response.get("code")
    bot_metadata_latency = final_response["metadata"]["usage"]["latency"]
    bot_metadata_retriever_resources_content = final_response.get("answer")
    bot_conversation_id = final_response.get("conversation_id")
    bot_session_id = final_response.get("session_id")
    
    
    #! ====================== extract status_code from response =======================
    '''
    We only use these column when we can access to 3 columns 

    bot_metadata_retriever_resources_content,
    bot_metadata_retriever_resources_document_name,
    bot_metadata_retriever_resources_score,
    '''
    #! ==================== push data into database =========================== 
    insertData = """
    INSERT INTO leadChatbotDatabase (
        status_code,
        message_is_send_by_page,
        conversation_id,
        session_id,
        ads_ids,
        conversation_name,
        message_channel_sender_id,
        message_channel_created_on,
        message_id,
        message_role,
        message_content,
        bot_metadata_retriever_resources_content,
        message_type,
        alias,
        store_id,
        page_id,
        message_post_id,
        message_post_type,
        message_post_image_urls,
        bot_task_id,
        bot_metadata_latency,
        bot_conversation_id,
        bot_session_id,
        request_input,
        bot_message_id,
        bot_role,
        bot_status_code
    ) VALUES (%s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s)
    """

    
    
    values = (
        status_code,
        message_is_send_by_page,
        conversation_id,
        session_id,
        ads_ids,
        conversation_name,
        message_channel_sender_id,
        message_channel_created_on,
        message_id,
        message_role,
        message_content,
        bot_metadata_retriever_resources_content,
        message_type,
        alias,
        store_id,
        page_id,
        message_post_id,
        message_post_type,
        message_post_image_urls,
        bot_task_id,
        bot_metadata_latency,
        bot_conversation_id,
        bot_session_id,
        request_input,
        bot_message_id,
        bot_role,
        bot_status_code
    )
    try:
        myCursor.execute(insertData, values)
        conn.commit()  #! make change to the database persistent
        print(f"execute to database done!")
    except Exception as e:
        '''
        If there is an error we also close our connection!
        '''
        print(f"AN error is occur when insert into DB: {e}")
        myCursor.close()
        conn.close()    
    myCursor.close()
    conn.close()