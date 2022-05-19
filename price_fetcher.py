import os
import shutil
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import time

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def crawl():
    ret = dict()
    ret['ERR'] = None
    d = datetime.now()
    ret['time'] = d
    ret['Day'] = d.strftime('%A')
    ret['Hour'] = d.strftime('%H:%M')
    ret['Price'] = None

    try:
        url = r'https://fastlane.co.il/'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        mydivs = soup.find_all("span", {"class": "price"})
        if len(mydivs) == 1:
            c_div = mydivs[0]
            price = float(c_div.text)
            ret['Price'] = price
        else:
            raise Exception("mydivs is invalid")
    except Exception as e:
        ret['ERR'] = e
        return ret
    return ret


def clear_folder(path, clear_if_exist=True):
    if os.path.exists(path) and clear_if_exist:
        all_items_to_remove = [os.path.join(path, f) for f in os.listdir(path)]
        for item_to_remove in all_items_to_remove:
            if os.path.exists(item_to_remove) and not os.path.isdir(item_to_remove):
                os.remove(item_to_remove)
            else:
                shutil.rmtree(item_to_remove)

    if not os.path.exists(path):
        os.makedirs(path, mode=0o777)
    time.sleep(0.1)


if __name__ == '__main__':
    datapath = os.path.dirname(__file__)
    save_path = os.path.join(datapath, 'prices.csv')
    info_path = os.path.join(datapath, 'info')

    section_crawl = False
    if section_crawl:
        sample_rate = 1
        sample_days = 21
        save_rate = 60  # Every 60 seconds

        hits = int((sample_days * 24 * 60 * 60) / float(sample_rate))

        cols = ['time', 'Day', 'Hour', 'Price', 'ERR']
        df = pd.DataFrame(columns=cols)
        curr_idx = 0
        if os.path.exists(save_path):
            df = pd.read_csv(save_path, index_col=0)
            curr_idx = df.index[-1] + 1

        time_start_time = datetime.now()
        for i in tqdm(range(hits)):
            q = crawl()
            df.loc[curr_idx] = q

            time_passed = (datetime.now() - time_start_time).total_seconds()
            if time_passed > save_rate:
                time_start_time = datetime.now()
                df.to_csv(save_path)
                print(f'File saved. Path: {save_path}\tItems: {df.shape[0]}')

            time.sleep(sample_rate)

    section_process = True
    if section_process:
        clear_folder(info_path)
        hours = [6, 12]

        df = pd.read_csv(save_path)
        df['Date'] = pd.to_datetime(df['time']).dt.date
        datacols = list()
        sumdf = None
        for c_date in df['Date'].unique():
            ddf = df[df['Date'].eq(c_date)]
            ddf = ddf[ddf['ERR'].isna()]
            if len(ddf['Price'].unique()) <= 1:
                continue
            else:
                print(f"For date [{c_date}], {len(ddf['Price'].unique())} prices found.")
            ddf['time'] = pd.to_datetime(ddf['time'])
            sig = ddf.iloc[0]['time'].strftime('%b-%d-%Y-%A')
            hr = ddf['Hour'].str.split(':', expand=True).astype(int)
            ddf = ddf[(hr[0] >= hours[0]) & (hr[0] <= hours[1])]

            xdf = ddf.groupby('Hour')['Price'].mean()
            if sumdf is None:
                sumdf = pd.DataFrame(index=xdf.index.values, columns=['time', sig], dtype='object')
                sumdf['time'] = xdf.index
                sumdf[sig] = xdf.values
            else:
                idx_missing_in_sumdf = [t for t in xdf.index.to_list() if t not in sumdf.index.to_list()]
                idx_missing_in_xdf = [t for t in sumdf.index.to_list() if t not in xdf.index.to_list()]
                common = [t for t in sumdf.index.to_list() if t in xdf.index.to_list()]

                sumdf.loc[common, sig] = xdf.loc[common]
                for tidx in idx_missing_in_sumdf:
                    sumdf.loc[tidx, sig] = xdf.loc[tidx]

            csv_path = os.path.join(info_path, f'{sig}.csv')
            datacols += [sig]
            ddf.to_csv(csv_path)
            print(f"Export: {csv_path}")

        csv_path = os.path.join(info_path, f'summary.csv')
        sumdf.to_csv(csv_path)

        section_aggregate = True
        if section_aggregate:
            smooth = sumdf[datacols].rolling(3).mean().ffill().bfill()
            smoothavg = smooth.mean(axis=1)
            csv_path = os.path.join(info_path, f'averaged.csv')
            img_path = os.path.join(info_path, f'averaged.png')
            smoothavg.to_csv(csv_path, header='Price')

            plt.plot(smoothavg)
            plt.savefig(img_path)
            plt.close('all')

        print(f"Summary: {csv_path}")


def get_weather()