import base64
import pandas as pd
from matdata.converter import csv2df, read_zip#, load_from_tsfile, xes2df
from matdata.converter import xes2df
from matdata.inc.ts_io import load_from_tsfile
import matdata
import io
from matdata.preprocess import readDataset, organizeFrame
import dash_bootstrap_components as dbc
import datetime
from matmodel.util.parsers import df2trajectory
from matmodel.util.parsers import json2movelet
from flask import Flask, session
import threading
import uuid


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    # DECODE DATAFRAME:
    decoded = base64.b64decode(content_string)
    try:
        ext = filename.split('.')[-1].lower()
        if ext in ['csv', 'zip', 'mat', 'ts']:

            df = pd.DataFrame()
            if ext == 'csv':
#                from matdata.converter import csv2df
                decoded = io.StringIO(decoded.decode('utf-8'))
                df = csv2df(decoded, missing='?')
            elif ext == 'zip':
#                from matdata.converter import read_zip
                from zipfile import ZipFile
                decoded = io.BytesIO(decoded)
                df = read_zip(ZipFile(decoded, "r"))
#             elif ext == 'mat':
# #                from matdata.converter import read_mat
#                 decoded = io.StringIO(decoded.decode('utf-8'))
#                 df = read_mat(decoded, missing='?')
            elif ext == 'ts':
#                from matdata.inc.ts_io import load_from_tsfile
                decoded = io.StringIO(decoded.decode('utf-8'))
                df = load_from_tsfile(decoded, replace_missing_vals_with="?")
            elif ext == 'xes':
#                from matdata.converter import xes2df
                decoded = io.StringIO(decoded.decode('utf-8'))
                df = xes2df(decoded, missing='?')

            df.columns = df.columns.astype(str)

            df, columns_order_zip, columns_order_csv = organizeFrame(df)
            update_trajectories(df[columns_order_csv])
        elif ext == 'json':
            update_movelets(io.BytesIO(decoded))
        else:
            return dbc.Alert("This file format is not accepted.", color="warning", style = {'margin':'1rem'})
    except Exception as e:
        raise e
        print(e)
        return dbc.Alert("There was an error processing this file.", color="danger", style = {'margin':'1rem'})

    return dbc.Alert("File "+filename+" loaded ("+str(datetime.datetime.fromtimestamp(date))+").", color="info", style = {'margin':'1rem'})

def update_trajectories(df):
    # TRANSFORM TRAJECTORIES:
    ls_tids        = set(gess('ls_tids', []))
    ls_trajs       = gess('ls_trajs', [])
    
    ls_aux, _ = df2trajectory(df)
    #for T in ls_aux:
    def processT(T):
        nonlocal ls_tids, ls_trajs
        if T.tid not in ls_tids:
            ls_tids.add(T.tid)
            ls_trajs.append(T)
            
    list(map(lambda T: processT(T), ls_aux))
            
    sess('ls_tids', list(ls_tids))
    sess('ls_trajs', ls_trajs)
            
def update_movelets(data):
    # TRANSFORM Movelets:
    ls_movs       = gess('ls_movs', [])
    
    ls_aux = json2movelet(data, load_distances=True)
    
    ls_movs = ls_movs + ls_aux 
        
    sess('ls_movs', ls_movs)



def gu():
    global SESS_USERS
    if 'user' not in session or session['user'] not in SESS_USERS:
        U = SelfDestUser()
        session['user'] = U.UID
        
    return session['user']

def sess(key, val):
    global SESS_USERS
    SESS_USERS[gu()].sev(key, val)

def gess(key, default=None):
    global SESS_USERS
    return SESS_USERS[gu()].gev(key, default)


class SelfDestUser:
    def __init__(self):
        self.UID = uuid.uuid4()
        self.data = dict()
        
        global SESS_USERS
        SESS_USERS[self.UID] = self

        self.start()

    def start(self):
        self.TTL = threading.Timer(30 * 60, self.__del__)
        self.TTL.start()

    def keep(self):
        self.TTL.cancel()
        self.start()
    
    def __del__(self):
        global SESS_USERS
        del SESS_USERS[self.UID]
        del self
      
    def sev(self, key, val):
        self.keep()
        self.data[key] = val

    def gev(self, key, default=None):
        self.keep()
        if key in self.data:
            return self.data[key]
        else:
            return default
        
        
        
        