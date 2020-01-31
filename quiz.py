from sys import stderr
from random import choice


def extract_questions() -> list:
    n_questions = 0
    try:
        with open("Raccolta quiz.txt", 'r') as f:
            for line in f.readlines():
                if "Esercizio" in line:
                    n_questions = max(int(line.split()[1].split(".")[0]), n_questions)
        possible_questions = [i+1 for i in range(n_questions)]
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
            for q_n in extracted_questions:
                q = text.split("Esercizio " + str(q_n) + ".")[1].split("Risposta")[0] + "\nPlease enter your answer: "
                ans = input(q)

    except FileNotFoundError:
        print("File 'Raccolta quiz.txt' not found.\n"
              "Please download it from https://docs.google.com/document/d/1wSpYcLHNeTCCatJaCriWi6h8m_pihWl3hAVESZ2JgEU -> File -> Download -> Normal text (.txt)",
              file=stderr)

if __name__ == '__main__':
    main()
