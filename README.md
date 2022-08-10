# Samochód zdalnie sterowany
Uwaga projekt nie jest jeszcze skończony!
Niektóre pliki nie są skończone i nie działają.

Poniżej przedstawie szczegółowy opis budowy prostego samochodu autonomicznego. Części które użyłem znajdują się [tutaj](https://github.com/M1chol/rcCar/blob/main/Inne/czesci.md). Oprócz wymienonych elementów przydadzą się kable złączki itd. Do zmontowania całości oczywiście będzie potrzeba lutownica.

## 1. Zmontowanie podwozia
Jako podwozie użyłem zestawu do samodzielnego montażu (patrz plik z częściami). Ponieważ instrukcja dołączonej w zestawie jest bardzo skromna, zmodyfikowaną dokładniejszą wesje znajdziesz [tutaj](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa) (Instrukcja1.png i Instrukcja2.png). 

# Parę zdjęć z montażu:
![IMG_20220727_143825](https://user-images.githubusercontent.com/106252516/184039809-f9397042-ed86-4d5f-9c24-03a827240d34.png)


 Samochód zasilany jest Baterią litowo-polimerową z 3 ogniwami która po naładowaniu daje napięcie ok. 12V Aby zasilić Arduino, Raspberry Pi oraz serwo które przyjmują 5V wykorzystałem przetwornice step-down. Ja użyłem DFR0205 ale tańsze zamienniki równiesz będą dobre. Jako sterownik silnika zastosowałem tani modułu wysokonapięciowego BTS7960D.


### Oto prosty schemat zawierający główne komponenty samochodu:
![Schematic_rcCar_2022-08-09](https://user-images.githubusercontent.com/106252516/183687655-5ca91baa-e46a-4876-8bab-b56d4de04d62.png)
