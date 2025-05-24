import base64
import requests

owner = "TAFH-debug"
repo = "nextjs_template"

def get_dir_files(dir_path):
    """
    Get names of files and directories in a given path.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{dir_path}"
    response = requests.get(url)
    unformatted_res = response.json()

    formatted_res = []
    for item in unformatted_res:
        formatted_res.append({
            "type": item["type"],
            "name": item["name"]
        })

    return formatted_res

def get_file_content(file_path):
    """
    Get the content of a file.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    response = requests.get(url)

    content = response.json()["content"]
    return base64.b64decode(content).decode("utf-8")


