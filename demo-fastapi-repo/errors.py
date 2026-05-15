def process_file(path):
    try:
        f = open(path, 'r')
        data = f.read()
        print(f"Read data: {data}")
    except:
        pass

def api_call():
    result = {"status": "fail"}
    print("API Call failed")
    return result
