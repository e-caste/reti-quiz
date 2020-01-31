from sys import stderr
from random import choice


def extract_questions() -> list:
    n_questions = 0
    try:
        with open("Raccolta quiz.txt", 'r') as f:
            for line in f.readlines():
                if "Esercizio" in line:
                    n_questions = max(int(line.split()[1].split(".")[0]), n_questions)
        possible_questions = [i + 1 for i in range(n_questions)]
        extracted_questions = []
        for _ in range(28):  # number of actual exam questions
            n = choice(possible_questions)
            extracted_questions.append(n)
            possible_questions.remove(n)
        return extracted_questions

    except FileNotFoundError:
        print("File 'Raccolta quiz.txt' not found.\n"
              "Please download it from https://docs.google.com/document/d/1wSpYcLHNeTCCatJaCriWi6h8m_pihWl3hAVESZ2JgEU -> File -> Download -> Normal text (.txt)",
              file=stderr)


def main():
    extracted_questions = extract_questions()
    try:
        with open("Raccolta quiz.txt", 'r') as f:
            text = f.read()

    except FileNotFoundError:
        print("File 'Raccolta quiz.txt' not found.\n"
              "Please download it from https://docs.google.com/document/d/1wSpYcLHNeTCCatJaCriWi6h8m_pihWl3hAVESZ2JgEU -> File -> Download -> Normal text (.txt)",
              file=stderr)

    for q_n in extracted_questions:
        q_and_a = text.split("Esercizio " + str(q_n) + ". ")[1].split("\n\n")[0]
        q = q_and_a.split("Risposta")[0].replace("1.", "A)").replace("2.", "B)").replace("3.", "C)") \
                   .replace("4.", "D)").replace("5.", "E)")
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
        print("Quiz " + str(q_n))
        ans = input(q + "\nPossible answers: " + avail_ans_str + " (not case sensitive)\nPlease enter your answer: ")
        while True:
            if ans.upper() in available_answers:
                if ans.upper() == a:
                    print("Correct!")
                else:
                    print("Wrong.")
                print(comment + "\n")
                break
            else:
                ans = input("Answer not recognized. Please enter it again: ")

if __name__ == '__main__':
    main()
