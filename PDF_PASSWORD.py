import tkinter as tk
from tkinter import filedialog, messagebox
import pikepdf
import os

class PDFPasswordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF パスワード設定ツール")
        self.root.geometry("500x300")
        
        # タイトル
        title_label = tk.Label(root, text="PDFファイルにパスワードを設定", font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # ファイル選択ボタン
        self.select_button = tk.Button(root, text="PDFファイルを選択", command=self.select_file, width=20, height=2)
        self.select_button.pack(pady=10)
        
        # 選択されたファイル名表示
        self.file_label = tk.Label(root, text="ファイルが選択されていません", fg="gray")
        self.file_label.pack(pady=5)
        
        # パスワード入力
        password_frame = tk.Frame(root)
        password_frame.pack(pady=10)
        
        tk.Label(password_frame, text="パスワード:").pack(side=tk.LEFT, padx=5)
        self.password_entry = tk.Entry(password_frame, show="*", width=25)
        self.password_entry.pack(side=tk.LEFT, padx=5)
        
        # パスワード設定ボタン
        self.set_button = tk.Button(root, text="パスワードを設定", command=self.set_password, width=20, height=2, bg="#2F312F", fg="white")
        self.set_button.pack(pady=20)
        
        self.input_file = None
    
    def select_file(self):
        self.input_file = filedialog.askopenfilename(
            title="PDFファイルを選択",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if self.input_file:
            filename = os.path.basename(self.input_file)
            self.file_label.config(text=f"選択: {filename}", fg="black")
    
    def set_password(self):
        if not self.input_file:
            messagebox.showerror("エラー", "PDFファイルを選択してください")
            return
        
        password = self.password_entry.get()
        if not password:
            messagebox.showerror("エラー", "パスワードを入力してください")
            return
        
        # 出力ファイル名の生成
        base_name = os.path.splitext(self.input_file)[0]
        output_file = f"{base_name}_protected.pdf"
        
        try:
            with pikepdf.open(self.input_file) as pdf:
                pdf.save(output_file, encryption=pikepdf.Encryption(
                    user=password,
                    owner=password,
                    R=6  # AES-256暗号化
                ))
            messagebox.showinfo("成功", f"パスワード保護されたPDFを作成しました:\n{os.path.basename(output_file)}")
            
            # リセット
            self.input_file = None
            self.file_label.config(text="ファイルが選択されていません", fg="gray")
            self.password_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("エラー", f"エラーが発生しました:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFPasswordApp(root)
    root.mainloop()