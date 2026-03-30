import customtkinter as ctk
import os
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CyberNotesUltimate(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🚀 CYBER NOTES PRO v7.5")
        self.geometry("1100x750")
        self.notes_dir = "my_notes"
        self.current_file = None 
        self.lang = "EN"
        self.history_buttons = {} # Словарь для хранения кнопок {имя_файла: объект_кнопки}
        
        if not os.path.exists(self.notes_dir):
            os.makedirs(self.notes_dir)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#0D0D0D")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="SYSTEM_CORE 📟", font=("Courier New", 22, "bold"), text_color="#00FF41")
        self.logo_label.pack(pady=25)
        
        self.new_btn = ctk.CTkButton(self.sidebar, text="+ NEW DATA", command=self.new_note, fg_color="#1f1f1f")
        self.new_btn.pack(pady=5, padx=20, fill="x")

        self.updates_btn = ctk.CTkButton(self.sidebar, text="✨ UPDATES", command=self.show_updates, fg_color="#1f1f1f")
        self.updates_btn.pack(pady=5, padx=20, fill="x")

        self.lang_btn = ctk.CTkButton(self.sidebar, text="🌐 ЯЗЫК: RU", command=self.toggle_lang, fg_color="#333333")
        self.lang_btn.pack(pady=5, padx=20, fill="x")

        self.history_label = ctk.CTkLabel(self.sidebar, text="SYSTEM_ARCHIVE", font=("Arial", 12, "bold"), text_color="#555555")
        self.history_label.pack(pady=(20, 5))
        
        self.history_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", height=400)
        self.history_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # --- MAIN EDITOR ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)
        
        self.title_entry = ctk.CTkEntry(self.main_frame, placeholder_text="ENTRY_TITLE...", 
                                        font=("Consolas", 22, "bold"), height=55, border_color="#00FF41", fg_color="#0D0D0D")
        self.title_entry.pack(fill="x", pady=(0, 15))

        self.emoji_frame = ctk.CTkFrame(self.main_frame, fg_color="#141414", height=60, corner_radius=15)
        self.emoji_frame.pack(fill="x", pady=(0, 10))
        
        emojis = ["🔥", "🚀", "💎", "✨", "🧬", "🎮", "🛸", "🤖", "⚡", "🌈", "👑", "🍕"]
        for emo in emojis:
            ctk.CTkButton(self.emoji_frame, text=emo, width=45, height=45, fg_color="transparent", font=("Segoe UI Emoji", 20), command=lambda e=emo: self.insert_emoji(e)).pack(side="left", padx=3)

        self.textbox = ctk.CTkTextbox(self.main_frame, font=("Consolas", 17), border_width=2, fg_color="#0D0D0D")
        self.textbox.pack(fill="both", expand=True, pady=(0, 20))

        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(fill="x")

        self.save_btn = ctk.CTkButton(self.action_frame, text="SAVE CHANGES 💾", command=self.save_note, height=60, fg_color="#0062ff")
        self.save_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.delete_btn = ctk.CTkButton(self.action_frame, text="PURGE 🗑️", width=160, command=self.show_delete_overlay, height=60, fg_color="#ff2a2a")
        self.delete_btn.pack(side="left")

        self.overlay = ctk.CTkFrame(self, fg_color="#000000")
        self.full_reload_history()

    # --- УМНОЕ ОБНОВЛЕНИЕ ИСТОРИИ БЕЗ ПРЫЖКОВ ---
    def full_reload_history(self):
        """Полная перезагрузка только при старте или удалении"""
        for widget in self.history_frame.winfo_children(): widget.destroy()
        self.history_buttons = {}
        files = sorted(os.listdir(self.notes_dir))
        for file in files:
            if file.endswith(".txt"):
                btn = ctk.CTkButton(self.history_frame, text=f"📂 {file.replace('.txt', '')}", fg_color="transparent", anchor="w", command=lambda f=file: self.load_note(f))
                btn.pack(pady=2, fill="x")
                self.history_buttons[file] = btn

    def save_note(self):
        new_title = self.title_entry.get().strip()
        if not new_title: new_title = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_title = "".join([c for c in new_title if c.isalnum() or c in (' ', '_', '-')]).rstrip()
        new_filename = f"{safe_title}.txt"
        new_path = os.path.join(self.notes_dir, new_filename)
        
        # ЛОГИКА ПЕРЕИМЕНОВАНИЯ БЕЗ ПЕРЕЗАГРУЗКИ СПИСКА 🏷️
        if self.current_file and self.current_file != new_filename:
            old_path = os.path.join(self.notes_dir, self.current_file)
            if os.path.exists(old_path): os.remove(old_path)
            
            # Обновляем существующую кнопку вместо полной перезагрузки! ✨
            if self.current_file in self.history_buttons:
                btn = self.history_buttons.pop(self.current_file)
                btn.configure(text=f"📂 {safe_title}", command=lambda f=new_filename: self.load_note(f))
                self.history_buttons[new_filename] = btn
        
        elif not self.current_file and new_filename not in self.history_buttons:
            # Если это новая запись, которой нет в списке — только тогда добавляем кнопку
            self.full_reload_history()

        with open(new_path, "w", encoding="utf-8") as f:
            f.write(self.textbox.get("0.0", "end").strip())
        
        self.current_file = new_filename
        msg = "UPDATED! ✅" if self.lang == "EN" else "ОБНОВЛЕНО! ✅"
        self.save_btn.configure(text=msg, fg_color="#00FF41", text_color="#000000")
        self.after(1000, lambda: self.save_btn.configure(text="SAVE CHANGES 💾" if self.lang == "EN" else "СОХРАНИТЬ ИЗМЕНЕНИЯ 💾", fg_color="#0062ff", text_color="#FFFFFF"))

    def load_note(self, filename):
        self.current_file = filename
        with open(os.path.join(self.notes_dir, filename), "r", encoding="utf-8") as f:
            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, filename.replace(".txt", ""))
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", f.read())

    def new_note(self):
        self.current_file = None
        self.title_entry.delete(0, "end")
        self.textbox.delete("0.0", "end")

    def toggle_lang(self):
        if self.lang == "EN":
            self.lang = "RU"
            self.lang_btn.configure(text="🌐 LANG: EN"); self.new_btn.configure(text="+ НОВАЯ ЗАПИСЬ")
            self.updates_btn.configure(text="✨ ОБНОВЛЕНИЯ"); self.save_btn.configure(text="ОБНОВИТЬ / СОХРАНИТЬ 💾")
            self.delete_btn.configure(text="УДАЛИТЬ 🗑️"); self.history_label.configure(text="АРХИВ ЗАПИСЕЙ")
            self.title_entry.configure(placeholder_text="ВВЕДИТЕ НАЗВАНИЕ...")
        else:
            self.lang = "EN"
            self.lang_btn.configure(text="🌐 ЯЗЫК: RU"); self.new_btn.configure(text="+ NEW DATA")
            self.updates_btn.configure(text="✨ UPDATES"); self.save_btn.configure(text="UPDATE / SAVE 💾")
            self.delete_btn.configure(text="PURGE 🗑️"); self.history_label.configure(text="SYSTEM_ARCHIVE")
            self.title_entry.configure(placeholder_text="ENTRY_TITLE...")

    def show_updates(self):
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        for w in self.overlay.winfo_children(): w.destroy()
        box = ctk.CTkFrame(self.overlay, fg_color="#1A1A1A", border_width=2, border_color="#00FF41", width=600, height=450)
        box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(box, text="VERSION 1.3 (FREEZE POSITION) 🚀", font=("Consolas", 18, "bold"), text_color="#00FF41").pack(pady=20)
        logs = "• Fixed: Notes no longer jump in list 📌\n• Real-time button renaming 🏷️\n• Smooth UI transition ✨"
        ctk.CTkLabel(box, text=logs, font=("Consolas", 16)).pack(pady=20, padx=40)
        ctk.CTkButton(box, text="CLOSE", command=self.overlay.place_forget).pack(pady=20)

    def show_delete_overlay(self):
        if not self.current_file: return
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        for w in self.overlay.winfo_children(): w.destroy()
        box = ctk.CTkFrame(self.overlay, fg_color="#1A1A1A", border_width=2, border_color="#ff2a2a")
        box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(box, text="PURGE DATA? 💀", font=("Arial", 16, "bold"), pady=30, padx=50).pack()
        ctk.CTkButton(box, text="YES", fg_color="#ff2a2a", command=self.delete_note).pack(side="left", padx=20, pady=20)
        ctk.CTkButton(box, text="NO", fg_color="#333333", command=self.overlay.place_forget).pack(side="right", padx=20, pady=20)

    def delete_note(self):
        if self.current_file: os.remove(os.path.join(self.notes_dir, self.current_file))
        self.new_note(); self.full_reload_history(); self.overlay.place_forget()

    def insert_emoji(self, emoji): self.textbox.insert("insert", emoji)

if __name__ == "__main__":
    app = CyberNotesUltimate(); app.mainloop()
