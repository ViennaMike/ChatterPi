#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 14:01:47 2020

@author: Mike McGurrin
"""
from configparser import ConfigParser
# Initialize constants from config.ini
cfg = ConfigParser()
cfg.read('config.ini')
SERVO_MIN = int(cfg['SERVO']['SERVO_MIN'])
SERVO_MAX = int(cfg['SERVO']['SERVO_MAX'])
MIN_ANGLE = int(cfg['SERVO']['MIN_ANGLE'])
MAX_ANGLE = int(cfg['SERVO']['MAX_ANGLE'])
STYLE = int(cfg['CONTROLLER']['STYLE'])
THRESHOLD = int(cfg['CONTROLLER']['THRESHOLD'])
LEVEL1 = int(cfg['CONTROLLER']['LEVEL1'])
LEVEL2 = int(cfg['CONTROLLER']['LEVEL2'])
LEVEL3 = int(cfg['CONTROLLER']['LEVEL3'])
FIlTERED_LEVEL1 = int(cfg['CONTROLLER']['FIlTERED_LEVEL1'])
FIlTERED_LEVEL2 = int(cfg['CONTROLLER']['FIlTERED_LEVEL2'])
FIlTERED_LEVEL3 = int(cfg['CONTROLLER']['FIlTERED_LEVEL3'])
BUFFER_SIZE = int(cfg['AUDIO']['BUFFER_SIZE']) 
SOURCE = cfg['AUDIO']['SOURCE']
MIC_TIME = int(cfg['AUDIO']['MIC_TIME'])
OUTPUT_CHANNELS = cfg['AUDIO']['OUTPUT_CHANNELS']
AMBIENT = cfg['AUDIO']['AMBIENT']
PROP_TRIGGER = cfg['PROP']['PROP_TRIGGER']
EYES = cfg['PROP']['EYES']
TRIGGER_OUT = cfg['PROP']['TRIGGER_OUT']
DELAY = int(cfg['PROP']['DELAY'])
JAW_PIN = int(cfg['PINS']['JAW_PIN'])
PIR_PIN = int(cfg['PINS']['PIR_PIN'])
EYES_PIN = int(cfg['PINS']['EYES_PIN'])
TRIGGER_OUT_PIN = int(cfg['PINS']['TRIGGER_OUT_PIN'])
