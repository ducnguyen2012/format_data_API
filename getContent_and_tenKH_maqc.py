def getContent_and_tenKH_maqc(json_data):
    '''
    Extract request json to get field content of buyer

    input: json_data from bot response
    output: content: str, ten_KH: str, ma_qc: str
    '''
    idx = 0
    
    while json_data["message"][idx]["role"] != "buyer":
        '''
        This condition will ensure take last message from buyer
        '''
        
        idx += 1
    while json_data["message"][idx]["role"] == "buyer" and json_data["message"][idx]["content"] == "":
        idx += 1
    content = json_data["message"][idx]["content"]
    ten_KH = json_data["conversation_name"]
    ma_qc = json_data["ads_ids"]
    return content, ten_KH, ma_qc