#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:14:07 2018

@author: jeff
"""

class historian(object):
    
    def __init__(self):
        self._log = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        return
    
    def log(self,data):
        self._log.append(data)
        
        