def get_content_ten_maqc(json_data):
    '''
    Extract request json from social to get field content of buyer, ten_KH, ma_QC

    input: json_data from bot response
    output: content: str, ten_KH: str, ma_qc: str
    '''

    idx = 0
    
    '''
    This while will let pointer get into buyer message (and content of message is not empty) to return 
    '''
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