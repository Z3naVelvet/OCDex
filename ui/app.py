import customtkinter as ctk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageDraw, ImageTk
from pathlib import Path

from core.database import *
from core.image_processor import process_image
from core.music_manager import start_music
from ui.creature_editor import CreatureEditor
from ui.kill_feed import KillFeed

RED="#c91f2b"; DARK_RED="#8f111a"; WHITE="#f4f4f2"
GRAY="#b7b7b7"; DARK_GRAY="#424242"; BLACK="#202020"
HUMAN_HEIGHT=1.70

def make_logo(size=256):
    img=Image.new("RGBA",(size,size),(0,0,0,0))
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((8,8,size-8,size-8),radius=size//9,fill=RED,outline=WHITE,width=max(3,size//32))
    d.ellipse((size*.25,size*.25,size*.75,size*.75),fill=WHITE)
    d.ellipse((size*.39,size*.39,size*.61,size*.61),fill=RED)
    d.rectangle((size*.12,size*.46,size*.88,size*.54),fill=WHITE)
    return img

class OCDEXApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ensure_storage()
        ctk.set_appearance_mode("light")
        self.title("OCDEX — Original Character Encyclopedia")
        self.geometry("1180x760")
        self.minsize(950,650)
        self.settings=load_settings()
        self.logo=make_logo()
        self._animation_token=0
        self._icon=ImageTk.PhotoImage(self.logo.resize((32,32),Image.Resampling.LANCZOS))
        self.iconphoto(True,self._icon)

        self._startup()
        start_music(Path(__file__).resolve().parents[1], .90)

    def _startup(self):
        self.boot=ctk.CTkFrame(self,fg_color=BLACK)
        self.boot.pack(fill="both",expand=True)
        self.boot_logo=ctk.CTkLabel(
            self.boot,text="",
            image=ctk.CTkImage(light_image=self.logo,dark_image=self.logo,size=(8,8))
        )
        self.boot_logo.place(relx=.5,rely=.47,anchor="center")
        self.boot_text=ctk.CTkLabel(
            self.boot,text="OCDEX",font=("Consolas",34,"bold"),text_color=WHITE
        )
        self.boot_text.place(relx=.5,rely=.76,anchor="center")
        self._boot_expand(8)

    def _boot_expand(self,size):
        if not self.boot.winfo_exists(): return
        if size < 220:
            self.boot_logo.configure(
                image=ctk.CTkImage(light_image=self.logo,dark_image=self.logo,size=(size,size))
            )
            self.after(15,lambda:self._boot_expand(size+10))
        else:
            self.after(80,self._finish_boot)

    def _finish_boot(self):
        if not self.boot.winfo_exists(): return
        self.boot.configure(fg_color=RED)
        self.after(55, lambda: self.boot.configure(fg_color=BLACK))
        self.after(150,self._show_main)

    def _show_main(self):
        if self.boot.winfo_exists(): self.boot.destroy()
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(1,weight=1)

        header=ctk.CTkFrame(self,fg_color=RED,corner_radius=0)
        header.grid(row=0,column=0,columnspan=2,sticky="nsew")
        ctk.CTkLabel(header,text="OCDEX",font=("Consolas",28,"bold"),text_color=WHITE).pack(side="left",padx=18,pady=16)
        self.search=ctk.CTkEntry(header,placeholder_text="Search entries...",width=300)
        self.search.pack(side="left",padx=18)
        self.search.bind("<KeyRelease>",lambda e:self.refresh_list())
        ctk.CTkButton(header,text="+ NEW",command=self.new_creature,fg_color=DARK_RED,width=100).pack(side="right",padx=8)
        ctk.CTkButton(header,text="UNIVERSE",command=self.new_universe,fg_color=DARK_RED,width=110).pack(side="right",padx=8)

        side=ctk.CTkFrame(self,fg_color=WHITE,corner_radius=0)
        side.grid(row=1,column=0,sticky="nsew")
        side.grid_rowconfigure(2,weight=1)
        ctk.CTkLabel(side,text="UNIVERSE",font=("Consolas",15,"bold"),text_color=DARK_GRAY).grid(row=0,column=0,padx=12,pady=10,sticky="w")
        self.universe_var=ctk.StringVar()
        self.universe_menu=ctk.CTkOptionMenu(
            side,variable=self.universe_var,values=[""],command=lambda _:self.refresh_list(),
            fg_color=RED,button_color=DARK_RED
        )
        self.universe_menu.grid(row=1,column=0,padx=12,sticky="ew")
        self.listbox=ctk.CTkScrollableFrame(side,fg_color="#e7e7e5")
        self.listbox.grid(row=2,column=0,padx=8,pady=10,sticky="nsew")

        self.detail=ctk.CTkFrame(self,fg_color=WHITE,border_width=2,border_color=GRAY,corner_radius=0)
        self.detail.grid(row=1,column=1,sticky="nsew",padx=10,pady=10)
        self.detail.grid_columnconfigure(0,weight=1); self.detail.grid_columnconfigure(1,weight=1)

        self.title_label=ctk.CTkLabel(self.detail,text="Select an entry",font=("Consolas",28,"bold"),text_color=DARK_GRAY)
        self.title_label.grid(row=0,column=0,columnspan=2,pady=14)

        self.art_panel=ctk.CTkFrame(self.detail,fg_color=DARK_GRAY,width=430,height=320)
        self.art_panel.grid(row=1,column=0,padx=15,pady=8,sticky="nsew")
        self.art_panel.grid_propagate(False)
        self.art_label=ctk.CTkLabel(self.art_panel,text="NO ARTWORK")
        self.art_label.place(relx=.5,rely=.5,anchor="center")

        self.info=ctk.CTkLabel(self.detail,text="",justify="left",anchor="nw",font=("Consolas",14))
        self.info.grid(row=1,column=1,padx=15,pady=8,sticky="nw")

        self.size_panel=ctk.CTkFrame(self.detail,fg_color="#eeeeeb")
        self.size_panel.grid(row=2,column=0,columnspan=2,padx=15,pady=8,sticky="ew")
        self.size_canvas=ctk.CTkCanvas(self.size_panel,height=165,bg="#eeeeeb",highlightthickness=0)
        self.size_canvas.pack(fill="x")
        self.size_text=ctk.CTkLabel(self.size_panel,text="",font=("Consolas",13),text_color=DARK_GRAY)
        self.size_text.pack(pady=3)

        self.terminate=ctk.CTkButton(self.detail,text="- TERMINATE ENTRY",command=self.delete_current,fg_color=RED)
        self.terminate.grid(row=3,column=1,padx=15,pady=10,sticky="e")

        self.feed=KillFeed(self)
        self.feed.place_forget()
        self.refresh_universes()

    def refresh_universes(self):
        self.universes=load_universes()
        if not self.universes:
            create_universe("Default")
            self.universes=load_universes()
        names=list(self.universes)
        self.universe_menu.configure(values=names)
        if self.universe_var.get() not in self.universes:
            self.universe_var.set(names[0])
        self.refresh_list()

    def refresh_list(self):
        for w in self.listbox.winfo_children(): w.destroy()
        u=self.universes.get(self.universe_var.get(),{"creatures":[]})
        q=self.search.get().lower()
        for c in u.get("creatures",[]):
            if q and q not in c.get("name","").lower(): continue
            ctk.CTkButton(
                self.listbox,
                text=f'#{c.get("number","?")}  {c.get("name","Unnamed")}',
                command=lambda c=c:self.show_creature(c),
                fg_color="transparent",text_color=DARK_GRAY,
                hover_color="#d8d8d5",anchor="w"
            ).pack(fill="x",pady=2)

    def show_creature(self,c):
        self._animation_token += 1
        token=self._animation_token
        self.current=c
        self.current_weight=c.get("weight",0)
        self.title_label.configure(text=f'#{c.get("number","?")}  {c.get("name","Unnamed")}')
        types=", ".join(c.get("types",[])) or "—"
        linked=", ".join(c.get("universes",[])) or self.universe_var.get()
        self.info.configure(text=
            f"TYPE(S): {types}\n\nCLASS: {c.get('classification','—')}\n"
            f"HEIGHT: {c.get('height',0)} m\nWEIGHT: {c.get('weight',0)} kg\n"
            f"HABITAT: {c.get('habitat','—')}\n\nABILITIES: {c.get('abilities','—')}\n\n"
            f"{c.get('description','')}\n\nLINKED UNIVERSES: {linked}"
        )
        self.draw_size(c.get("height",0))
        if c.get("artwork"):
            img=process_image(data_uri_to_image(c["artwork"]),pixel_size=3,colors=32,scanlines=True,crt=True)
            self.art_img=ctk.CTkImage(light_image=img,dark_image=img,size=(400,290))
            self.art_label.configure(image=self.art_img,text="")
            self.art_label.place(x=-430,rely=.5,anchor="w")
            self._slide_art(token,-430,18)
        else:
            self.art_label.configure(image=None,text="NO ARTWORK")
            self.art_label.place(relx=.5,rely=.5,anchor="center")

    def _slide_art(self,token,x,target):
        if token!=self._animation_token or not self.art_label.winfo_exists(): return
        if x < target:
            step=max(6,int((target-x)*.14))
            x=min(target,x+step)
            self.art_label.place(x=x,rely=.5,anchor="w")
            self.after(10,lambda:self._slide_art(token,x,target))
        else:
            self.art_label.place(relx=.5,rely=.5,anchor="center")

    def draw_size(self,height):
        self.size_canvas.delete("all")
        try: h=float(height or 0)
        except: h=0
        W=max(self.size_canvas.winfo_width(),700)
        base=135
        scale=min(55,125/HUMAN_HEIGHT)
        hx,cx=190,W*.65

        def silhouette(x,height,fill):
            s=scale*height
            self.size_canvas.create_oval(x-8,base-s,x+8,base-s+16,fill=fill,outline="")
            self.size_canvas.create_rectangle(x-6,base-s+16,x+6,base,fill=fill,outline="")

        silhouette(hx,HUMAN_HEIGHT,DARK_GRAY)
        if h>0: silhouette(cx,h,RED)
        self.size_canvas.create_text(hx,148,text="HUMAN 1.70m",fill=DARK_GRAY,font=("Consolas",10))
        if h>0:
            self.size_canvas.create_text(cx,148,text=f"OC {h:.2f}m",fill=DARK_GRAY,font=("Consolas",10))
        self.size_text.configure(text=f"HEIGHT: {h:.2f} m   |   WEIGHT: {self.current_weight if hasattr(self,'current_weight') else '—'} kg")

    def new_universe(self):
        name=simpledialog.askstring("New Universe","Universe name:",parent=self)
        if not name: return
        name=name.strip()
        if not name: return
        if name in self.universes:
            messagebox.showwarning("Exists","That universe already exists.")
            return
        create_universe(name)
        self.refresh_universes()

    def new_creature(self):
        initial={
            "number":next_number(self.universes[self.universe_var.get()].get("creatures",[])),
            "universes":[self.universe_var.get()]
        }
        CreatureEditor(
            self,initial,list(self.universes),self.settings["types"],self.save_creature
        )

    def save_creature(self,c):
        # Remove stale copies of the same logical entry from every universe,
        # then write one shared OC record to all selected universes.
        name=c.get("name","")
        for uname in self.universes:
            d=load_universe(uname)
            d["creatures"]=[
                x for x in d["creatures"]
                if not (x.get("name")==name and x.get("number")==c.get("number"))
            ]
            if uname in c.get("universes",[]):
                d["creatures"].append(c)
            save_universe(d)
        self.refresh_universes()
        self.feed.notify("+ CREATURE REGISTERED")

    def delete_current(self):
        if not hasattr(self,"current"): return
        c=self.current
        if not messagebox.askyesno("Terminate","Delete this entry from every linked universe?"):
            return
        for uname in c.get("universes",[]):
            d=load_universe(uname)
            d["creatures"]=[
                x for x in d["creatures"]
                if not (x.get("name")==c.get("name") and x.get("number")==c.get("number"))
            ]
            save_universe(d)
        self.current=None
        self.refresh_universes()
        self.title_label.configure(text="Select an entry")
        self.info.configure(text="")
        self.art_label.configure(image=None,text="NO ARTWORK")
        self.feed.notify("- ENTRY TERMINATED",True)
