# coding: utf-8


import requests
import os
import json
import socket
# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='AAAAAAAAAAAAAAAAAAAAADFvmQEAAAAATJmGj%2BjxxR4u86%2FCdP40tp50RbA%3DV0XFEUwru2tQMD76iEVNd4ued1f54PvawXE1FOSqbQCMvqjVKv'
bearer_token = os.environ.get("BEARER_TOKEN")

#twitter API사용을 위한 Bearer_token을 통한 AUTH 인증
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r

# twitter 스트림에 포함된 규칙 목록을 반환
def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()

# 사용자 정의 규칙 사용을 위해 스트림에서 기존 규칙 삭제
def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))

# 초기화된 규칙에 원하는 규칙 내용 
def set_rules(delete):
    # value 값 설정을 통해 원하는 카테고리의 데이터만 수집가능
    sample_rules = [{'value':'Kpop'},]
    
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


# 스트림 조회 결과 불러오기
def get_stream(set, client_socket):
    response = requests.get("https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,)
    print(response.status_code)
    if response.status_code != 200:
            raise Exception("Cannot get stream (HTTP {}): {}".format(response.status_code, response.text ))
    print("|-------- get_stream --------|")
    for response_line in response.iter_lines():
        if response_line:
            try:
                json_response = json.loads(response_line)
                print("\n\nOrigianl : " , json.dumps(json_response, indent=4, sort_keys=True))
                msg = json.loads(response_line)
                print("\n\nSend :" , msg['data']['text'].encode('utf-8') )
                client_socket.send( msg['data']['text'].encode('utf-8') )
            except BaseException as e :
                print("Error on get_stream() : %s" %str(e))


def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    get_stream(set)


# twitter API 연결 및 소켓 데이터 전송
def sendData(client_socket):
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    get_stream(set, client_socket)


#소켓 연결 후 twitter API로 데이터 조회에 소켓에 데이터 전송
if __name__ == "__main__":
    
  
    # 소켓 오브젝트 생성
    s = socket.socket()         
    host = "127.0.0.1"     
    port = 5555    
    # 소켓에 ip주소와 포트 연결
    s.bind((host, port))        

    print("Listening on port: %s" % str(port))
    # 클라이언트 소켓 연결 대기 
    s.listen(5)    
    # 클라이언트 연결 승인
    c, addr = s.accept()       

    print("Received request from: " + str(addr))

    sendData(c)







