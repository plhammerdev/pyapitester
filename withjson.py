import json
import os
from requests import session
from pprint import pprint

cur_dir = os.path.dirname(os.path.realpath(__file__))

def check_vals(resp, name, actual, expected, extent="full"):
    #import pdb; pdb.set_trace()
    assert extent in ("full", "partial")
    if extent == "partial":
        if expected not in actual:
            print(f"Mismatch on {name} for URL: {resp.url}, Method: {resp.request.method}, Expected: {expected}, Actual: {actual} [PARTIAL MATCH CHECK]")
    else:
        if actual != expected:
            print(f"Mismatch on {name} for URL: {resp.url}, Method: {resp.request.method}, Expected: {expected}, Actual: {actual}")


def verify_resp(resp, expected, responses_path):
    check_vals(resp, "Status Code", resp.status_code, expected["resp_code"])
    check_vals(resp, "Content Type", resp.headers["content-type"], expected["resp_content_type"])

    resp_body_file_path = expected.get("resp_body_file", None)
    if resp_body_file_path is not None:
        if os.path.isfile(resp_body_file_path):
            pass
        elif os.path.isfile(os.path.join(responses_path, resp_body_file_path)):
            resp_body_file_path = os.path.join(responses_path, resp_body_file_path)
        else:
            raise FileNotFoundError(f"File not found: {resp_body_file_path}")
        
        with open(resp_body_file_path, "rb") as f:
            expected_body = f.read()
            check_extent = expected.get("resp_compare_extent", "full").lower()
            check_vals(resp, "Body", resp.content, expected_body, extent=check_extent)

        

    

def make_http_call(ses, url, method, headers=None, body=None):
    if method == "get":
        resp = ses.get(url)
    elif method == "post":
        resp = ses.post(url)
    else:
        raise NotImplementedError(f"Method of {method} is not supported")
    return resp


def run_group(session, file_path:str, responses_path:str) -> None:
    with open(file_path) as f:
        test_group = json.loads(f.read())
        group_name = test_group["group_name"]
        print(f"Running for group: {group_name}")
        for call in test_group['calls']:
            name = call["name"]
            print(f"Checking {name}")

            url = call["req_url"]
            method = call["req_method"].lower()

            # Build URL
            base_url = test_group["base_url"]
            if base_url is not None:
                url = base_url + url
            
            headers = call["req_headers"]
            
            resp = make_http_call(session, url, method, headers)
            verify_resp(resp, call, responses_path)



if __name__ == "__main__":
    # Setup Requests session
    ses = session()

    # Discover groups
    test_groups = []
    endpoints_path = os.path.join(cur_dir, "endpoints")
    responses_path = os.path.join(cur_dir, "responses")
    file_paths = [os.path.join(endpoints_path, filename) for filename in os.listdir(endpoints_path) if filename.endswith(".json")]
    print(f"Discovered test groups in files: {','.join(file_paths)}")
    
    for file_path in file_paths:
        run_group(ses, file_path, responses_path)








    
# TODO:
# Add event loop
# Add test, add typing
# Add praise