import customtkinter as ctk

class KillFeed(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.label = ctk.CTkLabel(self, text="", font=("Consolas", 16, "bold"))
        self.label.pack()

    def notify(self, text, destructive=False):
        self.label.configure(
            text=text,
            text_color="#8f111a" if destructive else "#1c7c54"
        )
        self.place(relx=1.0, rely=.055, anchor="ne")
        self._slide_in(1.0)

    def _slide_in(self, x):
        if x > .73:
            self.place_configure(relx=x)
            self.after(12, lambda: self._slide_in(x-.045))
        else:
            self.after(1000, lambda: self._slide_out(.73))

    def _slide_out(self, x):
        if x < 1.02:
            self.place_configure(relx=x)
            self.after(12, lambda: self._slide_out(x+.055))
