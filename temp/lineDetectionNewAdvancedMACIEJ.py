import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

def canny(image):
    img_gray=cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_blur=cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_cann=cv2.Canny(img_blur, 150, 300)
    return img_cann

def displayLine(image, lines, color=(0, 0, 255), color2=(0, 0, 255)):
    line_image= np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2=line.reshape(4)
            cv2.line(line_image,(x1,y1),(x2,y2),color,4)
            cv2.circle(line_image, (x1, y1), 2, color2, 2)
            cv2.circle(line_image, (x2, y2), 2, color2, 2)
    return line_image

def avarageSlopeBird(image, lines, qual=3):
    lane1=[]
    lane2=[]
    threshold=50
    # podzielenie punktów wedłóg "wysokości"
    area=[]
    for line in lines:
        x1, y1, x2, y2=line.reshape(4)
        area.append([x1,y1])
        area.append([x2,y2])
    if area:
        area=sorted(area, key=lambda x: x[1],reverse=True)
        carret=area[0]
        lane1.append(carret)
        for pointNr in range(1,len(area)):
            if abs(area[pointNr][0]-carret[0])<threshold:
                lane1.append(area[pointNr])
                carret=area[pointNr]
            else: lane2.append(area[pointNr])
        index=0
        while index<len(lane2)-1:
            if abs(lane2[index][0]-lane2[index+1][0])>threshold:
                lane2.pop(index+1)
            else:
                index+=1

    return [lane1,lane2]

# ANALIZA OBRAZU Z PIERWSZEJ OSOBY #

def avarageSlopeIntersect(image, lines): #wyciąganie średniej z lini
    leftFit=[] #lewy pas
    rightFit=[] #prawy pas
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters= np.polyfit((x1,x2),(y1,y2), 1)
        slope = parameters[0] #nachylenie linii
        intercept = parameters[1]
        if slope < 0: #jeżeli funkcja rosnąca
            leftFit.append((slope, intercept)) #dodaj linie do lewego pasa
        elif slope > 0:
            rightFit.append((slope, intercept)) #jeżeli funkcja malejąca dodaj linie do prawego pasa
        else:
            pass
    leftFitAvarage = np.average(leftFit, axis=0) #średnia
    rightFitAverage = np.average(rightFit, axis=0) #średnia
    leftLine = makeCoords(image, leftFitAvarage) #koordynaty lini
    rightLine = makeCoords(image, rightFitAverage) #koordynaty lini
    return np.array([leftLine, rightLine])

def AnalizeForLines(image):
    img_cann=canny(image)  # zastosowanie metody canny
    gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred=cv2.GaussianBlur(gray, (7, 7), 0)
    (T, thresh)=cv2.threshold(blurred, 150, 255,
                              cv2.THRESH_BINARY)
    img_crop=regionOfIntrest(thresh, 0)  # przycięcie zdjęcia
    try:
        lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 70, None, minLineLength=60, maxLineGap=20)
        avaraged_lines=avarageSlopeIntersect(image, lines)
        image_lines=displayLine(image, avaraged_lines)
        img_comb=cv2.addWeighted(image, 0.8, image_lines, 1, 1, 1)
        return img_comb, img_crop
    except:
        return image, img_crop

def makeCoords(image, line_params):
    slope, intercept = line_params
    y1 = image.shape[0]
    y2 = int(y1*(2/5))
    x1=int((y1-intercept)/slope)
    x2=int((y2-intercept)/slope)
    return np.array([x1,y1,x2,y2])


def regionOfIntrest(image, normal=0):
    height, width = image.shape
    if normal==1:
        area=np.array([[(70,90), (570,90), (width // 2, height + 20)]])
    else:
        area=np.array([[(0, height), (width - 3, height), (width - 3, int(height * (1 / 3))),(0, int(height * (1 / 3)))]])  # stworzenie prostokąta o punktach
    mask=np.zeros_like(image) #puste zdjęcie o wymiarach oryginału
    cv2.fillPoly(mask,area,255) #wypełnienie pustego zdjęcia białym kolorem wedłóg zadanego kształtu
    img_mask=cv2.bitwise_and(image,mask) #operacja and na podanych obrazach
    return img_mask


def makeCordsBird(image, line_params, qual, cell_nr):
    slope, intercept = line_params
    height, width, _=image.shape
    y1 = int(height*((cell_nr+1)/qual))
    y2 = int(y1-height*(1/qual))
    x1=int((y1 - intercept) / slope)
    x2=int((y2 - intercept) / slope)
    return np.array([x1,y1,x2,y2])


def perspectiveWarp(img):
    IMAGE_H, IMAGE_W, _=img.shape
    src=np.float32([[0, IMAGE_H], [IMAGE_W, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    dst=np.float32([[300, IMAGE_H], [355, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    M=cv2.getPerspectiveTransform(src, dst)  # The transformation matrix
    img=img[int(IMAGE_H*(1/4)):IMAGE_H, 0:IMAGE_W]  # Apply np slicing for ROI crop
    warped_img=cv2.warpPerspective(img, M, (IMAGE_W, IMAGE_H))  # Image warping
    return warped_img

#TODO tutaj

def linie(Wykryte_Punkty_HOUGHA,max_odl_zad):
    # zmienne wyjściowe "Wykryte_P1", "Wykryte_P2" opisują zbiory
    # punktów Hougha określające początki i końce posortowanych
    # linii opisujących linię pasa ruchu

    for line in Wykryte_Punkty_HOUGHA:
        print(line)
        x1, y1, x2, y2 = line[0]
        #print(x1, y1, x2, y2)
        plt.plot([x1, x2], [y1, y2])
    plt.show()

    #określam roboczy zbiór dynamicznie zmiennych punktów Hougha
    Analizowane_Punkty_Hougha=Wykryte_Punkty_HOUGHA
    Analizowane_Punkty_Hougha=np.sort(Analizowane_Punkty_Hougha, axis=1)[::-1]
    Analizowane_Punkty_Hougha=Analizowane_Punkty_Hougha.T

    # wykrywanie linii zaczynam od 1 szego punktu
    # punkty P1 i P2 są połączone linią hougha
    # współrzędne x,y punktów początków linii
    P_1_X=Analizowane_Punkty_Hougha[0]
    P_1_Y=Analizowane_Punkty_Hougha[1]

    # współrzędne x,y punktów końców linii
    P_2_X=Analizowane_Punkty_Hougha[2]
    P_2_Y=Analizowane_Punkty_Hougha[3]

    # ITERACJA NR 1
    # początek
    wiersz=Analizowane_Punkty_Hougha.T[0]
    P1=np.array([wiersz[0,0],wiersz[0,1]])
    # koniec
    P2=np.array([wiersz[0,2],wiersz[0,3]])

    # Przyjmuje warunek początkowy dla pętli
    odl_min = 0
    lp_itercji = 1
    # wykryte P1 są interpretowane jak zwykł list Pythona
    Wykryte_P1 = [P1]
    Wykryte_P2 = [P2]

    # PETLA WHILE
    while (odl_min<=max_odl_zad)|lp_itercji<=5:
    #while lp_itercji<=3:
        # współrzędne punktów
        xp = P1[0]
        yp = P1[1]
        x0 = P2[0]
        y0 = P2[1]

        # - wektory kierunkowe linii hougha łączącej P1 z P2
        # a także - współczynniki równania ogólnego prostej prostopadłej
        # do niej o postaci:
        # A*x+B*y+C=0
        # przyrosty dx i dy
        DEL=(P2-P1)
        # długość
        L=np.sqrt(DEL[0]*DEL[0]+DEL[1]*DEL[1])
        # normalizacja
        DEL=DEL/L

        # parametry A i B równania w postaci ogólnej
        A= DEL[0]
        B= DEL[1]

        # wektor kierunkowy P1-P2
        # VEC=np.array([[A],[B]])

        # t=[-10,0,10]

        # równanie parametryczne prostej

        # lin1=P2.reshape(2,1)+VEC*t

        # x1,y1=lin1

        # wykres linii prostopadłej do linii P1-P2

        #A2= -DEL[1]
        #B2= DEL[0]
        # wektor kierunkowy P1-P2
        #VEC2=np.array([[A2],[B2]])

        # równanie parametryczne prostej prostopadłej
        # lin2=P2.reshape(2,1)+VEC2*t
        # x2, y2 = lin2

        # wyznaczenie wartości C postaci ogólnej linii prostopadłej
        C=-(A*x0+B*y0)

        # kryterium przynależności punktów do półpłaszczyzny
        # ograniczonca linia prostopadłą do linii Hougha
        # w punkcie jej końca
        # - wskaznik znaku półpłaszczyzny punktów P_1 oraz P_2
        # - punkty dodatnio określone leżą powyżej linii
        rownanie1=A*P_1_X+B*(P_1_Y)+C>0
        rownanie2=A*P_2_X+B*(P_2_Y)+C > 0
        # - warunek dla całej linii (punktów początku i końca)
        rownanie=rownanie2

        # indeksy punktów półpłaszczyzny
        deklarowane_indeksy=np.arange(len(P_1_X.T))

        # nowy zbiór punktów Hougha na półpłaszczyznie

        Punkty_polplaszczyzny=Analizowane_Punkty_Hougha.T[rownanie.T]

        EMP=np.any(Punkty_polplaszczyzny)

        # jeżeli macierz jest pusta
        if (EMP==False):
            break

        #if Punkty_polplaszczyzny:

        lin_Hougha_X=np.array([xp,x0])
        lin_Hougha_Y = np.array([yp,y0])

        #plt.plot(x1,y1,"o-", color="blue",linewidth=2, alpha=0.5)
        #plt.plot(x2, y2, "o-", color="blue", linewidth=2, alpha=0.5)
        plt.plot(lin_Hougha_X, lin_Hougha_Y, "o-", color="red", linewidth=4, alpha=0.5)
        plt.plot(P_1_X, P_1_Y, "o", color="green", linewidth=2, alpha=0.5)
        plt.plot(Punkty_polplaszczyzny.T[0], Punkty_polplaszczyzny.T[1], "o", color="black", linewidth=2, alpha=0.5)
        #plt.show()

        # - W zbiorze punktów półpłaszczyzny
        # - znajdę punkt początkowy następnej linii Hougha,
        # - położony najbliżej P2.
        # w tym celu wyznaczam przyrosty
        DDX = P2[0] - Punkty_polplaszczyzny.T[0]
        DDY = P2[1] - Punkty_polplaszczyzny.T[1]
        # suma kwadratów
        odl=np.sqrt((DDX**2+DDY**2))

        index_min_odl = np.argmin(odl)
        odl_min=odl[index_min_odl]

        # warunek: jeśli odl_min istnieje oraz
        # jest mniejsza od dopuszczalnej wart maksymalnej
        if odl_min<max_odl_zad:
            # współrzędne nowego punktu P_N1
            wiersz_N = Punkty_polplaszczyzny[index_min_odl]
            # początek
            P_N1 = np.array([wiersz_N[0], wiersz_N[1]])
            # koniec
            P_N2 = np.array([wiersz_N[2], wiersz_N[3]])
        else:
            break


        # - Podstawienie
        Analizowane_Punkty_Hougha=Punkty_polplaszczyzny.T

        lp_itercji=lp_itercji+1
        print(lp_itercji)

        P1=P_N1
        P2=P_N2
        # współrzędne x,y punktów początków linii
        P_1_X = Analizowane_Punkty_Hougha[0]
        P_1_Y = Analizowane_Punkty_Hougha[1]

        # współrzędne x,y punktów końców linii
        P_2_X = Analizowane_Punkty_Hougha[2]
        P_2_Y = Analizowane_Punkty_Hougha[3]


        Wykryte_P1.append(P1)
        Wykryte_P2.append(P2)
    print(Wykryte_P1,Wykryte_P2)
    return Wykryte_P1, Wykryte_P2

def avarageLines(image, lines):
    newLines=[]
    oldLines=[]
    for line_nr in range(len(lines)):
        x1, y1 = lines[line_nr][0][0],lines[line_nr][0][1]
        x2, y2 = lines[line_nr][0][2],lines[line_nr][0][3]
        dx, dy = x2-x1, y2-y1
        lengt = np.sqrt(dx**2+dy**2) #dlugosc lini
        wx=dx/lengt #A
        wy=dy/lengt #B
        if line_nr==0:
            C=-wx * x2 - wy * y2  # Ax + By + C = 0 -> C = -(Ax + By)
            A_ = dy
            B_ = dx
            C_ = -(A_*x2+B_*y2)
            lin_prost=np.add(np.array([[x2],[y2]]), np.multiply(np.array([[A_],[B_]]),[20,0,-20]))
            print(x2,y2)
            print(lin_prost)
        war=wx*x2+wy*y2+C
        war2=wx*x1+wy*y1+C
        if war>=0 and war2>=0:
            newLines.append(lines[line_nr])
        else:
            oldLines.append(lines[line_nr])
    return newLines, oldLines, [lines[0]]

def AnalizeForCurve(image):
    image=perspectiveWarp(image)
    img_cann=canny(image)
    #gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #blurred=cv2.GaussianBlur(gray, (7, 7), 0)
    #(T, thresh)=cv2.threshold(blurred, 150, 255,
    #                          cv2.THRESH_BINARY)
    img_crop=regionOfIntrest(img_cann, 1)

    lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 30, None, minLineLength=20, maxLineGap=30) #[[[x1,y1,x2,y2]],[x1,y1,x2,y2],[x1,y1,x2,y2]]
    #for line in lines:
    #    x1,y1,x2,y2 = line[0]
    #    print(x1,y1,x2,y2)
    #    plt.plot([x1,x2],[y1,y2])
    #plt.show()
    linie(lines,80)
    plt.show()
    print('ok')
    img_avarageLinesNew, img_avarageLinesOld, analizedLine = avarageLines(image, lines) # algorytm
    image_lines2=displayLine(image, img_avarageLinesOld)
    image_lines = displayLine(image, img_avarageLinesNew,(0,255,0),(0,255,0))
    image_analizedLIne = displayLine(image, analizedLine, (255,0,0),(255,0,0))
    img_comb = cv2.addWeighted(image, 0.5, image_lines2,1,1)
    img_comb2 = cv2.addWeighted(img_comb, 1, image_lines, 1 , 1, 1)
    img_comb3 = cv2.addWeighted(img_comb2, 0.5, image_analizedLIne, 1 , 1, 1)
    return img_comb3, img_crop


img = cv2.imread('../testImg/test3.8.png')
i1, i2 = AnalizeForLines(img)
cv2.imshow("normal",i1)
cv2.imshow("normal_canny",i2)
i3, i4 = AnalizeForCurve(img)
cv2.imshow("warped",i3)
cv2.imshow("warped_canny",i4)
cv2.waitKey(0)


