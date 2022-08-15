# Samochód zdalnie sterowany
Uwaga projekt nie jest jeszcze skończony!

Poniżej przedstawie szczegółowy opis budowy prostego samochodu autonomicznego. Części, które użyłem znajdują się [tutaj](https://github.com/M1chol/rcCar/blob/main/Inne/czesci.md). Oprócz wymienionych elementów przydadzą się kable złączki itd. Do zmontowania całości oczywiście będzie potrzeba lutownica.

## 1. Zmontowanie samochodu
Jako podwozie użyłem zestawu do samodzielnego montażu (patrz plik z częściami). Ponieważ instrukcja dołączona w zestawie jest bardzo skromna, zmodyfikowaną dokładniejszą wersję znajdziesz [tutaj](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy) (Instrukcja1.png i Instrukcja2.png). 

### Parę zdjęć z montażu:
![IMG_20220727_143825](https://user-images.githubusercontent.com/106252516/184039809-f9397042-ed86-4d5f-9c24-03a827240d34.png)

Samochód zasilany jest Baterią litowo-polimerową z 3 ogniwami, która po naładowaniu daje napięcie ok. 12V, Aby zasilić Arduino, Raspberry Pi oraz serwo, które przyjmują 5V wykorzystałem przetwornice step-down. W moim przypadku DFR0205, ale tańsze zamienniki również będą dobre. Jako sterownik silnika zastosowałem tani moduł wysokonapięciowy BTS7960D.

### Oto prosty schemat zawierający główne komponenty samochodu:
![Schematic_rcCar_2022-08-09](https://user-images.githubusercontent.com/106252516/183687655-5ca91baa-e46a-4876-8bab-b56d4de04d62.png)

## 2. Programowanie
### Etap 1: zdalne sterowanie
Na początku zrobiłem zdalne sterowanie przy pomocy kontrolera Xbox. Kontroler jest podłączony do komputera stacjonarnego, na którym sshCarController.py przechwytuje wciskane przyciski przy pomocy biblioteki pygame oraz wysyła input do raspberry pi po SSH (biblioteka paramiko). Konkretnie aplikacja na komputerze uruchamia wcześniej przygotowany program na Raspberry tj. arduinoConnect.py i wysyła jej określone komendy. arduinoConnect.py przekazuje je następnie do Arduino po porcie seryjnym (miżej łatwiejszy sposób).
### Diagram połączenia wykorzystującego SSH:
![IMG](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy/ScriptsDiagram1.jpg)

Dzięki takiemu połączeniu zasięg sterowania jest taki jak sieć Wi-Fi, do której jesteśmy podłączeni. Minusem natomiast jest większe opóźnienie, aby je (prawie) całkowicie zniwelować podłączyłem kontroler bezpośrednio do Raspberry.

### Diagram połączenia bezpośredniego:
![IMG](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy/ScriptsDiagram2.jpg)

### Efekt końcowy etapu pierwszego
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm.gif)
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm2.gif)

### Etap 2: wykrywanie lini
