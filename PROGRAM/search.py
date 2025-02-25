import sys
import time
import datetime
import traceback
import asyncio

import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By

class new_suzuki_scraping:
    def __init__(self, start_hour, end_hour, sleep_time):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.sleep_time = sleep_time
    
    # ドライバーをセットする
    def set_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-notifications')

        return webdriver.Chrome(options=chrome_options)

    # ドライバーを閉じる
    def release_driver(self):
        try:
            self.driver.quit()        
            self.driver = None
        except:
            pass

    # 特定の画像を探す
    def is_exist_img(self, img_path):
        for i in range(10):
            if pyautogui.locateOnScreen(img_path) is not None:
                return True
            time.sleep(1)
        
        return False
    
    # ログイン画面に遷移するURLを叩く
    async def execute_login_url(self):
        await asyncio.to_thread(self.driver.get, "https://stn.suzuki.co.jp/sios/menu/SLMA_Menu.jsp")

    # 認証突破
    async def pass_auth_window(self):
        if self.is_exist_img(__file__.replace("search.py", "image/dialog_img.png")):
            pyautogui.press("\t")
            pyautogui.press("\t")
            pyautogui.press("\n")
        else:
            raise Exception("ログイン画面が開けませんでした")
    
    # ログイン画面に遷移
    async def get_login_page(self):
        # ログイン画面に遷移するURLを叩くと認証画面が出てしまい、getメソッドが終了しなくなるため別スレッドで実行させてパスする
        await asyncio.gather(self.execute_login_url(), self.pass_auth_window())

    # ログイン処理
    def login(self, username, password):
        pyautogui.hotkey('win', 'd')
        time.sleep(self.sleep_time)

        self.driver = self.set_driver()
        time.sleep(self.sleep_time)

        asyncio.run(self.get_login_page())
        time.sleep(self.sleep_time)

        username_field = self.driver.find_element(By.XPATH, "//input[@type='text']")
        username_field.send_keys(username)

        password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
        password_field.send_keys(password)

        time.sleep(self.sleep_time)

        submit_btn = self.driver.find_element(By.XPATH, "//input[@type='submit']")
        submit_btn.click()

        time.sleep(self.sleep_time)

    # 部品発注ページに遷移
    def move_parts_order_page(self):
        parts_btn = self.driver.find_element(By.XPATH, "//img[@src='img/EPC.jpg']")
        parts_btn.click()
        time.sleep(self.sleep_time)

        if self.change_handle("SUZUKI_SIOS001 車台番号検索"):
            return True
        else:
            return False

    # 適当な車体番号を入力して車種情報タブに移動
    def move_car_info_page(self):
        vehicle_no_form = self.driver.find_element(By.XPATH, "//input[@id='tmpExportVin']")
        vehicle_no_form.send_keys(f"HA24S-100156")
        time.sleep(self.sleep_time)
        
        self.driver.execute_script("nextData()")
        time.sleep(self.sleep_time)

        if self.change_handle("SUZUKI_SIOS010 メイン"):
            return True
        else:
            return False

    # 車種詳細情報ページを開く
    def open_detail_car_page(self):
        self.driver.find_element(By.ID, "btn_detail").click()
        time.sleep(self.sleep_time)

        detail_iframe = self.driver.find_element(By.XPATH, "//iframe[@id='epc_floating_window_content_1']")
        self.driver.switch_to.frame(detail_iframe)
        time.sleep(self.sleep_time)

    # 車種詳細情報で車体番号を入力
    def input_chassis_num(self, car_model_name, chassis_num):
        veicle_no_form = self.driver.find_element(By.XPATH, "//input[@id='exportVin']")
        veicle_no_form.send_keys(f"{car_model_name}-{chassis_num}")
        time.sleep(self.sleep_time)

    # 車種詳細情報で型式指定番号・類別区分番号を入力
    def input_model_classification_num(self, car_model_designation_no, classification_num):
        car_model_field = self.driver.find_element(By.ID, "katashikiNo")
        car_model_field.send_keys(car_model_designation_no)
        time.sleep(0.5)
        classification_num_field = self.driver.find_element(By.ID, "rubetKubun")
        classification_num_field.send_keys(classification_num)

    # 車種詳細情報で確定ボタンをクリック
    def click_confirm_btn(self):
        confirm_btn = self.driver.find_element(By.XPATH, "//input[@id='decisioner']")
        confirm_btn.click()
        time.sleep(self.sleep_time)

        self.driver.switch_to.parent_frame()
        time.sleep(self.sleep_time)
    
    # 車種詳細情報で車種情報クリアボタンをクリック
    def click_clear_btn(self):
        clear_btn = self.driver.find_element(By.XPATH, "//input[@id='clearer']")
        clear_btn.click()
        time.sleep(self.sleep_time)

        self.driver.switch_to.parent_frame()
        time.sleep(self.sleep_time)

    # 車種詳細情報の情報を取得
    def get_car_data_list(self):
        car_data_list = {}
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        
        # 基本情報テーブルと追加情報テーブルをそれぞれ定義
        normal_info_table = tables[1]
        extra_info_table = tables[2]

        # 基本情報を取得
        before_text = ""
        for td in normal_info_table.find_elements(By.TAG_NAME, "td"):
            # td属性のtextによって処理を分ける
            if td.text == "":
                value = td.find_elements(By.TAG_NAME, "input")[-1].get_attribute("value")
                if before_text == "車台番号":
                    car_data_list[before_text] = value
                elif before_text == "型式類別":
                    if not "型式指定番号" in car_data_list.keys():
                        car_data_list["型式指定番号"] = value
                    else:
                        car_data_list["類型区分番号"] = value
                else:
                    car_data_list[before_text] = value
            else:
                before_text = td.text
        
        # 追加情報を取得
        before_text = ""
        for td in extra_info_table.find_elements(By.TAG_NAME, "td"):
            inputs = td.find_elements(By.TAG_NAME, "input")
            value = "/".join([input.get_attribute("value") for input in inputs])
            # td属性内にタグ「a」を持つかどうかでkey,valueを分ける
            if len(td.find_elements(By.TAG_NAME, "a")) > 0:
                before_text = value
            else:
                car_data_list[before_text] = value
            # inputのvalue値を持たない場合は終了
            if value == "":
                break
        
        return car_data_list

    # 車種詳細情報を閉じる
    def close_detail_car_page(self):
        close_btn = self.driver.find_element(By.XPATH, "//input[@id='closeWin']")
        close_btn.click()
        time.sleep(self.sleep_time)

        self.driver.switch_to.parent_frame()
        time.sleep(self.sleep_time)
    
    # 収録車種一覧ページの情報を取得
    def get_record_car_data_list(self):
        car_data_list = {"車名": [], "型式": [], "様式": [], "始号機": [], "終号機": [], "開始年月": [], "終了年月": [], "カタログ機種": []}

        table = self.driver.find_element(By.ID, "div004Items")
        for row in table.find_elements(By.ID, "tblRow"):
            cells = row.find_elements(By.TAG_NAME, "td")
            car_data_list["車名"].append(cells[0].text)
            car_data_list["型式"].append(cells[1].text)
            car_data_list["様式"].append(cells[2].text)
            car_data_list["始号機"].append(cells[3].text)
            car_data_list["終号機"].append(cells[4].text)
            car_data_list["開始年月"].append(cells[5].text)
            car_data_list["終了年月"].append(cells[6].text)
            car_data_list["カタログ機種"].append(cells[7].text)
        
        return car_data_list

    # 収録車種一覧ページの特定の車種をクリック
    def click_car_list_row(self, target_row_num):
        table = self.driver.find_element(By.ID, "div004Items")
        row = table.find_elements(By.ID, "tblRow")[target_row_num]
        row.click()
        time.sleep(self.sleep_time)
    
    # 収録車種一覧ページの次へをクリック
    def click_car_list_next_btn(self):
        next_btn = self.driver.find_element(By.CLASS_NAME, "cmButton5")
        next_btn.click()
        time.sleep(self.sleep_time)

    # 補助番号選択ページの情報を取得
    def get_auxiliary_num_list(self):
        table = self.driver.find_element(By.TAG_NAME, "table")

        # 補助番号選択のテーブルのヘッダー情報を取得
        trs = table.find_elements(By.TAG_NAME, "tr")
        headers = [td.get_attribute("value") for td in trs[0].find_elements(By.TAG_NAME, "td")[1:] if td.get_attribute("value") != ""]
        headers = ["補助記号"] + headers
        
        # 補助番号選択のテーブルのデータ情報を取得
        auxiliary_num_list = {key: [] for key in headers}
        for tr in trs[1:]:
            for idx, header in enumerate(headers):
                auxiliary_num_list[header].append(tr.find_elements(By.TAG_NAME, "td")[idx].get_attribute("value"))

        return auxiliary_num_list

    # 補助番号選択ページの特定の補助番号をクリック
    def click_auxiliary_num_list_row(self, target_row_num):
        table = self.driver.find_element(By.TAG_NAME, "table")
        row = table.find_elements(By.TAG_NAME, "tr")[target_row_num]
        row.click()
        time.sleep(self.sleep_time)
    
    # 補助番号選択ページの次へをクリック
    def click_auxiliary_num_list_next_btn(self):
        next_btn = self.driver.find_element(By.ID, "nexter")
        next_btn.click()
        time.sleep(self.sleep_time)

        if self.change_handle("SUZUKI_SIOS010 メイン"):
            return True
        else:
            return False
    
    # 補助番号選択ページの選択しないをクリック
    def click_auxiliary_num_list_no_select_btn(self):
        no_select_btn = self.driver.find_element(By.ID, "notSelecter")
        no_select_btn.click()
        time.sleep(self.sleep_time)

        if self.change_handle("SUZUKI_SIOS010 メイン"):
            return True
        else:
            return False
        
    # 部品番号を入力
    def input_parts_num(self, parts_code):
        parts_num_form = self.driver.find_element(By.XPATH, '//*[@id="inPartNo"]')
        parts_num_form.send_keys(parts_code)
        time.sleep(self.sleep_time)
    
    # 部品検索を行う
    def execute_add_parts(self):
        self.driver.execute_script("addParts()")
        time.sleep(self.sleep_time)
    
    # 部品検索結果を取得
    def get_result_parts_list(self, read_tokki=True):
        table = self.driver.find_element(By.ID, "tblSios010")
        trs = table.find_elements(By.CLASS_NAME, "TitleCellA")
        if read_tokki:
            result_dic = {"品番":[], "統一先品番":[], "FIGNo":[], "FIGSai":[], "Ref":[], "品名":[], "希望小売価格":[], "互換":[], "採用年式":[], "廃止年式":[], "適合スペック":[], "特記事項":[], "規格":[], "切替コード":[], "様式":[], "始号機":[], "終号機":[]}
        else:
            result_dic = {"品番":[], "統一先品番":[], "FIGNo":[], "FIGSai":[], "Ref":[], "品名":[], "希望小売価格":[], "互換":[]}
        keys = {"partNo":"品番", "generalPtsNo":"統一先品番", "figNo":"FIGNo", "figSai":"FIGSai", "refNo":"Ref", "partNm":"品名", "price":"希望小売価格", "compatiCd":"互換"}
        tokki_keys = {"saiyoYm":"採用年式", "haishiYm":"廃止年式", "tekiyouSpec":"適合スペック", "tokki":"特記事項", "kikakuSunpo":"規格", "kirikaeCd":"切替コード", "vintypeCd":"様式", "vinnoSta":"始号機", "vinnoEnd":"終号機"}

        for tr in trs:
            for key in keys.keys():
                obj = tr.find_element(By.ID, key)
                if key in ["partNo", "partNm"]:
                    result_dic[keys[key]].append(obj.get_attribute("value"))
                elif key in ["generalPtsNo", "figNo", "figSai", "refNo", "price", "compatiCd"]:
                    result_dic[keys[key]].append(obj.text)

            if read_tokki:
                # 特記事項を開いてデータを取得
                if len(tr.find_elements(By.ID, "tokkiIcon"))>0:
                    tr.find_element(By.ID, "tokkiIcon").click()
                    time.sleep(1)

                    self.change_handle("SUZUKI_SIOS040　部品特記")
                    
                    time.sleep(1)
                    for tokki_key in tokki_keys:
                        if tokki_key in ["kirikaeCd", "vintypeCd", "vinnoSta", "vinnoEnd"]:
                            if len(self.driver.find_elements(By.ID, tokki_key))>0:
                                elements = self.driver.find_elements(By.ID, tokki_key)
                                result_dic[tokki_keys[tokki_key]].append([element.text for element in elements])
                            else:
                                result_dic[tokki_keys[tokki_key]].append([])
                        elif tokki_key in ["tokki"]:
                            result_dic[tokki_keys[tokki_key]].append(self.driver.find_elements(By.ID, tokki_key)[-1].text)
                        else:
                            result_dic[tokki_keys[tokki_key]].append(self.driver.find_element(By.ID, tokki_key).text)
                    self.driver.find_element(By.CLASS_NAME, "cmButton5").click()     
                    time.sleep(1)
                    self.change_handle("SUZUKI_SIOS010 メイン")
                else:
                    for tokki_key in tokki_keys:
                        if tokki_key in ["kirikaeCd", "vintypeCd", "vinnoSta", "vinnoEnd"]:
                            result_dic[tokki_keys[tokki_key]].append([])
                        else:
                            result_dic[tokki_keys[tokki_key]].append("")
        
        return result_dic

    # 部品結果をクリア
    def click_result_clear_btn(self):
        self.driver.find_element(By.ID, "btn_all_delete").click()
        time.sleep(self.sleep_time)

        aleart_message = self.close_alert()
        if "全て削除" in aleart_message:
            time.sleep(self.sleep_time)
        elif aleart_message == "":
            pass
        else:
            raise Exception("Unknown Aleart Message")

    # エラーメッセージを取得
    def get_error_message(self):
        etype, value, tb = sys.exc_info()
        error_message = "".join(traceback.format_exception(etype, value, tb))

        return error_message

    # アラートを消す
    def close_alert(self):
        try:
            alert_message = self.driver.switch_to.alert.text
            self.driver.switch_to.alert.accept()
            
            return alert_message
        except Exception as e:
            return ""

    # 開かれているページの中で指定したページにハンドルを切り替える
    def change_handle(self, title):
        current_handles = self.driver.window_handles
        current_handles.reverse()

        for current_handle in current_handles:
            self.driver.switch_to.window(current_handle)
            time.sleep(0.2)

            if self.driver.title == title:
                return True
        
        return False

    # Webサイトの開いている時間内かを調べる
    def is_in_time(self):
        now = datetime.datetime.now()
        if not (self.start_hour <= now.hour and now.hour < self.end_hour):
            raise TimeOverError()

    # 車種情報ページまで遷移
    def scraping_setup(self, username, password):
        self.is_in_time()
        
        self.login(username, password)
        self.move_parts_order_page()
        self.move_car_info_page()
        self.open_detail_car_page()
        self.click_clear_btn()

    # 車体番号を検索する
    def chassis_num_serch(self, model, chassis_num, add_char="", tokusou=False):
        self.is_in_time()

        # alertを管理するためのtry-except文
        try:
            if not tokusou:
                self.open_detail_car_page()
                self.input_chassis_num(model, chassis_num)
                self.click_confirm_btn()
            
            self.open_detail_car_page()
            car_data_list = self.get_car_data_list()
            self.click_clear_btn()

            return car_data_list
        except Exception as e:
            error_message = self.get_error_message()

            for _ in range(10):
                # アラート画面を消す
                alert_message = self.close_alert()
                
                # 特装車に関するアラートは消したのち情報を取得する
                if "特装車" in alert_message:
                    self.driver.switch_to.parent_frame()
                    time.sleep(self.sleep_time)
                    
                    car_data_list = self.chassis_num_serch(model, chassis_num, add_char, tokusou=True)
                    return car_data_list

                # 車種詳細情報を閉じる
                try:
                    self.close_detail_car_page()
                    break
                except:
                    time.sleep(self.sleep_time)
            else:
                # driverを強制終了させる
                self.release_driver()

                return {"様式":model, "番号":chassis_num}
            
            return {"様式":model, "番号":chassis_num}

    # 類型で検索する
    def typology_search(self, car_model_designation_no, classification_no, tokusou=False, target_car_list_row_num=0, target_auxiliary_num_list_row_num=0):
        self.is_in_time()

        try:
            if not tokusou:
                self.open_detail_car_page()
                self.input_model_classification_num(car_model_designation_no, classification_no)
                self.click_confirm_btn()
            
            car_data_list = {}
            if self.change_handle("SUZUKI_SIOS004 収録車種一覧（２）"):
                if target_car_list_row_num == 0 and target_auxiliary_num_list_row_num == 0:
                    car_data_list = self.get_car_data_list()
                
                self.click_car_list_row(target_car_list_row_num)
                self.click_car_list_next_btn()
            
            auxiliary_num_list = {}
            if self.change_handle("SUZUKI_SIOS005 型式類別車種選択"):
                if target_auxiliary_num_list_row_num == 0:
                    auxiliary_num_list = self.get_auxiliary_num_list()
                
                self.click_auxiliary_num_list_row(target_auxiliary_num_list_row_num)
                self.click_auxiliary_num_list_next_btn()

            return car_data_list, auxiliary_num_list
        except Exception as e:
            error_message = self.get_error_message()

            for _ in range(10):
                # アラート画面を消す
                alert_message = self.close_alert()
                
                # 特装車に関するアラートは消したのち情報を取得する
                if "特装車" in alert_message:
                    self.driver.switch_to.parent_frame()
                    time.sleep(self.sleep_time)
                    
                    car_data_list, auxiliary_num_list = self.typology_search(car_model_designation_no, classification_no, tokusou=True, target_car_list_row_num=target_car_list_row_num, target_auxiliary_num_list_row_num=target_auxiliary_num_list_row_num)
                    return car_data_list, auxiliary_num_list

                # 車種詳細情報を閉じる
                try:
                    self.close_detail_car_page()
                    break
                except:
                    time.sleep(self.sleep_time)
            else:
                # driverを強制終了させる
                self.release_driver()

                return {"型式指定番号":car_model_designation_no, "類別区分番号":classification_no}
            
            return {"型式指定番号":car_model_designation_no, "類別区分番号":classification_no}

    # 特定の車種を指定して検索する
    def pinpoint_typology_search(self, car_model_designation_no, classification_no, car_name,car_model_name, youshiki, vin_start, vin_end, model_from, model_to, catalog_name, tokusou=False):
        self.is_in_time()

        try:
            if not tokusou:
                self.open_detail_car_page()
                self.input_model_classification_num(car_model_designation_no, classification_no)
                self.click_confirm_btn()
            
            if self.change_handle("SUZUKI_SIOS004 収録車種一覧（２）"):
                car_data_list = self.get_record_car_data_list()
                for idx in range(len(car_data_list["車名"])):
                    if (car_data_list["車名"][idx] == car_name and car_data_list["型式"][idx] == car_model_name and car_data_list["様式"][idx] == youshiki and car_data_list["始号機"][idx] == vin_start and car_data_list["終号機"][idx] == vin_end and car_data_list["開始年月"][idx] == model_from and car_data_list["終了年月"][idx] == model_to and car_data_list["カタログ機種"][idx] == catalog_name):
                        self.click_car_list_row(idx)
                        self.click_car_list_next_btn()
                        break
                else:
                    if (car_name == "" and car_model_name == "" and youshiki == "" and vin_start == "" and vin_end == "" and model_from == "" and model_to == "" and catalog_name == ""):
                        self.click_car_list_next_btn()
                    else:
                        raise NoCarinfoError("該当車種がありません")

            if self.change_handle("SUZUKI_SIOS005 型式類別車種選択"):
                self.click_auxiliary_num_list_no_select_btn()
            else:
                self.change_handle("SUZUKI_SIOS010 メイン")
        except Exception as e:
            error_message = self.get_error_message()
            print(error_message)

            # アラート画面を消す
            alert_message = self.close_alert()
            
            # 特装車に関するアラートは消したのち情報を取得する
            if "特装車" in error_message:
                self.driver.switch_to.parent_frame()
                time.sleep(self.sleep_time)
                
                self.pinpoint_typology_search(car_model_designation_no, classification_no, car_name, car_model_name, youshiki, vin_start, vin_end, model_from, model_to, catalog_name, tokusou=True)
            else:
                raise e

    # 部品番号を修正する
    def split_parts_code(self, parts_code, split_count):
        parts_code_list = parts_code.split(" ")
        step_count = len(parts_code_list)//split_count
        
        new_parts_code_list = []
        for i in range(split_count):
            if i == split_count-1:
                new_parts_code_list.append(" ".join(parts_code_list[step_count*i:]))
            else:
                new_parts_code_list.append(" ".join(parts_code_list[step_count*i:step_count*(i+1)]))
        
        return new_parts_code_list
    
    # 同一keyを持つ辞書を結合する
    def concat_dict(self, dict_list):
        result_dict = {}
        for key in dict_list[0].keys():
            result_dict[key] = []

        return result_dict

    # 部品番号を検索する
    def search_parts(self, parts_code_list, read_tokki=True):
        try:
            self.input_parts_num(parts_code_list)
            self.execute_add_parts()
            result_parts_list = self.get_result_parts_list(read_tokki)
            self.click_result_clear_btn()
            
            return result_parts_list
        except Exception as e:
            error_message = self.get_error_message()
            # アラート画面を消す
            alert_message = self.close_alert()
            
            # 特装車に関するアラートは消したのち情報を取得する
            if "１００件" in error_message:
                self.driver.switch_to.parent_frame()
                time.sleep(self.sleep_time)

                # 部品が残っている場合があるため、削除をかける
                self.click_result_clear_btn()

                # 部品コード一つで検索結果が100件超える場合はエラーとする
                if " " not in parts_code_list:
                    raise PartsResultOverError(Exception)
                
                # parts_code_listを分割して再度検索
                parts_code_list_list = self.split_parts_code(parts_code_list, split_count=2)

                result_parts_list_list = []
                for parts_code_list_2 in parts_code_list_list:
                    result_parts_list = self.search_parts(parts_code_list_2, read_tokki)
                    result_parts_list_list.append(result_parts_list)
                else:
                    return self.concat_dict(result_parts_list_list)
            else:
                raise e

# 時間外のエラー
class TimeOverError(Exception):
    pass

# 該当車種がないエラー
class NoCarinfoError(Exception):
    pass

# 単一部品で100件以上の結果が出る場合のエラー
class PartsResultOverError(Exception):
    pass
