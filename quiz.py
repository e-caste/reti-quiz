from sys import stderr
from random import choice
from math import ceil
from time import perf_counter


def human_readable_time(secs: int) -> str:
    hours = int(secs / 3600)
    secs -= hours * 3600
    minutes = int(secs / 60)
    secs -= minutes * 60
    seconds = int(secs)
    return str(hours) + "h " + str(minutes).zfill(2) + "m " + str(seconds).zfill(2) + "s"


def download_latest_google_doc():
    file_id = "1wSpYcLHNeTCCatJaCriWi6h8m_pihWl3hAVESZ2JgEU"  # on Google Docs
    dl_link = f"https://docs.google.com/document/d/{file_id}/export?format=txt"
    file_name = "Raccolta quiz.txt"
    try:
        import requests
    except ImportError:
        print("The requests module is not installed, thus this script can't download the latest version of the Google "
              "Docs file. Please install it with:\npip3 install requests", file=stderr)
        exit(42)
    response = requests.get(dl_link)
    with open(file_name, 'w') as f:
        f.write(response.content.decode('utf-8'))
    print("The latest version of " + file_name + " has been downloaded.")


def get_number_of_questions() -> int:
    n_questions = 0
    try:
        with open("Raccolta quiz.txt", 'r') as f:
            for line in f.readlines():
                if "Esercizio" in line:
                    n_questions = max(int(line.split()[1].split(".")[0]), n_questions)
        return n_questions

    except FileNotFoundError:
        print("File 'Raccolta quiz.txt' not found.\n"
              "Please download it from https://docs.google.com/document/d/1wSpYcLHNeTCCatJaCriWi6h8m_pihWl3hAVESZ2JgEU -> File -> Download -> Normal text (.txt)",
              file=stderr)
        exit(69)


def extract_questions(n_questions: int = 28) -> list:
    n_avail_questions = get_number_of_questions()
    possible_questions = [i + 1 for i in range(n_avail_questions)]
    extracted_questions = []
    for _ in range(n_questions):  # number of actual exam questions
        n = choice(possible_questions)
        extracted_questions.append(n)
        possible_questions.remove(n)
    return extracted_questions


def main():
    update_file = input("Do you want to update the .txt file with the latest version from Google Docs? "
                        "(Press Enter to skip) [y/N] ")
    if update_file.lower() == 'y':
        download_latest_google_doc()

    try:
        with open("Raccolta quiz.txt", 'r') as f:
            text = f.read()

    except FileNotFoundError:
        print("File 'Raccolta quiz.txt' not found.\n"
              "Please download it from https://docs.google.com/document/d/1wSpYcLHNeTCCatJaCriWi6h8m_pihWl3hAVESZ2JgEU -> File -> Download -> Normal text (.txt)",
              file=stderr)
        exit(69)

    n_q = 28
    change_number_of_questions = input("Do you want to change the number of questions for this quiz? (Default is 28) [y/N] ")
    if change_number_of_questions.lower() == 'y':
        while True:
            n_q = input("What number of questions would you like? Enter a number: ")
            if n_q.isdigit():
                n_avail_questions = get_number_of_questions()
                if int(n_q) < n_avail_questions:
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
        q_and_a = text.split("Esercizio " + str(q_n) + ". ")[1].split("\n\n")[0]
        q = q_and_a.split("Risposta")[0].replace("1. ", "A) ").replace("2. ", "B) ").replace("3. ", "C) ") \
                   .replace("4. ", "D) ").replace("5. ", "E) ").replace(" -- ", "")
        # correct answer
        a = q_and_a.split("Risposta: ")[1].split()[0]
        # explanation
        comment = q_and_a.split("Commento: ")[1].split("\n\n")[0]
        possible_answers = ["A)", "B)", "C)", "D)", "E)"]
        available_answers = []
        for poss_a in possible_answers:
            if poss_a in q:
                available_answers.append(poss_a[0])
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
    print(f"Quiz finished. Your result: {mark}/30 (max 28) -- correct: {correct_answers} -- wrong: {wrong_answers} -- not given: {not_given_answers}")
    print("Elapsed time for this quiz: " + human_readable_time(elapsed_time_in_seconds))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(42)
