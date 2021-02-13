# Original project by e-caste, 2020

import os
from sys import stderr, platform
from random import choice
from math import ceil
from time import perf_counter
import string

# import Docker environment variables
link = os.environ["LINK"]

# TODO: fix text is decoded but with wrong characters
windows = platform.startswith("win")

file_name = "Raccolta_quiz.txt"
dl_msg = "Please download it from " + link + \
         " -> File -> Download -> Normal text (.txt)\nor\nRelaunch this script and answer 'y' to the first question"
not_found_msg = f"File '{file_name}' not found.\n" + dl_msg
empty_msg = f"It seems that {file_name} is empty.\n" + dl_msg

forbidden_question_numbers = []


def human_readable_time(secs: int) -> str:
    hours = int(secs / 3600)
    secs -= hours * 3600
    minutes = int(secs / 60)
    secs -= minutes * 60
    seconds = int(secs)
    return str(hours) + "h " + str(minutes).zfill(2) + "m " + str(seconds).zfill(2) + "s"


def download_latest_google_doc(use_logger: bool = False):
    dl_link = link + "/export?format=txt"
    try:
        import requests
    except ImportError:
        print("The requests module is not installed, thus this script can't download the latest version of the Google "
              "Docs file. Please install it with:\npip3 install requests", file=stderr)
        exit(42)
    try:
        s = ""
        response = requests.get(dl_link)
    except requests.ConnectionError:
        s = "You're not connected to the Internet. Please try again later. Skipping download..."
        print(s, file=stderr)
        return
    except requests.HTTPError:
        s = f"HTTP error when downloading {file_name}"
        print(s)

    if not s:
        with open(file_name, 'w') as f:
            if windows:
                f.write(response.content.decode('cp1252', errors='ignore'))
            else:
                f.write(response.content.decode('utf-8'))
            s = f"The latest version of {file_name} has been downloaded."
    if use_logger:
        return s
    else:
        print(s)


def get_number_of_questions() -> int:
    n_questions = 0
    try:
        with open(file_name, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(not_found_msg, file=stderr)
        exit(69)
    if set(text) <= set(string.whitespace):
        print(empty_msg, file=stderr)
        exit(2)
    for line in text.splitlines():
        if "Esercizio" in line:
            n_questions = max(int(line.split()[1].split(".")[0]), n_questions)
    return n_questions - len(forbidden_question_numbers)


def extract_questions(n_questions: int = 28) -> list:
    n_avail_questions = get_number_of_questions()
    possible_questions = [i for i in range(1, n_avail_questions + len(forbidden_question_numbers) + 1)
                          if i not in forbidden_question_numbers]
    extracted_questions = []
    for _ in range(n_questions):  # number of actual exam questions
        n = choice(possible_questions)
        extracted_questions.append(n)
        possible_questions.remove(n)
    return extracted_questions


def get_q_n_a(text: str, q_n: int) -> tuple:
    def remove_empty_lines(text_block: str) -> str:
        return "\n".join([line for line in text_block.splitlines() if line.strip()])
    tmp = text.split("Esercizio " + str(q_n) + ". ")[1]
    question, answer, comment = ("", "", "")
    # form question
    for line in tmp.splitlines():
        if "Risposta" not in line and "Esercizio " + str(q_n + 1) not in line and "Orale" not in line:
            question += line + "\n"
        else:
            break
    question = question.replace("1. ", " A) ").replace("2. ", " B) ").replace("3. ", " C) ") \
        .replace("4. ", " D) ").replace("5. ", " E) ").replace(" -- ", "")
    # form answer
    # ignoring the first n lines, where n is the number of lines of the question
    for line in tmp.splitlines()[len(question.splitlines()):]:
        if "Commento" not in line and "Esercizio " + str(q_n + 1) not in line and "Orale" not in line:
            answer += line + "\n"
        else:
            break
    # form comment
    # ignoring the first n lines, where n is the number of lines of the question + the number of lines of the answer
    for line in tmp.splitlines()[len(question.splitlines()) + len(answer.splitlines()):]:
        if line and "Esercizio " + str(q_n + 1) not in line and "Orale" not in line:
            comment += line + "\n"
        else:
            break
    question = remove_empty_lines(question)
    answer = remove_empty_lines(answer)
    comment = remove_empty_lines(comment)
    # make answer one letter only
    answer = answer.replace("Risposta: ", "").replace("\n", "")
    if " " in answer:
        answer = answer.split()[0]
    # clean comment
    comment = comment.replace("Commento: ", "")
    return question, answer, comment


def get_available_answers(q: str) -> list:
    possible_answers = ["A)", "B)", "C)", "D)", "E)"]
    available_answers = []
    for poss_a in possible_answers:
        for line in q.splitlines():
            if line != "":
                if poss_a == line.split()[0] or line.startswith(poss_a):
                    available_answers.append(poss_a[0])
    return available_answers


def set_forbidden_questions():
    with open(file_name, 'r') as f:
        text = f.read()
    n_q = get_number_of_questions()
    for i in range(n_q):
        try:
            quiz = text.split("Esercizio " + str(i + 1) + ". ")[1].split("\n\n")[0]
            if "Risposta" not in quiz:
                forbidden_question_numbers.append(i + 1)
        except IndexError:
            forbidden_question_numbers.append(i + 1)
            continue


# Google Docs comments are represented as [a], [b]...
# and are referenced at the end of the document like: [a] this is the first comment...
def clean_comments_from_text(text: str) -> str:
    if "[a]" not in text:
        return text
    end = "[a]" + text.split("[a]")[-1]
    comment_refs = [ref.split("]")[0] for ref in end.split("[") if ref.split("]")[0] != ""]
    for ref in comment_refs:
        text = text.replace("[" + ref + "]", "\n")
    return text


def main():
    update_file = input("Do you want to update the .txt file with the latest version from Google Docs? "
                        "(Press Enter to skip) [y/N] ")
    if update_file.lower() == 'y':
        download_latest_google_doc()
    try:
        if windows:
            with open(file_name, 'r', encoding='cp1252') as f:
                text = f.read()
        else:
            with open(file_name, 'r') as f:
                text = f.read()
    except FileNotFoundError:
        print(not_found_msg, file=stderr)
        exit(69)

    text = clean_comments_from_text(text)
    set_forbidden_questions()

    n_q = 28
    change_number_of_questions = input("Do you want to change the number of questions for this quiz? "
                                       "(Default is 28) [y/N] ")
    if change_number_of_questions.lower() == 'y':
        n_avail_questions = get_number_of_questions()
        while True:
            n_q = input("What number of questions would you like? Enter a number: ")
            if n_q.isdigit():
                if int(n_q) <= n_avail_questions:
                    n_q = int(n_q)
                    extracted_questions = extract_questions(n_q)
                    break
                else:
                    print(f"Please enter a lower number than {n_avail_questions}.", file=stderr)
            else:
                print("Input not recognized. Please try again.", file=stderr)
    else:
        extracted_questions = extract_questions()

    print("You can press 'S' or 's' instead of giving an answer to skip a question.\n")
    correct_answers = 0
    wrong_answers = 0
    start_time = perf_counter()
    for i, q_n in enumerate(extracted_questions):
        q, a, comment = get_q_n_a(text, q_n)
        available_answers = get_available_answers(q)
        avail_ans_str = str(available_answers)[1:-1].replace("'", "")
        # user's answer
        print(f"Quiz {q_n} -- {i + 1}/{len(extracted_questions)}")
        ans = input(q + "\nPossible answers: " + avail_ans_str + " (not case sensitive)\nPlease enter your answer: ")
        while True:
            if ans.upper() in available_answers + ["S"]:
                if ans.upper() == "S":
                    print("Skipping question... The correct answer is " + a + ".")
                elif ans.upper() == a:
                    print("Correct!")
                    correct_answers += 1
                else:
                    print("Wrong. -- The correct answer is " + a + ".")
                    wrong_answers += 1
                print(comment + "\n")
                break
            else:
                ans = input("Answer not recognized. Please enter it again: ")

    elapsed_time_in_seconds = int(perf_counter() - start_time)
    not_given_answers = n_q - correct_answers - wrong_answers
    mark = ceil((correct_answers - wrong_answers * .5) / n_q * 28)
    print(f"Quiz finished. Your result: {mark}/30 (max 28) -- correct: {correct_answers} -- wrong: {wrong_answers} "
          f"-- not given: {not_given_answers}")
    print("Elapsed time for this quiz: " + human_readable_time(elapsed_time_in_seconds))


def test(text: str):
    set_forbidden_questions()
    for i in range(1, get_number_of_questions() + 1):
        if i not in forbidden_question_numbers:
            print(i)
            for t in get_q_n_a(text, i):
                print(t)
            print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit(1)
