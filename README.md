# Autonomiczny samochód zdalnie sterowany
```python
UWAGA PROJEKT NIE JEST JESZCZE ZKONCZONY
```
Poniżej przedstawię szczegółowy opis budowy prostego samochodu autonomicznego. Części, które użyłem znajdują się [tutaj](https://github.com/M1chol/rcCar/blob/main/Inne/czesci.md). Oprócz wymienionych elementów przydadzą się kable złączki itd. Do zmontowania całości oczywiście będzie potrzeba lutownica. W folderze skrypty znajdują się wszystkie napisane przeze mnie programy potrzebne do odpalenia samochodu. W razie dodatkowych pytań proszę o kontakt.

---

## 1. Zmontowanie samochodu
Jako podwozie użyłem zestawu do samodzielnego montażu (patrz plik z częściami). Ponieważ instrukcja dołączona w zestawie jest bardzo skromna, zmodyfikowaną dokładniejszą wersję znajdziesz [tutaj](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy) (Instrukcja1.png i Instrukcja2.png).

### Parę zdjęć z montażu:
![IMG_20220727_143825](https://user-images.githubusercontent.com/106252516/184039809-f9397042-ed86-4d5f-9c24-03a827240d34.png)

Samochód zasilany jest Baterią litowo-polimerową z 3 ogniwami, która po naładowaniu daje napięcie ok. 12V. Aby zasilić Arduino, Raspberry Pi oraz serwo, które przyjmują 5V wykorzystałem przetwornice step-down. W moim przypadku DFR0205, ale tańsze zamienniki również będą dobre. Jako sterownik silnika zastosowałem tani moduł wysokonapięciowy BTS7960D.

### Oto prosty schemat zawierający główne komponenty samochodu:
![Schematic_rcCar_2022-08-09](https://user-images.githubusercontent.com/106252516/183687655-5ca91baa-e46a-4876-8bab-b56d4de04d62.png)
<!--DODAĆ ZDJĘCIE KOŃCOWE-->

---

## 2. Programowanie
### Etap 1: zdalne sterowanie
Na początku zrobiłem zdalne sterowanie przy pomocy kontrolera Xbox. Kontroler jest podłączony do komputera stacjonarnego, na którym sshCarController.py przechwytuje wciskane przyciski przy pomocy biblioteki pygame oraz wysyła input do raspberry pi po SSH (biblioteka paramiko). Konkretnie aplikacja na komputerze uruchamia wcześniej przygotowany program na Raspberry tj. arduinoConnect.py i wysyła jej określone komendy. arduinoConnect.py przekazuje je następnie do Arduino po porcie seryjnym (niżej łatwiejszy sposób).
### Diagram połączenia wykorzystującego SSH:
![IMG](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy/ScriptsDiagram1.jpg)

Dzięki takiemu połączeniu zasięg sterowania jest taki jak sieć Wi-Fi, do której jesteśmy podłączeni. Minusem natomiast jest większe opóźnienie. Aby je (prawie) całkowicie zniwelować kontroler połączyłem bezpośrednio do Raspberry.

### Diagram połączenia bezpośredniego:
![IMG](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy/ScriptsDiagram2.jpg)

#### Efekt końcowy etapu pierwszego
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm.gif)
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm2.gif)

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

#### Advanced line detection

![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm5_copy.gif)
