# Samochód zdalnie sterowany
Uwaga projekt nie jest jeszcze skończony!

Poniżej przedstawie szczegółowy opis budowy prostego samochodu autonomicznego. Części które użyłem znajdują się w lokalizacji rcCar/Inne/czesci.

Jako podwozie użyłem zestawu do samodzielnego montażu (patrz plik z częściami). Samochód zasilany jest Baterią litowo-polimerową z 3 ogniwami która po naładowaniu daje napięcie ok. 12V Aby zasilić Arduino, Raspberry Pi oraz serwo które przyjmują 5V wykorzystałem przetwornice step-down. Ja użyłem DFR0205 ale tańsze zamienniki równiesz będą dobre. Jako sterownik silnika zastosowałem tani modułu wysokonapięciowego BTS7960D.


Oto prosty schemat zawierający główne komponenty samochodu:
![Schematic_rcCar_2022-08-09](https://user-images.githubusercontent.com/106252516/183687655-5ca91baa-e46a-4876-8bab-b56d4de04d62.png)
