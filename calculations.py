import os
import shutil
import datetime
import time

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

if __name__ == '__main__':
    datapath = os.path.dirname(__file__)
    save_path = os.path.join(datapath, 'prices.csv')
    info_path = os.path.join(datapath, 'info')

    pricedf = pd.read_csv(save_path, index_col=0)

    section_clean_data = True
    if section_clean_data:
        week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
        pricedf['time'] = pd.to_datetime(pricedf['time'])
        pricedf['date'] = pricedf['time'].dt.strftime('%d-%m-%Y')

        pricedf['time-sig'] = pricedf['date'] + ' ' + pricedf['Hour']
        # Convert the 'datetime' column to datetime objects
        pricedf['time-sig'] = pd.to_datetime(pricedf['time-sig'], format='%d-%m-%Y %H:%M')

        first_date = pricedf['date'].iloc[0]
        pricedf = pricedf[pricedf['date'] != first_date]
        last_date = pricedf['date'].iloc[-1]
        pricedf = pricedf[pricedf['date'] != last_date]

        new_df = pricedf.groupby('time-sig')['Price'].mean().reset_index()
        new_df['date'] = new_df['time-sig'].dt.strftime('%d-%m-%Y')
        new_df['Hour'] = new_df['time-sig'].dt.strftime('%H:%M')
        new_df['day_of_week'] = new_df['time-sig'].dt.day_name()
        new_df['Hour_int'] = new_df['time-sig'].dt.hour
        new_df['Day_int'] = (new_df['time-sig'].dt.dayofweek + 2) % 7

        pricedf = new_df.copy()

        # arrange to relevant hours only
        window = [6, 12]
        window_int = list(range(window[0], window[1]))
        pricedf = pricedf[pricedf['Hour_int'].isin(window_int)]

        # arrange to relevant days only
        relevant_days = [1, 2, 3, 4, 5]
        pricedf = pricedf[pricedf['Day_int'].isin(relevant_days)]

    section_process_data = True
    if section_process_data:
        section_plot_global_average = True
        if section_plot_global_average:
            # Create global average per minute
            average_price_df = pricedf.groupby('Hour')['Price'].mean().reset_index()

            # Ensure that the 'Hour' column is in datetime format for proper sorting on the x-axis
            average_price_df['Hour'] = pd.to_datetime(average_price_df['Hour'], format='%H:%M')

            # Create the plot with larger size
            fig, ax = plt.subplots(figsize=(15, 10))

            # Create line plot
            ax.plot_date(average_price_df['Hour'], average_price_df['Price'], linestyle='solid')

            # Set the title and labels
            ax.set_title('Average Price by Hour')
            ax.set_xlabel('Hour')
            ax.set_ylabel('Average Price')

            # Set major ticks location every 15 minutes
            ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0, 60, 10)))

            # Use DateFormatter to format x-axis labels
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

            # Add a vertical line at each round hour
            min_hour = pricedf['Hour_int'].min()
            max_hour = pricedf['Hour_int'].max()
            for hour in range(min_hour, max_hour + 1):
                ax.axvline(pd.to_datetime(f'1900-01-01 {hour}:00'), color='gray', linestyle='--', alpha=0.5)

            # Rotate and align the x-axis labels for better visibility
            fig.autofmt_xdate(rotation=45)

            # Save the figure locally in high quality
            outpath = os.path.join(info_path, 'average_price_by_hour.png')
            plt.savefig(outpath, dpi=300, bbox_inches='tight')

            print("Global average per minute saved to: {}".format(outpath))

        section_plot_per_day = True
        if section_plot_per_day:
            # Define the colors for each plot
            colors = ['red', 'green', 'blue', 'yellow', 'purple']

            # Create the subplot figure
            fig, axs = plt.subplots(5, 1, figsize=(15, 30))

            # Loop over the days
            for i, day in enumerate([1, 2, 3, 4, 5]):
                # Create a new DataFrame for each day
                daily_pricedf = pricedf[pricedf['Day_int'] == day]

                # Calculate the average price for each hour
                average_price_df = daily_pricedf.groupby('Hour')['Price'].mean().reset_index()

                # Ensure that the 'Hour' column is in datetime format for proper sorting on the x-axis
                average_price_df['Hour'] = pd.to_datetime(average_price_df['Hour'], format='%H:%M')

                # Create a line plot for each day
                axs[i].plot_date(average_price_df['Hour'], average_price_df['Price'], linestyle='solid',
                                 color=colors[i])

                # Set the title and labels
                day_as_string = week_days[i - 1]
                axs[i].set_title('Average Price by Hour for Day {}'.format(day_as_string))
                axs[i].set_xlabel('Hour')
                axs[i].set_ylabel('Average Price')

                # Set major ticks location every 15 minutes
                axs[i].xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0, 60, 15)))

                # Use DateFormatter to format x-axis labels
                axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

                # Add a vertical line at each round hour
                min_hour = daily_pricedf['Hour_int'].min()
                max_hour = daily_pricedf['Hour_int'].max()
                for hour in range(min_hour, max_hour + 1):
                    axs[i].axvline(pd.to_datetime(f'1900-01-01 {hour}:00'), color='gray', linestyle='--', alpha=0.5)

            # Rotate and align the x-axis labels for better visibility
            fig.autofmt_xdate(rotation=45)

            # Save the figure locally in high quality
            outpath = os.path.join(info_path, 'average_price_by_hour_per_day.png')
            plt.savefig(outpath, dpi=300, bbox_inches='tight')

            print("Daily average per minute saved to: {}".format(outpath))
