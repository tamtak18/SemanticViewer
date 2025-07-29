import os
import time
import threading
import pandas as pd
import tkinter as tk
from tkinter import messagebox

# フォルダ設定
CODE_FOLDER = './watched_code_folder'
SOURCE_ASSET_FOLDER = './source_asset_folder'
DOC_ASSET_FOLDER = './design_docs_folder'
MAPPER_TABLE_PATH = './mapper_table.csv'

# マッパーテーブル読み込み
def load_mapper():
    """
    CSV から source_file と design_doc のマッピングテーブルを読み込む。
    headerが正しくない場合はヘッダなしとして読み直す。
    """
    try:
        df = pd.read_csv(MAPPER_TABLE_PATH)
        if set(['source_file', 'design_doc']).issubset(df.columns):
            return df
    except Exception:
        pass
    # ヘッダなし想定で再読み込み
    df = pd.read_csv(MAPPER_TABLE_PATH, header=None, names=['source_file', 'design_doc'])
    return df

# 設計書検索: スニペットの内容から該当するソースファイルを検索し、マッピング情報に基づいて設計書名を返す
def find_design_docs(snippet_filename, mapper_df):
    snippet_path = os.path.join(CODE_FOLDER, snippet_filename)
    try:
        with open(snippet_path, 'r', encoding='utf-8') as f:
            snippet_text = f.read().strip()
    except Exception as e:
        print(f"スニペットの読み込みエラー: {snippet_filename}, {e}")
        return []

    if not snippet_text:
        return []

    matched_docs = []
    # マッピングテーブルの各行を確認
    for _, row in mapper_df.iterrows():
        source_file = row['source_file']
        design_doc = row['design_doc']
        source_path = os.path.join(SOURCE_ASSET_FOLDER, source_file)
        if not os.path.exists(source_path):
            continue
        try:
            with open(source_path, 'r', encoding='utf-8') as sf:
                source_text = sf.read()
            # スニペット全文がソースファイル内に含まれるかチェック
            if snippet_text in source_text:
                matched_docs.append(design_doc)
        except Exception as e:
            print(f"ソースファイル読み込みエラー: {source_file}, {e}")
    return matched_docs

# GUI 表示クラス
class DesignDocViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("設計書セマンティックビューワ")
        self.geometry("600x400")

        self.listbox = tk.Listbox(self, font=("Arial", 14))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.listbox.bind('<Double-1>', self.display_doc)

    def update_list(self, docs):
        """リストを更新。docs が空ならメッセージ表示"""
        self.listbox.delete(0, tk.END)
        if docs:
            for doc in docs:
                self.listbox.insert(tk.END, doc)
        else:
            self.listbox.insert(tk.END, "(該当する設計書がありません)")

    def display_doc(self, event):
        selected = self.listbox.get(tk.ACTIVE)
        if selected.startswith("("):
            return
        doc_path = os.path.join(DOC_ASSET_FOLDER, selected)
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.show_doc_window(selected, content)
        else:
            messagebox.showerror("Error", "設計書ファイルが見つかりません")

    def show_doc_window(self, title, content):
        doc_win = tk.Toplevel(self)
        doc_win.title(title)
        text = tk.Text(doc_win, wrap=tk.WORD, font=("Arial", 12))
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, content)

# フォルダ監視スレッド
class FolderWatcher(threading.Thread):
    def __init__(self, folder, callback):
        super().__init__(daemon=True)
        self.folder = folder
        self.callback = callback
        # フォルダが存在しない場合は空
        try:
            self.seen_files = set(os.listdir(folder))
        except FileNotFoundError:
            self.seen_files = set()

    def run(self):
        while True:
            try:
                current_files = set(os.listdir(self.folder))
            except FileNotFoundError:
                current_files = set()
            new_files = current_files - self.seen_files
            if new_files:
                for file in new_files:
                    self.callback(file)
            self.seen_files = current_files
            time.sleep(1)

# メイン処理
def main():
    # マッパーテーブル読み込み
    mapper_df = load_mapper()
    # GUI 起動
    viewer = DesignDocViewer()

    # 新規スニペット検出時のコールバック
    def on_new_code_detected(filename):
        docs = find_design_docs(filename, mapper_df)
        viewer.update_list(docs)

    # フォルダ監視開始
    watcher = FolderWatcher(CODE_FOLDER, on_new_code_detected)
    watcher.start()

    # GUI メインループ
    viewer.mainloop()

if __name__ == '__main__':
    main()
