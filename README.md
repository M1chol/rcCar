> [!NOTE]
> This project is not beeing maintained. You can visit the new version [here](https://github.com/M1chol/jetson-car).

# Remotely controlled autonomous car
I will present a detailed description of building a simple autonomous car below. The parts I used are found [here](https://github.com/M1chol/rcCar/blob/main/Inne/czesci.md). In addition to the listed components, cables and connectors will also be needed. Of course, a soldering iron will be required to assemble the whole thing. The scripts folder contains all the programs I wrote to get the car running. Please feel free to contact me if you have any additional questions.

This file is a translation from original Polish version (now README_PL.md), I am sorry for any translation errors and inaccuracies.

## 1. Assembling the car
I used a self-assembly kit for the chassis (see the parts file). Since the instruction included in the kit is very basic, you will find a modified, more detailed version [here](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy) (Instrukcja1.png and Instrukcja2.png).   
   
**Intended end result**
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/IMG_20220930_195806.jpg)
  
### A few assembly photos:
![IMG_20220727_143825](https://user-images.githubusercontent.com/106252516/184039809-f9397042-ed86-4d5f-9c24-03a827240d34.png)

The car is powered by a Lithium Polymer battery with 3 cells, which gives a voltage of about 12V after charging. To power the Arduino, Raspberry Pi, and servo, which take 5V, I used a step-down converter. In my case, it was the DFR0205, but cheaper alternatives will also be good. I used a cheap high voltage motor controller module, the BTS7960D, as the motor controller.

### Here is a simple diagram showing the main components of the car:
![Schematic_rcCar_2022-08-09](https://user-images.githubusercontent.com/106252516/183687655-5ca91baa-e46a-4876-8bab-b56d4de04d62.png)
  
### IMPORTANT INFORMATION!
In my project, I omitted two important things, so if you're planning to build a similar car, be sure to modify the schematic:

1. BMS (Battery Management System) - An important point if you're using multi-cell batteries. In my car, after a longer time, one cell has a clearly lower voltage than the others. The BMS with voltage stabilizer will solve this problem.
2. Fuse - Initially, I had plans to add a fuse on the positive battery terminal. This is a good additional protection against accidental short-circuit and uncontrolled and sudden lithium polymer oxidation :)
---

##  2: Programming
### Step 1: Remote Control
At the beginning, I made remote control using an Xbox controller. The controller is connected to a desktop computer where the sshCarController.py captures the pressed buttons (pygame library) and sends them to the Raspberry Pi over SSH (paramiko library). The RPi sends commands to Arduino over the serial port, which performs the commands (below is an easier way).
### Diagram of the connection using SSH:
![IMG](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy/ScriptsDiagram1.jpg)
  
Thanks to this connection, the control range is as far as the Wi-Fi network we are connected to. On the downside, there is a greater delay. A simpler way is to completely omit the desktop computer; I connected the controller directly to the Raspberry Pi.
  
### Diagram of direct connection:
![IMG](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Schematy/ScriptsDiagram2.jpg)
  
#### The final result of stage one:
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm.gif)
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm2.gif)
   
---
   
### Step 2: Edge Detection
### Assumptions:
1. The lanes are white lines on a black background.
2. The car is positioned correctly in the starting position; between the lanes.
3. Sharp road turns are possible.

The first step towards autonomous driving is good road lane detection. I mounted a camera on the car that is connected to the Raspberry Pi. The image streams to the Raspberry Pi's IP port using the Motion application. Then, on a computer connected to the same network, a [stream analyzing program is running](https://github.com/M1chol/rcCar/blob/main/Skrypty/LineDetectionAdvanced.py).

Below I will describe the operation of two algorithms for line detection, the first of which is great for locating on a straight (or slightly twisting) piece of lane. The second, on the other hand, I will use for analyzing turns at high angles.
### Simple edge detection:
**The intended end result**.
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm3.gif)
First of all, we find places in the photo where there is a big change in contrast using the [canny](https://pl.wikipedia.org/wiki/Canny) filter. The result is a black photo with the edges of the stripes highlighted in white. We do this to remove unnecessary information from the analyzed photo. Then we apply [Hough transforms](https://pl.wikipedia.org/wiki/Transformacja_Hougha), an algorithm that detects straight lines in the image. We divide the list of obtained lines according to the slope: straight lines with a negative direction vector the right lane, and those with a positive direction vector the left lane. From the divided lines, we extract two averages that accurately describe the two detected lanes.
### Summary of the process
1. input photo
2. Canny filter
3. line detection
4. dividing the lines relative to the slope
5. extraction of the average
### Animation:
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/lineDetecionProces.gif)

### Advanced line detection:
**The intended end result:**  
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/car.gif)  
  
First, we stretch the original image so as to remove perspective and achieve a bird's eye view. Then, as in the previous point, we filter the stretched image with the canny filter and search for lines on it. In order to get rid of the lines that were detected incorrectly and separate the individual lanes in the place where we expect to observe the beginning of the left lane, we search for the nearest detected line. In the next step we check if its distance from the expected point is within the specified range. We do the same with the right lane.  
  
**Effect on video**  
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/DrivingTestAinm5_copy.gif)
   
As you can see in the animation above, the next step after finding the beginning of the lane is to find the closest line counting from the end of the lane. We use this algorithm in a loop. Remember to change the line from which we measure the distance, and to remove previously analyzed lines from the set of all lines.  
   
**Animation of the algorithm**  
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/linedetect.gif)  
   
**Code fragment**.   
Below are the code fragments with additional comments responsible for the described algorithm    
note: code have been through translator so if you find any errors compare to the original   
   
The fragment responsible for the function call:
> lineDetection.py
```python
import lineDetectionHandleLines as Lines # reference to the algorithm file
startingPoints=[[246, 460, 246, 450], [411, 460, 411, 450]]     # task of lines from which we start searching for the first lanes
left_line = Lines.detectBirdLines(startingPoints[0], lines, 55, numberOfLines=numberOfSteps) # function call
```  
 
Main function:
> lineDetecionHandleLines.py
```python
def detectBirdLines(line_start, lines, maxDist=40, numberOfLines=0):
    """
    :param line_start: the line from which we are looking for
    :param lines: all lines
    :param maxDist: maximum line distance
    :param numberOfLines: number of steps, if 0 - to the last detected line
    :return: array of lines in one lane
    """
    detectedLines=[] # saves the found lines
    step=0 # adds the possibility to ask the maximum number of steps 
    while True if numberOfLines==0 else step<numberOfLines:                                   # if the set number of steps is 0 ignore the counter, otherwise limit the number of loops
        closestLineslist=distaceBetweenPoints(line_start, lines, True, displacement=True) # return for each line [distance, displacement on x, index (if sorting)]
        closestLine=closestLineslist[0] # assign closest line to variable
        if closestLine[0] <= maxDist:                                   # if odl less than maxDist
            chosenLine=lines[int(closestLine[2])]                           # save the lines (reference to the real line not an array of distances)
            detectedLines.append(chosenLine) # add the found line to the array
            line_start=chosenLine # overwrite the line from which we are searching
        else:                                                           # if distance greater than maximum
            return detectedLines # return the array with the detected lines
        step+=1 # increment the counter
        lines=np.delete(lines, int(closestLineslist[0][2]), 0) # remove the detected line from the array of all lines
    return detectedLines # return the array of detected lines
```
### Additional materials:
![GIF](https://github.com/M1chol/rcCar/blob/main/Zdjęcia/Budowa/car2-2.gif)

---
  
## 3. In the future
1. improve the problem of detecting the initial lane -> save the last location of detected lines and refer to them in subsequent steps
2. stable return of angle to turn
3. autonomous driving and PID
