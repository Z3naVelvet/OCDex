import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.database import image_to_data_uri

class CreatureEditor(ctk.CTkToplevel):
    def __init__(self, master, initial, universe_names, type_names, save_callback):
        super().__init__(master)
        self.title("OCDEX — Creature Editor")
        self.geometry("720x760")
        self.configure(fg_color="#f4f4f2")
        self.save_callback = save_callback
        self.data = dict(initial)
        self._image_path = None

        fields = [
            ("Name","name"),("Classification","classification"),
            ("Height (m)","height"),("Weight (kg)","weight"),
            ("Habitat","habitat"),("Abilities","abilities"),
            ("Behaviour","behaviour"),("Description","description"),("Notes","notes")
        ]
        self.entries = {}
        for label, key in fields:
            ctk.CTkLabel(self, text=label, anchor="w").pack(fill="x", padx=18, pady=(7,0))
            e = ctk.CTkEntry(self)
            e.pack(fill="x", padx=18)
            e.insert(0, str(self.data.get(key, "")))
            self.entries[key] = e

        ctk.CTkLabel(self, text="Types").pack(anchor="w", padx=18, pady=(9,0))
        tf = ctk.CTkFrame(self, fg_color="transparent")
        tf.pack(fill="x", padx=18)
        self.type_vars = {}
        for i, t in enumerate(type_names):
            v = ctk.BooleanVar(value=t in self.data.get("types", []))
            self.type_vars[t] = v
            ctk.CTkCheckBox(tf, text=t, variable=v).grid(
                row=i//4, column=i%4, padx=4, pady=3, sticky="w"
            )

        ctk.CTkLabel(self, text="Linked universes").pack(anchor="w", padx=18, pady=(9,0))
        uf = ctk.CTkFrame(self, fg_color="transparent")
        uf.pack(fill="x", padx=18)
        self.universe_vars = {}
        for i, u in enumerate(universe_names):
            v = ctk.BooleanVar(value=u in self.data.get("universes", []))
            self.universe_vars[u] = v
            ctk.CTkCheckBox(uf, text=u, variable=v).grid(
                row=i//3, column=i%3, padx=4, pady=3, sticky="w"
            )

        self.bg_var = ctk.BooleanVar(value=False)
        ctk.CTkButton(
            self, text="IMPORT ARTWORK", command=self.import_artwork,
            fg_color="#c91f2b"
        ).pack(pady=(12,5))
        ctk.CTkCheckBox(
            self, text="Remove image background on import", variable=self.bg_var
        ).pack()

        ctk.CTkButton(
            self, text="SAVE ENTRY", command=self.save, fg_color="#8f111a"
        ).pack(pady=14)

    def import_artwork(self):
        p = filedialog.askopenfilename(
            filetypes=[("Images","*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if p:
            self._image_path = p
            messagebox.showinfo("Artwork", "Artwork selected. Save the entry to embed it.")

    def save(self):
        d = dict(self.data)
        for k, e in self.entries.items():
            d[k] = e.get().strip()
        try:
            d["height"] = float(d["height"]) if d["height"] else 0.0
        except ValueError:
            d["height"] = 0.0
        try:
            d["weight"] = float(d["weight"]) if d["weight"] else 0.0
        except ValueError:
            d["weight"] = 0.0
        d["types"] = [t for t,v in self.type_vars.items() if v.get()]
        d["universes"] = [u for u,v in self.universe_vars.items() if v.get()]
        if self._image_path:
            d["artwork"] = image_to_data_uri(self._image_path, self.bg_var.get())
        self.save_callback(d)
        self.destroy()
