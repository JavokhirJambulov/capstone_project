from ctypes import *
from datetime import datetime

import cv2
import sys, os, platform
import time
import telegram_messenger


def getLibPath():
  os_name = platform.system().lower()
  arch_name = platform.machine().lower()
  print('os_name=%s, arch_name=%s' % (os_name, arch_name))

  if os_name == 'windows':
    if arch_name == 'x86_64' or arch_name == 'amd64':
      return os.path.join('..', 'bin', 'windows-x86_64', 'tsanpr.dll')
    elif arch_name == 'x86':
      return os.path.join('..', 'bin', 'windows-x86', 'tsanpr.dll')
  elif os_name == 'linux':
    if arch_name == 'x86_64':
      return os.path.join('..', 'bin', 'linux-x86_64', 'libtsanpr.so')
    elif arch_name == 'aarch64':
      return os.path.join('..', 'bin', 'linux-aarch64', 'libtsanpr.so')

  print('Unsupported target platform')
  sys.exit(-1)


IMG_PATH = '../img/'
LIB_PATH = getLibPath()
print('LIB_PATH=', LIB_PATH)
lib = cdll.LoadLibrary(LIB_PATH)

"""
const char* WINAPI anpr_initialize(const char* mode); // [IN] 라이브러리 동작 방식 설정
"""
lib.anpr_initialize.argtype = c_char_p
lib.anpr_initialize.restype = c_char_p

"""
const char* WINAPI anpr_read_file(
    const char* imgFileName,      // [IN] 입력 이미지 파일명
    const char* outputFormat,     // [IN] 출력 데이터 형식
    const char* options);         // [IN] 기능 옵션
"""
lib.anpr_read_file.argtypes = (c_char_p, c_char_p, c_char_p)
lib.anpr_read_file.restype = c_char_p

"""
const char* WINAPI anpr_read_pixels(
  const unsigned char* pixels,  // [IN] 이미지 픽셀 시작 주소
  const unsigned long width,    // [IN] 이미지 가로 픽셀 수
  const unsigned long height,   // [IN] 이미지 세로 픽셀 수
  const unsigned long stride,   // [IN] 이미지 한 라인의 바이트 수
  const char* pixelFormat,      // [IN] 이미지 픽셀 형식 
  const char* outputFormat,     // [IN] 출력 데이터 형식
  const char* options);         // [IN] 기능 옵션
"""
lib.anpr_read_pixels.argtypes = (c_char_p, c_int32, c_int32, c_int32, c_char_p, c_char_p, c_char_p)
lib.anpr_read_pixels.restype = c_char_p


def initialize():
  error = lib.anpr_initialize('text')
  return error.decode('utf8') if error else error


def main():
  error = initialize()
  if error:
    print(error)
    sys.exit(1)

  capture = cv2.VideoCapture(0)
  capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
  capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
  fps = capture.get(cv2.CAP_PROP_FPS)
  delayDefault = 1000 / fps

  delay = delayDefault
  last_lp = 'Not recognized'
  count_same_lp = 0
  while cv2.waitKey(int(delay)) < 0:
      ret, frame = capture.read()
      start = time.time()
      height = frame.shape[0]
      width = frame.shape[1]
      result = lib.anpr_read_pixels(bytes(frame), width, height, 0, 'BGR'.encode('utf-8'), 'text'.encode('utf-8'), ''.encode('utf-8'))
      if len(result) > 0:

        resultnum = result.decode('utf8')
        print(resultnum)
        if last_lp == resultnum:
            count_same_lp +=1
        else:
            count_same_lp = 0

        if last_lp != resultnum:
            telegram_messenger.send_attendance(resultnum)
        last_lp = resultnum

      cv2.imshow("ANPR Demo", frame)
      spent = time.time() - start
      delay = delayDefault - spent

  capture.release()
  cv2.destroyAllWindows()


if __name__ == '__main__':
  main()
