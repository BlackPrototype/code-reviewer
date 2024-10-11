import argparse
from utility import review_code

def main():
    parser = argparse.ArgumentParser(description='Code Reviewer')
    parser.add_argument('--repo-path', required=True, help='Path to the local repository')
    parser.add_argument('--extra-files', nargs='*', help='Additional files to review')
    args = parser.parse_args()

    review_code(args.repo_path, args.extra_files)

if __name__ == '__main__':
    main()
