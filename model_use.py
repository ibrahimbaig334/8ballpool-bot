# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'model_use.py'
# Bytecode version: 3.9.0beta5 (3425)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import os
import sys
import cv2
import mss
import numpy as np
import onnxruntime as ort
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath('.'), relative_path)
DETECTION_SIZE = 100
CLASSIFIER_SIZE = 25
CLASS_NAMES = ['solid', 'stripe', 'cue', 'black']
det_path = resource_path('model_ball/best.onnx')
clf_path = resource_path('model_ball/best_classifier.onnx')
_det_session = ort.InferenceSession(det_path)
_clf_session = ort.InferenceSession(clf_path)
_sct = mss.mss()
def apply_circular_mask(img, cx, cy, r):
    """Masks pixels outside the ball radius. Works on both grayscale and color."""
    h, w = img.shape[:2]
    Y, X = np.ogrid[:h, :w]
    mask = (X - cx) ** 2 + (Y - cy) ** 2 <= r ** 2
    out = np.zeros_like(img)
    out[mask] = img[mask]
    return out
def _preprocess_detector(gray_np):
    """Grayscale (H, W) uint8 → (1, 1, H, W) float32 normalized to [-1, 1]."""
    t = gray_np.astype(np.float32) / 255.0
    t = (t - 0.5) / 0.5
    return np.expand_dims(np.expand_dims(t, 0), 0)
def _preprocess_classifier(bgr_np):
    """Color BGR (H, W, 3) uint8 → (1, 3, H, W) float32 normalized to [-1, 1]."""
    t = bgr_np.astype(np.float32) / 255.0
    t = (t - 0.5) / 0.5
    return np.expand_dims(t.transpose(2, 0, 1), 0)
def detect_and_classify(mx: int, my: int, search_width: int=100):
    """\n    Detects ball with full float precision and performs tight-crop classification.\n    Returns: (rel_x_float, rel_y_float, radius_float, label, confidence)\n    """
    half_w = search_width / 2.0
    region = {'left': int(mx - half_w), 'top': int(my - half_w), 'width': search_width, 'height': search_width}
    shot = _sct.grab(region)
    frame = np.array(shot)[:, :, :3]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized_det = cv2.resize(gray, (DETECTION_SIZE, DETECTION_SIZE), interpolation=cv2.INTER_LINEAR)
    det_input = _preprocess_detector(resized_det)
    det_output = _det_session.run(None, {_det_session.get_inputs()[0].name: det_input})[0][0]
    pred = np.clip(det_output, 0.0, 1.0)
    bx_local = float(pred[0] * search_width)
    by_local = float(pred[1] * search_width)
    br = float(pred[2] * search_width)
    left = int(np.floor(bx_local - br))
    top = int(np.floor(by_local - br))
    right = int(np.ceil(bx_local + br))
    bottom = int(np.ceil(by_local + br))
    crop_color = frame[max(0, top):bottom, max(0, left):right]
    if crop_color.size == 0 or br < 3.0:
        return (bx_local - half_w, by_local - half_w, br, 'none', 0.0)
    else:
        crop_cx = bx_local - max(0, left)
        crop_cy = by_local - max(0, top)
        masked = apply_circular_mask(crop_color, crop_cx, crop_cy, br)
        diameter_f = br * 2.0
        interp = cv2.INTER_AREA if diameter_f > CLASSIFIER_SIZE else cv2.INTER_CUBIC
        resized_clf = cv2.resize(masked, (CLASSIFIER_SIZE, CLASSIFIER_SIZE), interpolation=interp)
        clf_input = _preprocess_classifier(resized_clf)
        logits = _clf_session.run(None, {_clf_session.get_inputs()[0].name: clf_input})[0]
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)
        idx = np.argmax(probs)
        return (bx_local - half_w, by_local - half_w, br, CLASS_NAMES[idx], float(probs[0][idx]))