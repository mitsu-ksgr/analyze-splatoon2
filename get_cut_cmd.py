import argparse
from datetime import datetime, timedelta
import os
import pdb
import time

import cv2
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('movie_path')
parser.add_argument('output_dir')
parser.add_argument('--game_duration_thr', type=int, default=50,
                    help='minimum seconds regard as one game')
args = parser.parse_args()

os.makedirs(args.output_dir, exist_ok=True)

video = cv2.VideoCapture(args.movie_path)
num_frame = video.get(cv2.CAP_PROP_FRAME_COUNT)
fps = video.get(cv2.CAP_PROP_FPS)

bkout_frames = []
was_bkout = False

while video.isOpened():
    ret, frame = video.read()
    if not ret:
        break

    is_bkout = np.all(frame[50:600, 50:600, :] == 0)
    if is_bkout:
        bkout_frames.append(0)
        was_bkout = True
    else:
        if was_bkout:
            bkout_frames.append(1)
        else:
            bkout_frames.append(0)
        was_bkout = False
video.release()

bkout_frames = np.array(bkout_frames)
bkout_sec = np.where(bkout_frames==1)[0] / fps

games = []
for i in range(len(bkout_sec) - 1):
    diff = bkout_sec[i+1] - bkout_sec[i]
    if diff > args.game_duration_thr:
        games.append([bkout_sec[i], diff])

margin_sec = len(bkout_frames) / fps - bkout_sec[-1]
if margin_sec > args.game_duration_thr and margin_sec < 400:
    games.append([bkout_sec[-1], margin_sec])

for game in games:
    ss = round(int(game[0]))
    duration = round(int(game[1]))

    # output as csv
    print('{},{}'.format(ss, duration))

