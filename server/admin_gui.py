import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os

SERVER_URL = "http://127.0.0.1:5000"

class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Admin Panel")
        self.geometry("800x600")

        # GUI-Elemente
        self.image_list = ttk.Treeview(self, columns=("Username", "Filename"), show="headings")
        self.image_list.heading("Username", text="Hochgeladen von")
        self.image_list.heading("Filename", text="Dateiname")
        self.image_list.bind("<<TreeviewSelect>>", self.preview_image)

        self.image_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Vorschaufenster
        self.preview_frame = tk.Frame(self, width=300)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.preview_label = tk.Label(self.preview_frame, text="Vorschau", font=("Arial", 14))
        self.preview_label.pack()
        self.preview_canvas = tk.Label(self.preview_frame)
        self.preview_canvas.pack()

        # Steuerungsbuttons
        self.delete_button = tk.Button(self.preview_frame, text="Bild löschen", command=self.delete_selected_image)
        self.delete_button.pack(pady=10)

        self.sync_button = tk.Button(self.preview_frame, text="Synchronisieren", command=self.load_images)
        self.sync_button.pack(pady=10)

        # Daten laden
        self.load_images()

    def load_images(self):
        """Lädt die Bilddaten vom Server."""
        try:
            response = requests.get(f"{SERVER_URL}/images")
            if response.status_code == 200:
                images = response.json().get("images", [])
                self.update_image_list(images)
            else:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Bilder: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Verbinden mit dem Server: {str(e)}")

    def update_image_list(self, images):
        """Aktualisiert die Liste der Bilder."""
        self.image_list.delete(*self.image_list.get_children())
        for image in images:
            self.image_list.insert("", tk.END, values=(image["username"], image["filepath"]))

    def preview_image(self, event):
        """Zeigt das ausgewählte Bild in der Vorschau an."""
        selected_item = self.image_list.selection()
        if selected_item:
            item = self.image_list.item(selected_item[0])
            filename = item["values"][1]

            # Lade das Bild vom Server
            try:
                response = requests.get(f"{SERVER_URL}/uploaded_images/{filename}", stream=True)
                if response.status_code == 200:
                    image_data = Image.open(BytesIO(response.content))
                    image_data.thumbnail((300, 300))  # Bild skalieren
                    image_tk = ImageTk.PhotoImage(image_data)

                    # Bild anzeigen
                    self.preview_canvas.config(image=image_tk)
                    self.preview_canvas.image = image_tk
                else:
                    messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes: {response.status_code}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes: {str(e)}")

    def delete_selected_image(self):
        """Löscht das ausgewählte Bild vom Server."""
        selected_item = self.image_list.selection()
        if selected_item:
            item = self.image_list.item(selected_item[0])
            filename = item["values"][1]

            # Bestätigung
            if messagebox.askyesno("Löschen", f"Möchten Sie das Bild '{filename}' wirklich löschen?"):
                try:
                    response = requests.delete(f"{SERVER_URL}/delete/{filename}")
                    if response.status_code == 200:
                        messagebox.showinfo("Erfolg", "Bild erfolgreich gelöscht")
                        self.load_images()
                    else:
                        messagebox.showerror("Fehler", f"Fehler beim Löschen: {response.status_code}")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Löschen: {str(e)}")

# Hauptprogramm
if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
