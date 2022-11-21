# Autonomiczny samochód zdalnie sterowany
```python
UWAGA PROJEKT NIE JEST JESZCZE ZKONCZONY
```
Poniżej przedstawię szczegółowy opis budowy prostego samochodu autonomicznego. Części, które użyłem znajdują się [tutaj](https://github.com/M1chol/rcCar/blob/main/Inne/czesci.md). Oprócz wymienionych elementów przydadzą się kable złączki itd. Do zmontowania całości oczywiście będzie potrzeba lutownica. W folderze skrypty znajdują się wszystkie napisane przeze mnie programy potrzebne do odpalenia samochodu. W razie dodatkowych pytań proszę o kontakt.

---

## 1. Zmontowanie samochodu
Jako podwozie użyłem zestawu do samodzielnego montażu (patrz plik z częściami). Ponieważ instrukcja dołączona w zestawie jest bardzo skromna, zmodyfikowaną dokładniejszą wersję znajdziesz [tutaj](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy) (Instrukcja1.png i Instrukcja2.png).
  
**Zamierzony efekt końcowy**
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/IMG_20220930_195806.jpg)
  
### Parę zdjęć z montażu:
![IMG_20220727_143825](https://user-images.githubusercontent.com/106252516/184039809-f9397042-ed86-4d5f-9c24-03a827240d34.png)

Samochód zasilany jest Baterią litowo-polimerową z 3 ogniwami, która po naładowaniu daje napięcie ok. 12V. Aby zasilić Arduino, Raspberry Pi oraz serwo, które przyjmują 5V wykorzystałem przetwornice step-down. W moim przypadku DFR0205, ale tańsze zamienniki również będą dobre. Jako sterownik silnika zastosowałem tani moduł wysokonapięciowy BTS7960D.

### Oto prosty schemat zawierający główne komponenty samochodu:
![Schematic_rcCar_2022-08-09](https://user-images.githubusercontent.com/106252516/183687655-5ca91baa-e46a-4876-8bab-b56d4de04d62.png)
  
### WAŻNA INFORMACJA!
W moim projekcie pominąłem dwie istotnie rzeczy więc jeżeli planujesz zbudować podobny samochód koniecznie zmodyfikuj schemat:
1. BMS (Battery Menegment System) - Istotny punkt jeżeli używasz bateri wielo ogniwowych. W moim samochodzie po dłuższym czasie jedno ogniwo ma wyraźnie niższe napięcie od pozostałych. BMS ze stabilizatorem napięć rozwiąże ten problem
2. Bezpiecznik - Początkowo miałem w planach dodanie bezpiecznika na dodatnim terminalu baterii. Jest to dobre dodatkowe zabezpieczenie przed przypadkowym zwarciem a więc niekontrolowanym i nagłum utlenianiem litu z polimerem :)

---

## 2. Programowanie
### Etap 1: zdalne sterowanie
Na początku zrobiłem zdalne sterowanie przy pomocy kontrolera Xbox. Kontroler jest podłączony do komputera stacjonarnego, na którym sshCarController.py przechwytuje wciskane przyciski (biblioteka pygame) i wysyła je do raspberry pi po SSH (biblioteka paramiko). RPi po porcie seryjnym wysyła komendy do Arduino które wykonuje polecenia (niżej łatwiejszy sposób).
  
### Diagram połączenia wykorzystującego SSH:
![IMG](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy/ScriptsDiagram1.jpg)
  
Dzięki takiemu połączeniu zasięg sterowania jest taki jak sieć Wi-Fi, do której jesteśmy podłączeni. Minusem natomiast jest większe opóźnienie. Prostszym sposobem jest pominięcie w całości komputer stacjonarny; kontroler połączyłem bezpośrednio do Raspberry.
  
### Diagram połączenia bezpośredniego:
![IMG](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy/ScriptsDiagram2.jpg)
  
#### Efekt końcowy etapu pierwszego
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm.gif)
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm2.gif)
   
---
   
### Etap 2: wykrywanie krawędzi
### Założenia:
1. Pasy to białe linie na czarnym tle.
2. Samochód zostaje ułożony w poprawnej pozycji startowej; między pasami.
3. Możliwe ostre zakręty drogi

Pierwszym krokiem do autonomicznej jazdy jest dobre wykrywanie pasów ruchu. Na samochodzie zamontowałem kamerę, która podłączona jest do Raspberry. Obraz streamuje na port ip Raspberry przy pomocy aplikacji motion. Następnie na komputerze podłączonym do tej samej sieci działa [program analizujący stream](https://github.com/M1chol/rcCar/blob/main/Skrypty/LineDetectionAdvanced.py).

Poniżej opiszę działanie dwóch algorytmów do wykrywania linii, pierwszy z nich świetnie nadaje się do lokalizacji na prostym (lub lekko skręcającym) kawału pasa. Drugi natomiast wykorzystam do analizy skrętów pod dużym kątem.
### Proste wykrywanie krawędzi:
**Zamierzony efekt końcowy**
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm3.gif)
W pierwszej kolejności na zdjęciu znajdujemy miejsca, w których jest duża zmiana kontrastu przy użyciu filtru [canny](https://pl.wikipedia.org/wiki/Canny). Rezultat to czarne zdjęcie z zaznaczonymi na biało krawędziami pasów. Robimy to aby z analizowango zdjęcia usunąć zbędne informacje. Następnie stosujemy [transformacje Hougha](https://pl.wikipedia.org/wiki/Transformacja_Hougha), czyli algorytm wykrywający linie proste na obrazie. Liste otrzymanych linii dzielimy według nachylenia: proste o ujemnym wektorze kierunku prawy pas, a o dodatnim lewy. Z podzielonych linii wyciągamy dwie średnie, które dokładnie opisują dwa wykryte pasy.
### Podsumowanie procesu
1. Zdjęcie wejściowe
2. Nałożenie filtru Canny
3. Wykrycie linii
4. Podzielenie linii względem nachylenia
5. Wyciągnięcie średniej
### Animacja:
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/lineDetecionProces.gif)

### Zaawansowane wykrywanie pasów:
**Zamierzony efekt końcowy:**  
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/car.gif)  
  
Na początku rozciągamy obraz orginalny tak aby usunąć perspektywe i osiągnąc widok z lotu ptaka. Następnie poobnie jak we wcześniejszym punkcie filtrujemy rozciągnięty obraz przy pomocy filtru canny i wyszukujemy na nim linie. Aby pozbyć się lini które zostały wykryte błędnie i odseparować poszczególne pasy w miejscu w którym spodziewamy się zaobserwować początek lewego pasa wyszukujemy najbliższeą wykrytą linie. W kolejnym kroku sprawdzamy czy jej odległość od spodziewanego punktu jest w zadanym przedziale. Tak samo postępujemy z pasem prawym.  
  
**Efekt na filmie**  
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm5_copy.gif)
   
Jak możesz zobaczyć na powyższej animacji, kolejnym krokiem po znalezieniu początku pasa jest znalezienie najbliższej mu lini licząc od jego końca. Ten algorytm stosujemy w pętli. Należy pamiętać o zmienianu lini od której mierzymy odległość, oraz o usuwaniu wcześniej analizowanych lini ze zbioru wszystkich lini.  
   
**Animacja algorytmu**  
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/linedetect.gif)  
   
**Fragment kodu**   
Niżej zamieszczam fragmenty kodu z dodatkowymi komentarzami odpowiedzialne za opisany algorytm 

Fragment odpowiedzialny za wywołanie funkcji:
> lineDetection.py
```python
import lineDetectionHandleLines as Lines      # odwołanie do pliku z algorytmem
startingPoints=[[246, 460, 246, 450], [411, 460, 411, 450]]     # zadanie linie od których zaczynamy poszukiwanie pierwszych pasów
left_line = Lines.detectBirdLines(startingPoints[0], lines, 55, numberOfLines=numberOfSteps)      # wywołanie funkcji
```  
 
Zasadnicza funkcja:
> lineDetecionHandleLines.py
```python
def detectBirdLines(line_start, lines, maxDist=40, numberOfLines=0):
    """
    :param line_start: linia od ktorej szukamy
    :param lines: wszystkie linie
    :param maxDist: maksymalna odleglosc lini
    :param numberOfLines: ilosc krokow, jezeli 0 - do ostatniej wykrytej
    :return: tablica lini w jednym pasie
    """
    detectedLines=[]                                                                          # zapisuje znalezione linie
    krok=0                                                                                    # dodaje możliwość zadania maksymalnej liczby kroków 
    while True if numberOfLines==0 else krok<numberOfLines:                                   # jeżeli zadana liczba kroków to 0 ignoruj licznik, w przeciwnym raze ogranicz liczbę pętli
        closestLineslist=distaceBetweenPoints(line_start, lines, True, displacement=True)     # zwróć dla każdej lini [odleglosc, przesuniecie na x, indeks (jeżeli sortowanie)]
        closestLine=closestLineslist[0]                                 # przypisz najbliższą linie do zmiennej
        if closestLine[0] <= maxDist:                                   # jeżeli odl mniejsza niż maksymalna
            chosenLine=lines[int(closestLine[2])]                           # zapisz linie (odwołanie do prawdziwej lini nie tablicy z odleglosciami)
            detectedLines.append(chosenLine)                                # dodaj znalezioną linie do tablicy
            line_start=chosenLine                                           # nadpisz linie od której szukamy
        else:                                                           # jeżeli odl większa nisz maksymalna
            return detectedLines                                            # zwróć tablice z wykrytymi liniami
        krok+=1                                                         # zwiększ licznik
        lines=np.delete(lines, int(closestLineslist[0][2]), 0)          # usuń analizowaną linie z tablicy wszyst. lini
    return detectedLines                                              # zwróć tablice z wykrytymi liniami
```
