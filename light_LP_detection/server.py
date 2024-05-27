import time

import torch
import easyocr
import numpy as np
import cv2
from PIL import ImageFont, ImageDraw, Image
import telegram_messenger

def main():
    car_m, lp_m, reader = load_model()
    # Load the cascade classifier for license plate detection
    plate_cascade = cv2.CascadeClassifier('haarcascade_license_plate_rus_16stages.xml')

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect license plates
        plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))


        # If at least one license plate is detected
        if len(plates) >= 1:
            #print('hello')
            # Perform OCR on the detected license plate
            im, text = detect(car_m, lp_m, reader, frame)
            print(text)
            #telegram_messenger.send_message(text)



        # Break the loop on 'q' key press
        if 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def load_model():
    car_m = torch.hub.load("ultralytics/yolov5", 'yolov5s', force_reload=True, skip_validation=True)
    lp_m = torch.hub.load('ultralytics/yolov5', 'custom', 'lp_det.pt')
    reader = easyocr.Reader(['en'], detect_network='craft', recog_network='best_acc',
                            user_network_directory='lp_models/user_network', model_storage_directory='lp_models/models')

    car_m.classes = [2, 3, 5, 7]
    return car_m, lp_m, reader

def detect(car_m, lp_m, reader, frame):
    fontpath = "SpoqaHanSansNeo-Light.ttf"
    font = ImageFont.truetype(fontpath, 20)

    to_draw = frame.copy()
    results = car_m(frame)
    locs = results.xyxy[0]

    result_text = []

    if len(locs) == 0:
        result = lp_m(frame)
        if len(result) == 0:
            result_text.append('검출된 차 없음')
        else:
            for rslt in result.xyxy[0]:
                x2, y2, x3, y3 = [int(item.cpu().detach().numpy()) for item in rslt[:4]]
                try:
                    extra_boxes = 0
                    cropped_im = cv2.cvtColor(cv2.resize(to_draw[y2-extra_boxes:y3+extra_boxes, x2-extra_boxes:x3+extra_boxes], (224, 128)), cv2.COLOR_BGR2GRAY)
                    text = reader.readtext(cropped_im)[0][1]
                    result_text.append(text)
                except Exception as e:
                    return cv2.resize(to_draw, (1280, 1280)), ""
                img_pil = Image.fromarray(to_draw)
                draw = ImageDraw.Draw(img_pil)
                draw.text((x2 - 10, y2 - 30), text, font=font, fill=(255, 0, 255))
                to_draw = np.array(img_pil)
                cv2.rectangle(to_draw, (x2, y2), (x3, y3), (255, 0, 255), 2)
            for i in result_text:
                print(i)
                telegram_messenger.send_attendance(i)
                time.sleep(1.5)
            return cv2.resize(to_draw, (1280, 1280)), result_text

    for idx, item in enumerate(locs):
        x, y, x1, y1 = [int(it.cpu().detach().numpy()) for it in item[:4]]
        car_im = to_draw[y:y1, x:x1, :].copy()
        result = lp_m(Image.fromarray(car_im))

        if len(result) == 0:
            result_text.append("차는 검출됬으나, 번호판이 검출되지 않음")

        for rslt in result.xyxy[0]:
            x2, y2, x3, y3 = [int(item.cpu().detach().numpy()) for item in rslt[:4]]
            try:
                extra_boxes = 0
                cropped_im = cv2.cvtColor(cv2.resize(to_draw[y + y2 - extra_boxes:y + y3 + extra_boxes, x + x2 - extra_boxes:x + x3 + extra_boxes], (224, 128)), cv2.COLOR_BGR2GRAY)
                text = reader.readtext(cropped_im)[0][1]
                result_text.append(text)
            except Exception as e:
                return cv2.resize(to_draw, (1280, 1280)), ""
            img_pil = Image.fromarray(to_draw)
            draw = ImageDraw.Draw(img_pil)
            draw.text((x + x2 - 10, y + y2 - 30), text, font=font, fill=(255, 0, 255))
            to_draw = np.array(img_pil)
            cv2.rectangle(to_draw, (x + x2, y + y2), (x + x3, y + y3), (255, 0, 255), 2)


    return cv2.resize(to_draw, (1280, 1280)), result_text




if __name__ == '__main__':
    main()
