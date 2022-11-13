import numpy as np
import matplotlib.pyplot as plt

P_1_X=[51,51,89,89,80,50,51,49,48,46,89,91,80,44,50,
       +80,59,51,79,26,50,51,49,82,82,88,50,49,57,54,
       +50,51,51,47,50,91,75,54,50,82,91,49,80,70,26,
       +26,87,55]
P_1_Y=[1,22,9,14,56,16,26,63,69,74,5,2,59,77,56,
       +58,85,9,62,95,16,45,63,50,52,12,60,66,86,87,
       +17,9,47,68,59,3,68,87,18,50,4,66,59,74,95,
       +95,25,87]
P_2_X=[51,50,80,82,78,51,50,48,35,32,86,87,69,32,45,
       +70,74,50,62,43,51,50,48,78,73,87,43,37,74,64,
       +51,50,50,46,45,88,62,70,51,76,88,43,75,65,40,
       +37,85,70]
P_2_Y=[14,62,59,48,63,52,51,69,88,91,29,18,77,91,75,
       +76,71,22,83,79,29,58,69,63,72,26,79,86,71,81,
       +37,18,55,74,75,13,83,76,27,66,13,79,67,80,83,
       +86,30,75]

# zbiór wykrytych punktów

Wykryte_Punkty_HOUGHA=np.array([[P_1_X],[P_1_Y],[P_2_X],[P_2_Y]])
#Wykryte_Punkty_HOUGHA=Wykryte_Punkty_HOUGHA.T
print(Wykryte_Punkty_HOUGHA)

# WYKRESY LINII PRZECHODZĄCEJ PRZEZ DWA PUNKTY
# ORAZ LINII PROSTOPADŁEJ

# punkty na prostej postać wierszowqa
#P1 = np.array([5, 3])
#P2= np.array([-7,8])

# zakładam wartości punktów do analizy
#x3=np.array([-12.5,-10,-2.5,-5,-5])
#y3=np.array([2.5,12.5,2.5,0,10])

def linie(Wykryte_Punkty_HOUGHA):

    # współrzędne x,y punktów początków linii
    P_1_X=Wykryte_Punkty_HOUGHA[0]
    P_1_Y=Wykryte_Punkty_HOUGHA[1]

    # współrzędne x,y punktów końców linii
    P_2_X=Wykryte_Punkty_HOUGHA[2]
    P_2_Y=Wykryte_Punkty_HOUGHA[3]

    # ITERACJA NR 1
    # początek
    wiersz=Wykryte_Punkty_HOUGHA.T[0]
    P1=np.array([wiersz[0,0],wiersz[0,1]])
    # koniec
    P2=np.array([wiersz[0,2],wiersz[0,3]])

    # Przyrosty wartości

    DEL=(P2-P1)
    L=np.sqrt(DEL[0]*DEL[0]+DEL[1]*DEL[1])
    DEL=DEL/L

    # równanie parametryczne prostej przechodzącej przez punkty P1-P2
    A= DEL[0]
    B= DEL[1]

    # wektor kierunkowy P1-P2
    # VEC=np.array([[A],[B]])

    # t=[-10,0,10]

    # równanie parametryczne prostej

    # lin1=P2.reshape(2,1)+VEC*t

    # x1,y1=lin1


    # wykres linii prostopadłej do linii P1-P2

    A2= -DEL[1]
    B2= DEL[0]
    # wektor kierunkowy P1-P2
    VEC2=np.array([[A2],[B2]])

    # równanie parametryczne prostej prostopadłej
    # lin2=P2.reshape(2,1)+VEC2*t
    # x2, y2 = lin2

    x0 = P2[0]
    y0 = P2[1]
    # wyznaczenie wartości C postaci ogólnej linii prostopadłej
    C=-(A*x0+B*y0)

    # kryterium
    rownanie1=A*P_1_X+B*P_1_Y+C>0
    rownanie2=A * P_2_X + B * P_2_Y + C > 0
    rownanie=rownanie1&rownanie2

    # indeksy
    deklarowane_indeksy=np.arange(len(P_1_X.T))
    #deklarowane_indeksy=np.transpose(deklarowane_indeksy)


    # nowy zbiór punktów Hogha
    nowy_zbior=Wykryte_Punkty_HOUGHA.T[rownanie.T]

    #plt.plot(x1,y1,"o-", color="blue",linewidth=2, alpha=0.5)
    #plt.plot(x2, y2, "o-", color="blue", linewidth=2, alpha=0.5)
    plt.plot(x0, y0, "o-", color="red", linewidth=2, alpha=0.5)
    plt.plot(P_1_X, P_1_Y, "o-", color="green", linewidth=2, alpha=0.5)
    plt.plot(nowy_zbior.T[0], nowy_zbior.T[1], "o", color="black", linewidth=2, alpha=0.5)

    return nowy_zbior


nowy_zbior = linie(Wykryte_Punkty_HOUGHA)
len(nowy_zbior)
print(nowy_zbior)
plt.show()


