import numpy as np
import matplotlib.pyplot as plt
# WYKRESY LINII PRZECHODZĄCEJ PRZEZ DWA PUNKTY
# ORAZ LINII PROSTOPADŁEJ

# punkty na prostej postać wierszowqa
P1 = np.array([5, 3])
P2= np.array([-7,8])

# zakładam wartości punktów do analizy
x3=np.array([-12.5,-10,-2.5,-5,-5])
y3=np.array([2.5,12.5,2.5,0,10])

def linie(P1,P2,x3,y3):

    # Przyrosty wartości
    DEL=(P2-P1)
    L=np.sqrt(DEL[0]*DEL[0]+DEL[1]*DEL[1])
    DEL=DEL/L
    #print(DEL)
    # równanie parametryczne prostej przechodzącej przez punkty P1-P2
    A= DEL[0]
    B= DEL[1]
    # wektor kierunkowy P1-P2
    VEC=np.array([[A],[B]])
    #print(VEC)
    t=[-10,0,10]
    # równanie parametryczne prostej

    lin1=P2.reshape(2,1)+VEC*t
    #lin=np.transpose(lin)
    x1,y1=lin1
    #print(x,y)

    # wykres linii prostopadłej do linii P1-P2
    A2= -DEL[1]
    B2= DEL[0]
    # wektor kierunkowy P1-P2
    VEC2=np.array([[A2],[B2]])
    #print(VEC)
    t=[-10,0,10]
    # równanie parametryczne prostej prostopadłej
    lin2=P2.reshape(2,1)+VEC2*t
    x2, y2 = lin2
    #lin=np.transpose(lin)

    # wyznaczenie wartości C postaci ogólnej linii prostopadłej
    C=-(A*P2[0]+B*P2[1])

    rownanie=A*x3+B*y3+C>=0

    plt.plot(x1,y1,"o-", color="green", linewidth=2, alpha=0.5)
    plt.plot(x2, y2, "o-", color="red", linewidth=2, alpha=0.5)
    plt.plot(x3, y3, "o", color="black", linewidth=2, alpha=0.5)

    return rownanie


row=linie(P1,P2,x3,y3)
print(row)
znalezione_indeksy=np.arange(len(row))
znalezione_indeksy=znalezione_indeksy[row]
print(znalezione_indeksy)
#plt.show()


