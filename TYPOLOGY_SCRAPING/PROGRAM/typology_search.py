import os
import sys
import pandas as pd
from dotenv import load_dotenv
load_dotenv(__file__.replace("typology_search.py", ".env"))

def split_parts_code(parts_code, split_num):
    tmp_list = parts_code.split(" ")

    tmp_list_2 = []
    for i in range(split_num):
        if i < split_num-1:
            tmp_list_2.append(" ".join(tmp_list[int(len(tmp_list)/split_num)*i:int(len(tmp_list)/split_num)*(i+1)]))
        else:
            tmp_list_2.append(" ".join(tmp_list[int(len(tmp_list)/split_num)*i:]))
    
    return tmp_list_2

def no_data_handling(str):
    if str == "no_data":
        return ""
    else:
        return str

sys.path.append(os.environ.get("SCRAPING_PROGRAM_PATH"))
import search
new_suzuki_scraping = search.new_suzuki_scraping(start_hour=9, end_hour=21, sleep_time=2)
new_suzuki_scraping.scraping_setup(username="EBW0063768I", password="57110T5GN60")

target_df = pd.read_csv(os.environ.get("TARGET_DATA_PATH"), dtype=str)
if os.path.exists(os.environ.get("OUTPUT_DATA_PATH")):
    output_df = pd.read_csv(os.environ.get("OUTPUT_DATA_PATH"))
else:
    output_df = pd.DataFrame()


for idx, target_row in target_df.iterrows():
    is_scraping = target_row["is_scraping"]
    if is_scraping == "True" or is_scraping == "Over":
        continue

    car_model_designation_no = no_data_handling(target_row["car_model_designation_no"])
    classification_no = no_data_handling(target_row["classification_no"])
    car_name = no_data_handling(target_row["car_name"])
    car_model_name = no_data_handling(target_row["car_model_name"])
    youshiki = no_data_handling(target_row["youshiki"])
    vin_start = no_data_handling(target_row["vin_start"])
    vin_end = no_data_handling(target_row["vin_end"])
    model_from = no_data_handling(target_row["model_from"])
    model_to = no_data_handling(target_row["model_to"])
    catalog_name = no_data_handling(target_row["catalog_name"])
    parts_code = no_data_handling(target_row["parts_code"])

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
    
    # ヒットが100件以上の場合はparts_codeを修正する
    result_parts_list = new_suzuki_scraping.search_parts(parts_code, read_tokki=False)
    if not result_parts_list == "over":
        new_suzuki_scraping.open_detail_car_page()
        new_suzuki_scraping.click_clear_btn()

        tmp_df = pd.DataFrame.from_dict(result_parts_list)
        
        output_df = pd.concat([output_df, tmp_df], axis=0)
        output_df.to_csv(os.environ.get("OUTPUT_DATA_PATH"), index=False)

        target_df.loc[idx, "is_scraping"] = "True"
        target_df.to_csv(os.environ.get("TARGET_DATA_PATH"), index=False)
    else:
        new_suzuki_scraping.open_detail_car_page()
        new_suzuki_scraping.click_clear_btn()

        target_df.loc[idx, "is_scraping"] = "Over"
        target_df.to_csv(os.environ.get("TARGET_DATA_PATH"), index=False)
