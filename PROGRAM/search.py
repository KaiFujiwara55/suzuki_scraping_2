import sys
import time
import datetime
import traceback

# import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By

class new_suzuki_scraping:
    def __init__(self, start_hour, end_hour, sleep_time):
        self.driver = self.set_driver()
        
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
        self.driver.quit()        
        self.driver = None

    # 特定の画像をクリック
    def is_exist_img(self, img_path):
        for i in range(10):
            if pyautogui.locateOnScreen(img_path) is not None:
                return True
            time.sleep(1)
        
        raise False

    # ログイン
    def login(self, username, password):
        pyautogui.hotkey('win', 'd')
        time.sleep(self.sleep_time)

        self.driver.get("https://stn.suzuki.co.jp/sios/menu/SLMA_Menu.jsp")
        time.sleep(self.sleep_time)

        if self.is_exist_img(__file__.replace("serch.py", "image/dialog_img.png")):
            pyautogui.press("\t")
            pyautogui.press("\t")
            pyautogui.press("\n")
        else:
            raise Exception("ログイン画面が開けませんでした")
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
        self.driver.time_sleep(self.sleep_time)

        detail_iframe = self.driver.find_element(By.XPATH, "//iframe[@id='epc_floating_window_content_1']")
        self.driver.switch_to.frame(detail_iframe)
        time.sleep(self.sleep_time)

    # 車種詳細情報で車体番号を入力
    def input_chassis_num(self, car_model_name, chassis_num):
        veicle_no_form = self.driver.find_element(By.XPATH, "//input[@id='exportVin']")
        veicle_no_form.send_keys(f"{car_model_name}-{chassis_num}")
        time.sleep(self.sleep_time)

    # 車種詳細情報で型式指定番号・類別区分番号を入力
    def input_model_classification_num(self, model_num, classification_num):
        car_model_field = self.driver.find_element(By.ID, "katashikiNo")
        car_model_field.send_keys(model_num)
        time.sleep(0.5)
        classification_num_field = self.driver.find_element(By.ID, "rubetKubun")
        classification_num_field.send_keys(classification_num)

    # 車種詳細情報で確定ボタンをクリック
    def click_confirm_btn(self):
        confirm_btn = self.driver.find_element(By.XPATH, "//input[@id='decisioner']")
        confirm_btn.click()
        time.sleep(self.sleep_time)
    
    # 車種詳細情報で車種情報クリアボタンをクリック
    def click_clear_btn(self):
        clear_btn = self.driver.find_element(By.XPATH, "//input[@id='clearer']")
        clear_btn.click()
        time.sleep(self.sleep_time)

    # 車種詳細情報の情報を取得
    def get_car_data_list(self):
        car_data_list = []
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

    # エラーメッセージを取得
    def get_error_message(self):
        etype, value, tb = sys.exc_info()
        error_message = "".join(traceback.format_exception(etype, value, tb))

        return error_message

    # アラートを消す
    def close_alert(self):
        self.driver.switch_to.alert.accept()

    # 開かれているページの中で指定したページにハンドルを切り替える
    def change_handle(self, title):
        current_handles = self.driver.window_handles
        current_handles.reverse()

        for current_handle in current_handles:
            self.driver.switch_to.window(current_handle)
            time.sleep(self.sleep_time)

            if self.driver.title == title:
                return True
        
        return False

    # 指定したページがあるかどうかを確認
    def is_exist_page(self, title):
        current_handles = self.driver.window_handles
        current_handles.reverse()

        for current_handle in current_handles:
            self.driver.switch_to.window(current_handle)
            time.sleep(self.sleep_time)

            if self.driver.title == title:
                return True
            else:
                continue
        else:
            return False

    # Webサイトの開いている時間内かを調べる
    def is_in_time(self):
        now = datetime.datetime.now()
        if self.start_hour <= now.hour and now.hour < self.end_hour:
            return True
        else:
            return False

    # 車種情報ページまで遷移
    def scraping_setup(self):
        if not self.is_in_time():
            raise Exception("Webサイトの開いている時間外です")
        
        self.login()
        self.move_parts_order_page()
        self.move_car_info_page()

    # 車体番号を検索する
    def chassis_num_serch(self, model, chassis_num, add_char, tokusou=False):
        if not self.is_in_time():
            raise Exception("Webサイトの開いている時間外です")
        try:
            if not tokusou:
                self.open_detail_car_page()
                self.input_chassis_num(model, chassis_num)
                self.click_confirm_btn()

            car_data_list = self.get_car_data_list()
            self.click_clear_btn()
            self.close_detail_car_page()

            return True, car_data_list
        except Exception as e:
            error_message = self.get_error_message()

            for errorCount in range(10):
                # アラート画面を消す
                try:
                    self.close_alert()
                except:
                    pass
                
                # 特装車に関するアラートは消したのち情報を取得する
                if "特装車" in error_message:
                    flg, car_data_list = self.chassis_num_serch(model, chassis_num, add_char, tokusou=True)
                    return flg, car_data_list

                # 車種詳細情報を閉じる
                try:
                    self.close_detail_car_page()
                    break
                except:
                    time.sleep(self.sleep_time)
            else:
                # driverを強制終了させる
                self.release_driver()

                return "Error", {"様式":model, "番号":chassis_num}
            
            return False, {"様式":model, "番号":chassis_num}
