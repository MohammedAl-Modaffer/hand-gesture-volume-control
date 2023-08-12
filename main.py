import cv2
import mediapipe as mp
import comtypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class HandDetector:
    def __init__(self, mode=False, max_hands=2, model_complexity=1, detection_confidence=0.5, track_confidence=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.model_complexity = model_complexity
        self.detection_confidence = detection_confidence
        self.track_confidence = track_confidence
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, self.model_complexity, self.detection_confidence,
                                         self.track_confidence)
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, hand_number=0, draw=True):
        lm_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_number]
            for id_index, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id_index, cx, cy])
        return lm_list


TIP_IDS = [4, 8, 12, 16, 20]


def main():
    cap = cv2.VideoCapture(0)
    w_cam, h_cam = 640, 480
    cap.set(3, w_cam)
    cap.set(4, h_cam)
    detector = HandDetector()

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)

    while True:
        success, img = cap.read()
        img = detector.find_hands(img)
        lm_list = detector.find_positions(img, draw=False)
        if len(lm_list) != 0:
            finger_count = []
            # Thumb
            if lm_list[TIP_IDS[0]][1] > lm_list[TIP_IDS[0] - 1][1]:
                finger_count.append(1)
            else:
                finger_count.append(0)
            # 4 fingers
            for i in range(1, 5):
                if lm_list[TIP_IDS[i]][2] < lm_list[TIP_IDS[i] - 2][2]:
                    finger_count.append(1)
                else:
                    finger_count.append(0)
            # setting volume value.
            level = finger_count.count(1)
            level = (level / 10) * 2
            print(level)
            volume.SetMasterVolumeLevelScalar(level, None)

            cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, str(level), (45, 375), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 8)
            cv2.putText(img, "volume level", (34, 275), cv2.FONT_HERSHEY_PLAIN, 1.3, (255, 0, 0), 2)

        cv2.imshow('frame', img)  # display the frame, the 'frame' is the title, the img is the frame from
        # device
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
