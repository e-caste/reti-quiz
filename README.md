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
Do you want to update the .txt file with the latest version from Google Docs? (Press Enter to skip) [y/N] 
Do you want to change the number of questions for this quiz? (Default is 28) [y/N] y
What number of questions would you like? Enter a number: 3
Quiz 103
E’ data una topologia di rete con N nodi e M canali unidirezionali. Ogni canale ha capacità C Mbit/s. L’algoritmo di instradamento è tale da distribuire uniformemente il traffico sui canali della rete. Il numero medio di canali attraversato da un pacchetto nel percorso della sorgente alla destinazione è pari a D. La quantità massima di traffico smaltito dalla rete aumenta se: 
   A) Diminuisce C a pari N, M e D
   B) Diminuisce M a pari N, D e C
   C) Diminuisce D a pari N, M e C
   D) Diminuisce N a pari D, M e C

Possible answers: A, B, C, D (not case sensitive)
Please enter your answer: c
Correct!
se la distanza media diminuisce, a parità di capacità del canale ,il traffico smaltito dovrebbe aumentare.

Quiz 125
L’Address Resolution Protocol (ARP)
A) Consente di ottenere un indirizzo Ethernet da assegnare alla scheda della macchina che ha effettuato la richiesta ARP
B) Consente ad un host di conoscere l’indirizzo ip del suo DNS server
C) Realizza in termini OSI una funzione di mapping (traduzione) tra (3)-indirizzi e (2)-indirizzi

Possible answers: A, B, C (not case sensitive)
Please enter your answer: c
Correct!
consente di conoscere l’indirizzo mac di un’altro host conoscendo il suo indirizzo ip

Quiz 51
Una scheda Ethernet di uno switch elabora (ovvero legge e decide se e come instradare)
   A) Solo i pacchetti con indirizzo MAC di destinazione broadcast
   B) Tutti i pacchetti, indipendentemente dall’indirizzo di destinazione
   C) Solo i pacchetti con indirizzo MAC di destinazione unicast pari a quello dello switch
   D) Solo i pacchetti con indirizzo MAC di destinazione multicast

Possible answers: A, B, C, D (not case sensitive)
Please enter your answer: a
Wrong.
Vedere funzionamento switch.

Quiz finished. Your result: 14/30 (max 28) -- correct: 2 -- wrong: 1
```


### Info

This project has been tested using `python3.7`.

