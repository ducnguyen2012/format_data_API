def getContent_and_tenKH_maqc(json_data):
    '''
    Extract request json to get field content of buyer
    '''
    idx = -1
    print(f"this is json_data: {json_data}")
    
    while json_data["message"][idx]["role"] != "buyer":
        '''
        This condition will ensure take last message from buyer
        '''
        
        idx -= 1
    while json_data["message"][idx]["role"] == "buyer" and json_data["message"][idx]["content"] == "":
        idx -= 1
    content = json_data["message"][idx]["content"]
    
    ten_KH = json_data["ten_kh"]
    ma_qc = json_data["ma_qc"]
    return content, ten_KH, ma_qc