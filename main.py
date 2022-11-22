import cv2
import mediapipe as mp
import time
from pynput.keyboard import Key, Controller

cap = cv2.VideoCapture(0)
x, y = 1024, 768
cap.set(cv2.CAP_PROP_FRAME_WIDTH, x)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, y)
mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils
hands = mpHands.Hands(min_detection_confidence=0.7)
ptime = 0
newTime = 0
timer = 0
counting = False
cooldown = 0
direction = "none"
keyboard = Controller()



def findPosition(results, img, handNo=0, draw=False):
    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            # print(id, lm)
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            # print(id, cx, cy)
            lmList.append([id, cx, cy])
            if draw:
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

    return lmList


while cap.isOpened():
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # update time and counter
    newTime = time.time()
    if counting:
        timer += newTime - ptime

    fps = 1 / (newTime - ptime)
    ptime = newTime
    img.flags.writeable = False
    results = hands.process(imgRGB)
    img.flags.writeable = True
    # get hand landmarks
    lmList = findPosition(results, img)
    cv2.line(img, (300, 0), (300, 728), (255, 0, 255), thickness=2)
    cv2.line(img, (x-400, 0), (x-400, 728), (255, 0, 255), thickness=2)
    #if cooldown:
    cv2.putText(img, f'timer: {int(timer)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX,1.5, (0, 255, 0), 2)
    cv2.putText(img, f'cooldown: {int(cooldown)}', (20, 150), cv2.FONT_HERSHEY_SIMPLEX,1.5, (0, 255, 0), 2)

    # check landmarks of fingers
    if len(lmList) != 0:
        cv2.circle(img, (lmList[8][1], lmList[8][2]), 15, (255, 0, 255), cv2.FILLED)
        # trigger to right
        if (lmList[8][1] < 300 or lmList[12][1] < 300 or lmList[16][1] < 300 or lmList[20][1] < 300) and cooldown == 0 and direction == "none":
            counting = True
            timer = 0
            direction = "right"

        # trigger to left
        if (lmList[8][1] > x-400 or lmList[16][1] > x-400 or lmList[20][1] > x-400 or lmList[12][1] > x-400) and cooldown == 0 and direction == "none":
            counting = True
            timer = 0
            direction = "left"

        # check if swipped right
        if (lmList[8][1] > x-400 or lmList[16][1] > x-400 or lmList[20][1] > x-400 or lmList[12][1] > x-400) and timer < 2 and direction == "right":
            print("Swipped right")
            keyboard.press(Key.left)
            keyboard.release(Key.left)
            cooldown = 50
            timer = 0
            direction = "none"

        # check if swipped left
        if (lmList[8][1] < 300 or lmList[12][1] < 300 or lmList[16][1] < 300 or lmList[20][1] < 300) and timer < 2 and direction == "left":
                print("Swipped left")
                keyboard.press(Key.right)
                keyboard.release(Key.right)
                timer = 0
                cooldown = 50
                direction = "none"

    # draw hands
    if results.multi_hand_landmarks:
        for hand_landmark in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, hand_landmark, mpHands.HAND_CONNECTIONS)
            # print(hand_landmark)

    cv2.imshow("Image", img)

    # ================ timer reset of 2 seconds ===================
    if timer >= 2:
        timer = 0
        counting = False
        direction = "none"
    # =================== cooldown timer ==================
    if cooldown > 0:
        cooldown = cooldown - 1
    # loop delay
    cv2.waitKey(1)
