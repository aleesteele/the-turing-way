import os
import re
import argparse
import requests

HERE = os.getcwd()
ABSOLUTE_HERE = os.path.dirname(HERE)
BAD_PHRASE = "lorem ipsum"


def parse_args():
    """Construct the command line interface for the script"""
    DESCRIPTION = "Script to check for occurences of 'Lorem Ipsum' in Markdown files"
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        "--pull-request",
        type=str,
        default=None,
        help="If the script is be run on files changed by a pull request, parse the PR number",
    )

    return parser.parse_args()


def remove_comments(text_string):
    """Function to omit  html comment identifiers in a text string using
	regular expression matches

	Arguments:
		text_string {string} -- The text to be matched

	Returns:
		{string} -- The input text string with html comments removed
	"""
    p = re.sub("(?s)<!--(.*?)-->", "", text_string)
    return p


def get_files_from_pr(pr_num):
    """Return a list of changed files from a GitHub Pull Request

    Arguments:
        pr_num {str} -- Pull Request number to get modified files from

    Returns:
        {list} -- List of modified filenames
    """
    files = []
    pr_url = f"https://api.github.com/repos/alan-turing-institute/the-turing-way/pulls/{pr_num}/files"
    resp = requests.get(pr_url)

    for item in resp.json():
        files.append(item["filename"])

    return files


def filter_files(pr_num, start_phrase="book/content"):
    """Filter modified files from a Pull Request by a start phrase

    Arguments:
        pr_num {str} -- Number of the Pull Request to get modified files from

    Keyword Arguments:
        start_phrase {str} -- Start phrase to filter changed files by
                              (default: {"book/content"})

    Returns:
        {list} -- List of filenames that begin with the desired start phrase
    """
    files = get_files_from_pr(pr_num)
    filtered_files = []

    for filename in files:
        if filename.startswith(start_phrase):
            filtered_files.append(filename)

    return filtered_files


def check_changed_files(pr_num, bad_phrase=BAD_PHRASE):
    """Check the files in a Pull Request for an undesirable phrase

    Arguments:
        pr_num {str} -- Number of the Pull Request with modified files

    Keyword Arguments:
        bad_phrase {str} -- The undesirable phrase to check for (default: {BAD_PHRASE})

    Returns:
        {list} -- List of filenames that contain the undesirable phrase
    """
    filenames = filter_files(pr_num)
    failed = []

    for filename in filenames:
        f = open(
            os.path.join(ABSOLUTE_HERE, filename), encoding="utf8", errors="ignore"
        )
        text = f.read()
        text = remove_comments(text)
        if bad_phrase in text.lower():
            failed.append(filename.name)

    return failed


def check_all_files(
    bad_phrase=BAD_PHRASE,
    directory_to_check=os.path.join(ABSOLUTE_HERE, "book", "content"),
):
    """Check all files in a given directory for an undesirable phrase

    Keyword Arguments:
        bad_phrase {str} -- Phrase to check and warn for (default: {"lorem ipsum"})
        directory_to_check {str} -- Parent directory of files to be checked (default: {os.path.join(ABSOLUTE_HERE, "book", "content")})

    Returns:
        {list} -- List of filenames that contain the undesirable phrase
    """
    failed = []

    for root_dir, _, filenames in os.walk(directory_to_check):
        for filename in filenames:
            f = open(os.path.join(root_dir, filename), encoding="utf8", errors="ignore")
            text = f.read()
            text = remove_comments(text)
            if bad_phrase in text.lower():
                failed.append(filename.name)

    return failed


def main():
    """Main function"""
    args = parse_args()

    if args.pull_request is not None:
        failed = check_changed_files(args.pull_request)
    else:
        failed = check_all_files()

    if len(failed) != 0:
        error_message = '"Lorem ipsum"s found in the following files:\n' + "\n".join(
            failed
        )
        raise Exception(error_message)


if __name__ == "__main__":
    main()
