# reti-quiz

### How to run

Simply download this repository by clicking the "Download Repository" button to the top right of this page or clone it from the command line with `git clone https://git.caste.dev/e-caste/reti-quiz.git`. If you have downloaded it as a .zip file, you need to unzip to a folder with `unzip reti-quiz.zip` (or by double-clicking the file in your system's file explorer).  
Head to the directory where you have cloned it with `cd reti-quiz`, then you can simply run it with `python3 quiz.py`.  

This project has only `requests` as an optional dependency, to automatically download the latest version of the file from Google Docs.  
It's recommended to install it in a virtual environment, but you may download it to your system-wide Python libraries with `pip3 install requests`.  

To use a virtual environment instead (cleaner but longer approach):  
- go to repo directory with `cd reti-quiz`
- make it with `python3 -m venv venv`
- activate it with `source venv/bin/activate`
- install requests with `pip install requests`
- use script: `python quiz.py`
- when finished, deactivate the virtualenv with `deactivate`


### Usage example

```
Do you want to update the .txt file with the latest version from Google Docs? (Press Enter to skip) [y/N] y
Do you want to change the number of questions for this quiz? (Default is 28) [y/N] y
What number of questions would you like? Enter a number: 3
Quiz 138
Un protocollo
   A) E’ un insieme di regole semantiche e sintattiche per consentire la comunicazione tra due entità di pari livello
   B) E’ un insieme di regole semantiche e sintattiche per consentire la comunicazione tra due entità di stesso sistema
   C) E’ un insieme di regole semantiche e sintattiche per consentire la comunicazione tra due sistemi che vengono collegati tra loro
   D) E’ un insieme di regole semantiche e sintattiche per consentire la comunicazione tra due entità di sistemi diversi

Possible answers: A, B, C, D (not case sensitive)
Please enter your answer: a
Correct!
Per definizione un’entità comunica con altre entità dello stesso livello.

Quiz 24
Che cosa si intende per il dominio di collisione (collision domain) in Ethernet?
   A) La porzione di rete entro la quale viene rilevata una stessa collisione
   B) Il numero di bit dell’intestazione dei pacchetti che possono essere danneggiati da una collisione
   C) L’insieme dei nodi che interrompono la trasmissione a causa di una collisione

Possible answers: A, B, C (not case sensitive)
Please enter your answer: b
Wrong. -- The correct answer is A
Dominio di collisione: porzione di rete in cui due trame collidono. Vedi lucidi m“Dominio di collisione”. 

Quiz 145
Quale tra le seguenti affermazioni è vera?
   A) Una topologia T1, con N nodi, C canali e distanza media M1, consente sempre di smaltire una   quantità di traffico minore di una topologia T2, con N nodi, C canali e distanza media M2>M1, solo con traffico uniformemente distribuito tra nodi.
   B) Una topologia T1, con N nodi, C canali e distanza media M1, consente sempre di smaltire una quantità di traffico minore di una topologia T2, con N nodi, C canali e distanza media M2>M1, indipendentemente dalla distribuzione di traffico.
   C) La quantità di traffico smaltita in una topologia T1, con N nodi, C canali e distanza media M1, rispetto a quella smaltita in una topologia T2, con N nodi, C canali e distanza media M2>M1, dipende dalla distribuzione del traffico tra nodi

Possible answers: A, B, C (not case sensitive)
Please enter your answer: c
Correct!
da definire.

Quiz finished. Your result: 14/30 (max 28) -- correct: 2 -- wrong: 1
Elapsed time for this quiz: 0h 0m 41s
```


### Info

This project has been tested using `python3.7`.

