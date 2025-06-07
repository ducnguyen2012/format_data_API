def getContent_and_tenKH(json_data):
    '''
    Extract request json to get field content of buyer
    '''
    idx = -1
    while json_data["message"][idx]["role"] != "buyer":
        '''
        This condition will ensure take last message from buyer
        '''
        idx -= 1
    content = json_data["message"][idx]["content"]
    print(f"this is json_data: {json_data}")
    ten_KH = json_data["message"][idx]["ten_KH"]
    return content, ten_KH