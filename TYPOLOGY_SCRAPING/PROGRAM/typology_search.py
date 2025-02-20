import os
import sys
import pandas as pd
from dotenv import load_dotenv
load_dotenv(__file__.replace("typology_search.py", ".env"))

sys.path.append(os.environ.get("SCRAPING_PROGRAM_PATH"))
import search
new_suzuki_scraping = search.new_suzuki_scraping(start_hour=9, end_hour=18, sleep_time=2)
new_suzuki_scraping.scraping_setup(username="EBW0063768I", password="57110T5GN60")

target_df = pd.read_csv(os.environ.get("TARGET_DATA_PATH"), dtype=str)
if os.path.exists(os.environ.get("OUTPUT_DATA_PATH")):
    output_df = pd.read_csv(os.environ.get("OUTPUT_DATA_PATH"))
else:
    output_df = pd.DataFrame()


for idx, target_row in target_df.iterrows():
    is_scraping = target_row["is_scraping"]
    if is_scraping == "True":
        continue

    car_model_designation_no = target_row["car_model_designation_no"]
    classification_no = target_row["classification_no"]
    car_name = target_row["car_name"]
    car_model_name = target_row["car_model_name"]
    youshiki = target_row["youshiki"]
    vin_start = target_row["vin_start"]
    vin_end = target_row["vin_end"]
    model_from = target_row["model_from"]
    model_to = target_row["model_to"]
    catalog_name = target_row["catalog_name"]
    parts_code = target_row["parts_code"]

    is_success = new_suzuki_scraping.pinpoint_typology_search(
        car_model_designation_no=car_model_designation_no,
        classification_no=classification_no,
        car_name=car_name,
        car_model_name=car_model_name,
        youshiki=youshiki,
        vin_start=vin_start,
        vin_end=vin_end,
        model_from=model_from,
        model_to=model_to,
        catalog_name=catalog_name
    )
        
    new_suzuki_scraping.pinpoint_typology_search_parts(car_model_designation_no, classification_no, car_name, car_model_name, youshiki, vin_start, vin_end, model_from, model_to, catalog_name)
    result_parts_list = new_suzuki_scraping.search_parts(parts_code)
    print(result_parts_list)
