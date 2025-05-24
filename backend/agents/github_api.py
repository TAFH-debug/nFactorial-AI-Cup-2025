import base64
import requests

def get_owner_and_repo(github_repo):
    return github_repo.split("/")[-2], github_repo.split("/")[-1]

def get_repo_read_functions(github_repo):
    owner, repo = get_owner_and_repo(github_repo)

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
    
    return get_dir_files, get_file_content

