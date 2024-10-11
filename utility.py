import os
import subprocess
from colorama import Fore, Style, init
from openai import OpenAI

init(autoreset=True)

def call_openai_for_review(file_content):
    """
    Call OpenAI API to review the given file content.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = (
        "You are a software engineer expert.\n"
        "Given an input, create a comment on the changes if needed.\n"
        "If need to provide an example give only one.\n"
        "Remember NOT include backticks ```code ``` before and after the diff.\n"
        "Print the diff of the file too. Some files have no diff, so print only the line with the comment.\n"
        "Place your comments after the corresponding line and if there are many place it one after the other.\n"
        "Your code review should look similar to this if the first line starts with 'diff --git':\n"
        """diff --git a/FILENAME b/FILENAME
           index some hashes and the permissions
           Some lines of code from the diff.
            
           -Changed lines starts with '-' and means it is the original line.
           Comment#1: This is the first comment
           Comment#2: This is the second comment if needed.
           +Changed lines starts with '+' and means it is different from the original line.
           Comment#3: This is the third comment if needed.
            
           Some other lines of code from the diff"""
        "Otherwise your code review should look similar to this:\n"
        """some line of code that should be changed
           Comment#1: This is the first comment
           Comment#2: This is the second comment if needed.
        """
        "Remember NOT include backticks ```code ``` before and after the file content.\n"
        "The comments have to start with 'Comment#' and the number of the comment.\n"
        "Do not repeat comments in the suggestion section.\n"
        "The suggestion should start with 'Suggestion#' and this is where you should put the general suggestion about the code.\n"
        f"Review the following code and provide comments on improvements:\n\n{file_content}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
            {"role": "system", "content": prompt},                                                                                                                                               
        ]
    )
    return response.choices[0].message.content

def review_code(repo_path, extra_files=None):
    """
    Review code in the specified repository path and any extra files.
    """
    files_to_review = []
    color_map = {
        '+': Fore.GREEN,
        '-': Fore.RED,
        'Comment#': Fore.YELLOW,
        'Suggestion#': Fore.LIGHTCYAN_EX
    }

    result = subprocess.run(
        ['git', '-C', repo_path, 'diff', '--name-only', 'HEAD'],
        stdout=subprocess.PIPE,
        text=True
    )
    modified_files = result.stdout.splitlines()

    for file in modified_files:
        if file.endswith(('.py', '.js', '.coffee', '.html', '.sh')):
            diff_result = subprocess.run(
                ['git', '-C', repo_path, 'diff', 'HEAD', '--', file],
                stdout=subprocess.PIPE,
                text=True
            )
            files_to_review.append((file, diff_result.stdout))

    for file_path, file_diff in files_to_review:
        print(f"Reviewing changes in {file_path}:")

        review_comments = call_openai_for_review(file_diff).splitlines()

        for line in review_comments:
            color = Fore.LIGHTBLACK_EX
            for prefix, fore_color in color_map.items():
                if line.startswith(prefix) and not line.startswith(prefix * 3):
                    color = fore_color
                    break

            print(color + ' ' + line)

    if extra_files:
        for file in extra_files:
            file_path = os.path.join(repo_path, file)
            with open(file_path, 'r') as f:
                file_content = f.read()
            print(f"Reviewing extra file {file_path}:")
            review_comments = call_openai_for_review(file_content).splitlines()

            for line in review_comments:
                color = Fore.LIGHTBLACK_EX
                line = line.lstrip()
                for prefix, fore_color in color_map.items():
                    if line.startswith(prefix):
                        color = fore_color
                        break

                print(color + ' ' + line)
