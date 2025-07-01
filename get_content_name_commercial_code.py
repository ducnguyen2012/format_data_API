def get_content_name_commercial_code(json_data):
    '''
    Extract request json from social to get field content of buyer, ten_KH, ma_QC

    input: json_data from bot response
    output: content: str, ten_KH: str, ma_qc: str
    '''

    n = len(json_data)
    '''
    This while will let pointer get into buyer message (and content of message is not empty) to return 
    '''
    idx = 0
    content = ""
    ten_KH = ""
    ma_qc = ""
    for i in range(n):
        idx = i
        if (json_data["message"][idx]["role"] != "buyer" or (json_data["message"][idx]["role"] == "buyer" and json_data["message"][idx]["content"] == "")):
            continue 
        else:
            content = json_data["message"][idx]["content"]
            ten_KH = json_data["conversation_name"]
            ma_qc = json_data["ads_ids"]
            return content, ten_KH, ma_qc
    
        
    