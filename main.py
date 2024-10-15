import argparse
from utility import review_code
from db_utils import insert_review_result, insert_into_knowledge_base

def main():
    parser = argparse.ArgumentParser(description='Code Reviewer')
    parser.add_argument('--repo-path', required=True, help='Path to the local repository')
    parser.add_argument('--extra-files', nargs='*', help='Additional files to review')
    args = parser.parse_args()

    review_results = review_code(args.repo_path, args.extra_files)
    for result in review_results:
        raw_text = result["code"]
        review_id, snippet_id = insert_review_result(result)
        insert_into_knowledge_base(review_id, snippet_id, raw_text)

if __name__ == '__main__':
    main()
