# デヂエのお知らせページから，各お知らせへのリンクやタイトルを取得

import requests, bs4, re

class Scrape:
    # コンストラクタ
    def __init__(self, url, filepath):
        self.url = url # ページのURL
        self.filepath = filepath # IDの書き出し先

        # ----- どのページかの判定に用いる -----
        self.info = False # お知らせページ
        self.change = False # 時間割・講義室変更ページ
        self.cancel = False # 休講通知ページ
        self.makeup = False # 補講通知ページ
        self.call = False # 学生呼び出しページ
        self.exam = False # 授業調整・期末試験ページ

        # ----- どのページかの判定 -----
        if "did=357" in self.url: # お知らせページ
            self.info = True
        elif "did=391" in self.url: # 時間割・講義室変更ページ
            self.change = True
        elif "did=361" in self.url: # 休講通知ページ
            self.cancel = True
        elif "did=363" in self.url: # 補講通知ページ
            self.makeup = True
        elif "did=393" in self.url: # 学生呼び出しページ
            self.call = True
        elif "did=364" in self.url: # 授業調整・期末試験ページ
            self.exam = True


    # ファイルにページIDを書き出し
    def write_rid(self, rid):
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(str(rid))


    # ページIDの取得
    def get_rid(self):
        with open(self.filepath) as f:
            rid = f.read()
        return rid


    # リンクやらタイトルやらを取得
    def get_elems(self):
        req = requests.get(self.url) # 接続
        req.raise_for_status() # 接続チェック

        soup = bs4.BeautifulSoup(req.text, "html.parser")

        # 要素を辞書に入れていく
        elements = {}

        # ----- 要素の取得 -----
        # リンクを取得
        elements["link_elems"] = soup.select(".dz_fontSmall > a")

        # タイトルの取得
        if self.info or self.call or self.exam:
            elements["title_elems"] = soup.select(".record-value-7")
        elif self.change:
            elements["title_elems"] = soup.select(".record-value-116")
        
        # 日付の取得
        elements["date_elems"] = soup.select(".record-value-4")

        # 時限等の取得
        if self.info:
            elements["period_elems"] = soup.select(".record-value-221")
        elif self.change:
            elements["period_elems"] = soup.select(".record-value-200")
        elif self.cancel or self.makeup or self.exam:
            elements["period_elems"] = soup.select(".record-value-94")

        # 学科の取得
        if self.info or self.cancel or self.makeup or self.call or self.exam:
            elements["department_elems"] = soup.select(".record-value-109")
        elif self.change:
            elements["department_elems"] = soup.select(".record-value-6")
        
        # 学年の取得
        if self.info or self.cancel or self.makeup or self.exam:
            elements["year_elems"] = soup.select(".record-value-111")
        elif self.change:
            elements["year_elems"] = soup.select(".record-value-109")
        elif self.call:
            elements["year_elems"] = soup.select(".record-value-119")
        
        # 科目の取得
        if self.change:
            elements["subject_elems"] = soup.select(".record-value-203")
        elif self.cancel or self.makeup:
            elements["subject_elems"] = soup.select(".record-value-7")
        
        # 教員の取得
        if self.change:
            elements["teacher_elems"] = soup.select(".record-value-204")
        elif self.cancel or self.makeup or self.exam:
            elements["teacher_elems"] = soup.select(".record-value-8")

        # 種別の取得（時間割・講義室変更）
        if self.change:
            elements["type_elems"] = soup.select(".record-value-201")
        
        # 変更前の取得（時間割・講義室変更）
        if self.change:
            elements["before_elems"] = soup.select(".record-value-205")
        
        # 変更後の取得（時間割・講義室変更）
        if self.change:
            elements["after_elems"] = soup.select(".record-value-206")
        
        # 注記の取得（学生呼び出し）
        if self.call:
            elements["note_elems"] = soup.select(".record-value-121")
        
        # ----- 要素の取得ここまで -----


        # 要素を返す
        return elements


    # 取得した情報を文字列として返す
    # 引数：url -> デヂエのページのurl, filepath -> IDの書き出し先
    def get_elems_string(self):
        # 返す文字列
        ret_str = ""

        # 要素を取得
        elements = self.get_elems()

        # 各ページのIDを取得するための正規表現
        pattern = r"rid=\d+"
        rid_regex = re.compile(pattern)

        # 最大20件表示する
        for i in range(20):
            # 各ページのURL．0番目には詳細検索のリンクが入る
            page_url = "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/" + elements["link_elems"][i+1].get("href")

            # ページのID取得（正規表現使用）
            match_obj = rid_regex.findall(page_url) # マッチした文字列のリストが返る
            
            # ページのID．"rid=(数字)"という文字列から数字のみを取り出す
            rid = int(match_obj[0][4:])

            # 最新のページIDを記録
            if(i == 0):
                newest_rid = rid

            # datファイルからIDを読み取り，読み取ったIDより大きいものを表示
            if(rid > int(self.get_rid())):
                # ----- 取得した情報の表示 -----
                # お知らせページ
                if self.info:
                    #ret_str += "ID : " + str(rid) + "\n"
                    ret_str += "【お知らせ】\n"
                    ret_str += "URL : " + page_url + "\n"                                           # 各ページのURL
                    ret_str += "タイトル : " + str(elements["title_elems"][i].text) + "\n"          # タイトル
                    ret_str += "日付 : " + str(elements["date_elems"][i].text) + "\n"               # 日付
                    ret_str += "時限等 : " + str(elements["period_elems"][i].text) + "\n"           # 時限
                    ret_str += "対象学科 : " + str(elements["department_elems"][i].text) + "\n"     # 対象学科
                    ret_str += "対象学年 : " + str(elements["year_elems"][i].text) + "\n\n"         # 対象学年

                # 時間割・講義室変更ページ
                elif self.change:
                    #ret_str += "ID : " + str(rid) + "\n"
                    ret_str += "【時間割・講義室変更】\n"
                    ret_str += "URL : " + page_url + "\n"                                        # 各ページのURL
                    ret_str += "タイトル : " + str(elements["title_elems"][i].text) + "\n"       # タイトル
                    ret_str += "科目名 : " + str(elements["subject_elems"][i].text) + "\n"       # 科目
                    ret_str += "教員 : " + str(elements["teacher_elems"][i].text) + "\n"         # 教員
                    ret_str += "日付 : " + str(elements["date_elems"][i].text) + "\n"            # 日付
                    ret_str += "時限等 : " + str(elements["period_elems"][i].text) + "\n"        # 時限
                    ret_str += "種別 : " + str(elements["type_elems"][i].text) + "\n"            # 種別
                    ret_str += "変更前 : " + str(elements["before_elems"][i].text) + "\n"        # 変更前
                    ret_str += "変更後 : " + str(elements["after_elems"][i].text) + "\n"         # 変更後
                    ret_str += "対象学科 : " + str(elements["department_elems"][i].text) + "\n"  # 対象学科
                    ret_str += "対象学年 : " + str(elements["year_elems"][i].text) + "\n\n"      # 対象学年

                # 休講通知ページ, 補講通知ページ
                elif self.cancel or self.makeup:
                    if self.cancel:
                        ret_str += "【休講通知】\n"
                    else:
                        ret_str += "【補講通知】\n"
                    #ret_str += "ID : " + str(rid) + "\n"
                    ret_str += "URL : " + page_url + "\n"                                        # 各ページのURL
                    ret_str += "日付 : " + str(elements["date_elems"][i].text) + "\n"            # 日付
                    ret_str += "時限等 : " + str(elements["period_elems"][i].text) + "\n"        # 時限
                    ret_str += "科目名 : " + str(elements["subject_elems"][i].text) + "\n"       # 科目
                    ret_str += "教員名 : " + str(elements["teacher_elems"][i].text) + "\n"       # 教員
                    ret_str += "対象学科 : " + str(elements["department_elems"][i].text) + "\n"  # 対象学科
                    ret_str += "対象学年 : " + str(elements["year_elems"][i].text) + "\n\n"      # 対象学年

                # 学生呼び出しページ
                elif self.call:
                    #ret_str += "ID : " + str(rid) + "\n"
                    ret_str += "【学生呼び出し】\n"
                    ret_str += "URL : " + page_url + "\n"                                        # 各ページのURL
                    ret_str += "タイトル : " + str(elements["title_elems"][i].text) + "\n"       # タイトル
                    ret_str += "注記 : " + str(elements["note_elems"][i].text) + "\n"            # 注記
                    ret_str += "対象学科 : " + str(elements["department_elems"][i].text) + "\n"  # 対象学科
                    ret_str += "対象学年 : " + str(elements["year_elems"][i].text) + "\n"        # 対象学年
                    ret_str += "日付 : " + str(elements["date_elems"][i].text) + "\n\n"          # 日付

                # 授業調整・期末試験ページ
                elif self.exam:
                    #ret_str += "ID : " + str(rid) + "\n"
                    ret_str += "【授業調整・期末試験】\n"
                    ret_str += "URL : " + page_url + "\n"                                        # 各ページのURL
                    ret_str += "タイトル : " + str(elements["title_elems"][i].text) + "\n"        # タイトル
                    ret_str += "日付 : " + str(elements["date_elems"][i].text) + "\n"            # 日付
                    ret_str += "時限等 : " + str(elements["period_elems"][i].text) + "\n"        # 時限
                    ret_str += "対象学科 : " + str(elements["department_elems"][i].text) + "\n"  # 対象学科
                    ret_str += "対象学年 : " + str(elements["year_elems"][i].text) + "\n\n"      # 対象学年

        # 最新のページIDをファイルに書き出し
        self.write_rid(newest_rid)

        return ret_str


if __name__ == "__main__":
    # デヂエのページ
    info_url = "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=357" # お知らせページ
    change_url = "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=391" # 時間割・講義室変更ページ
    cancel_url = "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=361" # 休講通知ページ
    makeup_url = "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=363" # 補講通知ページ
    call_url = "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=393" # 学生呼び出しページ
    exam_url = "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=364" # 授業調整・期末試験ページ

    # 各ページのIDの書き出し先
    path_to_info = "data/rid_info.dat"
    path_to_change = "data/rid_change.dat"
    path_to_cancel = "data/rid_cancel.dat"
    path_to_makeup = "data/rid_makeup.dat"
    path_to_call = "data/rid_call.dat"
    path_to_exam = "data/rid_exam.dat"

    # 表示
    scr = Scrape(info_url, path_to_info)
    print(scr.get_elems_string())

    scr2 = Scrape(change_url, path_to_change)
    print(scr2.get_elems_string())

    scr3 = Scrape(cancel_url, path_to_cancel)
    print(scr3.get_elems_string())

    scr4 = Scrape(makeup_url, path_to_makeup)
    print(scr4.get_elems_string())

    scr5 = Scrape(call_url, path_to_call)
    print(scr5.get_elems_string())

    scr6 = Scrape(exam_url, path_to_exam)
    print(scr6.get_elems_string())

