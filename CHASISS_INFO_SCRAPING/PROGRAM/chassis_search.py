import os
import sys
import pandas as pd
from dotenv import load_dotenv
load_dotenv(__file__.replace("chassis_search.py", ".env"))

sys.path.append(os.environ.get("SCRAPING_PROGRAM_PATH"))
import search
new_suzuki_scraping = search.new_suzuki_scraping(start_hour=9, end_hour=18, sleep_time=2)
new_suzuki_scraping.scraping_setup()

target_df = pd.read_csv(os.environ.get("TARGET_DATA_PATH") + "/target.csv", dtype=str)
for idx, target_row in target_df.iterrows():
    car_model_name = target_row["car_model_name"]
    chassis_no = target_row["chassis_no"]

    print(car_model_name, chassis_no)
    is_success, car_data_list = new_suzuki_scraping.chassis_num_serch(car_model_name, chassis_no)
    
    if is_success:
        print(car_data_list)
    else:
        print("No data")
