import subprocess as sub
import customtkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
from ytmusicapi import YTMusic
import os, datetime, sys
from shutil import which
import threading as the
from urllib.request import urlretrieve
import tempfile
import webbrowser

class Window(tk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WaveDown")
        self.geometry("600x650")

        # Check values
        self.is_working = False # Fight user's impatience >:(
        self.zenity_check = bool(which('zenity')) # Check for zenity file picker
        self.loaded_default = True
        self.search_mode = 'id' # default mode search (By URL)
        self.thetmp = tempfile.gettempdir() # get temporary folder
        self.tmp = os.path.join(self.thetmp, 'wavedown') # make program's temporary folder
        # check for ffmpeg and ytdlp
        self.ffmpeg = which('ffmpeg')
        self.ytdlp = which('yt-dlp')

        # if ffmpeg and ytdlp don't exist display a message, leave.
        if not self.ffmpeg:
            messagebox.askokcancel(title="Missing ffmpeg!",message='FFMPEG is required for proper program functioning.', detail='Please install ffmpeg into your path!')
            sys.exit(1)
        if not self.ytdlp:
            messagebox.askokcancel(title="Missing yt-dlp!",message="YT-DLP is CRUCIAL for this program to work!", detail='Please install yt-dlp into your path!')
            sys.exit(1)

        os.makedirs(self.tmp, exist_ok=True) # create temporary
        if os.path.exists('cookies.txt'): # check for cookies in the same folder
            with open('cookies.txt', 'r') as f:
                data = f.read() # read cookies
            with open(os.path.join(self.tmp, 'cookies.txt'), 'w') as f:
                f.write(data) # write cookies to temporary folder

        self.protocol('WM_DELETE_WINDOW',self.close) # assign close function to application closing

        #
        savepath = os.path.join(self.tmp, 'default.png') # define save path
        if not os.path.exists(savepath):
            temp_image = Image.new('RGB', (300, 300), (75, 75, 75)) # Create gray square 300x300
            draw = ImageDraw.Draw(temp_image)
            draw.text((110,150), "Song Cover Here!", (255,255,255)) # Add text onto it
            temp_image.save(savepath) # save to temp folder

        self.default_image = tk.CTkImage(light_image=Image.open(savepath),size=(300, 300)) # set the temporary image


        # Video metadata values
        self.mtitle = None
        self.mauthor = None
        self.mvid = None
        self.mdate = None
        self.mthumbnail_url = None


        # Entire GUI
        self.search_options_label = tk.CTkLabel(self, bg_color='gray', text='|    Search    |',height=20)
        self.search_options_label.pack(fill='x')

        self.addcookiesbutton = tk.CTkButton(self, text='Add cookies.txt', command=self.addcookies)
        self.addcookiesbutton.pack(fill='x', pady=5)

        self.sfr = tk.CTkFrame(self)
        self.sfr.grid_columnconfigure(1, weight=1)
        self.modebut = tk.CTkComboBox(self.sfr,width=200,values=['Search by URL','Search by Name (YouTube)','Search by Name (YTMusic)'])
        self.modebut.set('Search by URL')
        self.modebut.grid(row=0, column=0)
        self.sentry = tk.CTkEntry(self.sfr)
        self.sentry.grid(row=0, column=1, sticky='ew')
        self.sbut = tk.CTkButton(self.sfr, text="Search", width=30, command=self.fetch_metadata)
        self.sbut.grid(row=0,column=2)

        self.sfr.pack(pady=5, fill='x')

        self.download_options_label = tk.CTkLabel(self, bg_color='gray', text='|    Metadata    |',height=20)
        self.download_options_label.pack(fill='x')

        self.musictitle = tk.CTkLabel(self, text="Title: WaveDown", font=('',14))
        self.musictitle.pack()

        self.imglab = tk.CTkFrame(self)
        self.coverlab = tk.CTkLabel(self.imglab, image=self.default_image, text="")
        self.coverlab.pack()
        self.imglab.pack()

        self.authorlab = tk.CTkLabel(self, text="Author: qmicropi")
        self.videoidlab = tk.CTkLabel(self, text="ID: https://github.com/qmicropi/wavedown")
        self.datelab = tk.CTkLabel(self, text=f"Date: {datetime.datetime.now()}")

        self.authorlab.pack()
        self.videoidlab.pack()
        self.datelab.pack()


        self.download_options_label = tk.CTkLabel(self, bg_color='gray', text='|   Download Options    |',height=20)
        self.download_options_label.pack(fill='x')
        
        self.download_frame = tk.CTkFrame(self)

        self.output_d_frame = tk.CTkFrame(self.download_frame)
        self.output_d_frame.grid_columnconfigure(1, weight=1)
        self.fpb = tk.CTkButton(self.output_d_frame, text="Choose Download Path...", command=self.get_savepath)
        self.fpe = tk.CTkEntry(self.output_d_frame)
        self.fpb.grid(row=0, column=0)
        self.fpe.grid(row=0, column=1, sticky='ew')
        self.output_d_frame.pack(fill='x')

        self.file_options_d_frame = tk.CTkFrame(self.download_frame)
        self.file_options_d_frame.grid_columnconfigure(0, weight=1)
        self.t_entry = tk.CTkEntry(self.file_options_d_frame)
        self.dotlabel = tk.CTkLabel(self.file_options_d_frame, text=".", font=('',20))
        self.file_format = tk.CTkComboBox(self.file_options_d_frame, values=['m4a','flac','mp3'])
        self.file_format.set('m4a')
        self.t_entry.grid(row=0, column=0, sticky='ew')
        self.dotlabel.grid(row=0,column=1)
        self.file_format.grid(row=0,column=2)
        self.file_options_d_frame.pack(fill='x')

        self.download_button = tk.CTkButton(self.download_frame, text='Download', command=self.down)
        self.download_button.pack(fill='x')

        self.download_frame.pack(fill='x')

        self.progbar = tk.CTkProgressBar(self, height=15)
        self.progbar.set(0)
        self.progbar.pack(fill='x', side='bottom')

    def addcookies(self):
        def loadit(twhich, iftext):
            if twhich == 'text':
                with open(os.path.join(self.tmp, 'cookies.txt'), 'w') as f:
                    f.write(iftext)
            else:
                with open(iftext, 'r') as f:
                    data = f.read()
                with open(os.path.join(self.tmp, 'cookies.txt'), 'w') as f:
                    f.write(data)

        def fromfile():
            if self.zenity_check:
                getdat = sub.run(['zenity','--file-selection'],capture_output=True, text=True)
                dat = getdat.stdout.strip()
            else:
                dat = filedialog.askdirectory()
            if dat:
                loadit('file', dat)
            
        def fromtext():
            def loadloadit():
                r.destroy()
                loadit('text', fttextbox.get('1.0', tk.END))
            w.destroy()
            r = tk.CTkToplevel(self)
            r.title('WaveDown')
            ftlabel = tk.CTkLabel(r, text='Paste Netscape format cookies for youtube', font=('',16))
            ftlabel.pack(pady=20)
            fttextbox = tk.CTkTextbox(r)
            fttextbox.pack(fill='both', expand=True)
            ftframe = tk.CTkFrame(r)
            ftybutton = tk.CTkButton(frame, text='Import', command=lambda: loadloadit())
            ftnbutton = tk.CTkButton(frame, text='Cancel', command=lambda: r.destroy())
            ftybutton.grid(row=0, column=0)
            ftnbutton.grid(row=0, column=1)
            ftframe.pack()

        def loadfromfile():
            w.destroy()
            fromfile()

        w = tk.CTkToplevel(self)
        w.title('WaveDown')
        label = tk.CTkLabel(w, text='In which way do you want to add the cookies.txt?', font=('',16))
        label.pack(pady=20)
        frame = tk.CTkFrame(w)
        ybutton = tk.CTkButton(frame, text='From a file', command=lambda: loadfromfile())
        nbutton = tk.CTkButton(frame, text='From text', command=lambda: fromtext())
        cbutton = tk.CTkButton(frame, text='Cancel', command=lambda: w.destroy())
        ybutton.grid(row=0, column=0)
        nbutton.grid(row=0, column=1)
        cbutton.grid(row=0, column=2)
        frame.pack()

    def close(self):
        def finally_close(var):
            if var:
                w.destroy() # close the toplevel
            self.destroy() # close the main window
            exit(0)

        if self.is_working: # check if the program is still working
            w = tk.CTkToplevel(self)
            w.title('WaveDown')
            label = tk.CTkLabel(w, text='WaveDown is still WORKING.\nAre you SURE you want to leave?', font=('',16))
            label.pack(pady=20)
            frame = tk.CTkFrame(w)
            ybutton = tk.CTkButton(frame, text='Yes', command=lambda: finally_close(True)) # if user still wants to leave, force quit.
            nbutton = tk.CTkButton(frame, text='No', command=lambda: w.destroy()) # close question window if user wants to stay
            ybutton.grid(row=0, column=0)
            nbutton.grid(row=0, column=1)
            frame.pack()
        else:
            finally_close(False) # if not, close without force closing the toplevel as it will close itself with the app.

    def fetch_metadata(self):
        assert self.ytdlp is not None
        self.is_working = True
        tosearch = self.sentry.get()
        if not tosearch:
            self.is_working = False
            return
        args = [self.ytdlp, '--skip-download', '--print',"title", '--print', "uploader", '--print', "id", '--print', "%(upload_date>%Y-%m-%d)s"]
        if os.path.exists(os.path.join(self.tmp, 'cookies.txt')):
            args.append('--cookies')
            args.append(os.path.join(self.tmp, 'cookies.txt'))
        mode = self.modebut.get()
        
        if mode == 'Search by URL':
            args.append(tosearch)
            self.mvid = tosearch
        elif mode == 'Search by Name (YouTube)':
            args.append(f"ytsearch:{tosearch}")

        if not mode == "Search by Name (YTMusic)":
            getdata = sub.run(args, capture_output=True, text=True)
            data = getdata.stdout
        else:
            yt = YTMusic()
            data = yt.search(tosearch, filter='songs', limit=1)
        
        if not data:
            details = "You are either using wrong search mode, or youtube is requiring cookies.\n\nLearn how to get youtube cookies here:\nhttps://rentry.co/howtogetyoutubecookies"
            messagebox.askokcancel(title='WaveDown',message='Something went wrong, did not get the metadata.', detail=details)
            return
        

        self.mtitle = None
        self.mauthor = None
        self.mvid = None
        self.mdate = None
        self.mthumbnail_url = None

        if isinstance(data, str):
            spld = data.split('\n')
            self.mtitle = spld[0] if len(spld) > 0 else "NONE"
            self.mauthor = spld[1] if len(spld) > 1 else "NONE"
            self.mvid = spld[2] if len(spld) > 2 else "NONE"
            self.mdate = spld[3] if len(spld) > 3 else "NONE"
        elif isinstance(data, list):
            toparse = data[0] if len(data) >= 1 else None
            if not toparse:
                return
            self.mtitle = toparse.get('title', "NONE")
            authors = toparse.get('artists', 'NONE')
            self.mauthor = ""
            if isinstance(authors, list):
                for a in authors:
                    auname = a.get('name', 'NONE')
                    self.mauthor += f"{auname}, "
            else:
                self.mauthor = authors
            self.mvid = toparse.get('videoId', 'NONE')
            self.mdate = toparse.get('year')
            thumbnails = toparse.get('thumbnails', "NONE")
            if isinstance(thumbnails, list):
                if len(thumbnails) > 0:
                    self.mthumbnail_url = thumbnails[-1].get('url')

            thumburl = self.mthumbnail_url if self.mthumbnail_url else "none"
            if '=' in thumburl:
                splittu = thumburl.split('=')
                splittu.pop(-1)
                finished = splittu[0] + "=w500-h500-l90-rj"
                self.mthumbnail_url = finished
        
        if not self.mvid:
            self.mvid = ""

        if self.mthumbnail_url:
            os.makedirs(self.tmp, exist_ok=True)
            for file in os.listdir(self.tmp):
                os.remove(os.path.join(self.tmp, file))
            urlretrieve(self.mthumbnail_url, os.path.join(self.tmp, 'thumb.jpg'))
            thumbloc = os.path.join(self.tmp, 'thumb.jpg')
        else:
            sub.run([self.ytdlp,'--skip-download','--write-thumbnail', self.mvid, '-o', os.path.join(self.tmp, 'temp_thumb')])
            thumbloc = os.path.join(self.tmp, 'temp_thumb.webp')
        
        if not self.mthumbnail_url:
            imgtc = Image.open(thumbloc)
            imgrstc = imgtc.resize((1280, 720))
            img_c = imgrstc.crop((280,0,1000,720))
            thumbloc = os.path.join(self.tmp, 'thumb.jpg')
            img_c.save(thumbloc) 

        img = tk.CTkImage(light_image=Image.open(thumbloc), size=(300, 300))
        self.coverlab.configure(image=img)

        self.musictitle.configure(text=f"Title: {self.mtitle}")
        self.t_entry.delete("0", tk.END)
        self.t_entry.insert("0", self.mtitle)
        self.authorlab.configure(text=f"Author/s: {self.mauthor}")
        self.videoidlab.configure(text=f"ID: {self.mvid}")
        if not self.mdate:
            getdate = sub.run([self.ytdlp,'--skip-download','--print','%(upload_date>%Y-%m-%d)s',self.mvid],text=True,capture_output=True)
            self.mdate = getdate.stdout
        self.datelab.configure(text=f"Upload Date: {self.mdate}")
        self.is_working = False

    def down(self):
        self.progbar.after(0,lambda: self.progbar.set(0))
        title = self.t_entry.get()
        savepath = self.fpe.get()
        vid = str(self.mvid) or None
        if not vid:
            messagebox.askokcancel(title='WaveDown',message='No video ID',detail='Make sure to search for a song.')
            return
        fileformat = self.file_format.get()
        ytdargs = [self.ytdlp, '-x', '--audio-format', fileformat, '-o', os.path.join(self.tmp, 'song.%(ext)s'), '--embed-metadata']
        if os.path.exists(os.path.join(self.tmp, 'cookies.txt')):
            ytdargs.append('--cookies')
            ytdargs.append(os.path.join(self.tmp, 'cookies.txt'))
        ytdargs.append(vid)
        
        def load(args):
            proc = sub.Popen(
                args,
                stdout=sub.PIPE,
                stderr=sub.STDOUT,
                text=True,
            )

            is_done = False

            assert proc.stdout is not None
            buffer = ""
            while not is_done:
                char = proc.stdout.read(1)
                if not char and proc.poll() is not None:
                    break

                if char == "\r" or char == "\n":
                    print(buffer)
                    if "cookies" in buffer:
                        ask = messagebox.askokcancel(title='WaveDown', message='ERROR! YouTube requests cookies.', detail='You need to get cookies.\nYou can learn here:\nhttps://rentry.co/howtogetyoutubecookies\nClick OK to go to the website')
                        if ask:
                            webbrowser.open('https://rentry.co/howtogetyoutubecookies')
                            self.download_button.configure(state='normal')
                            self.is_working = False
                            return
                    sbu = buffer.split()
                    perb = sbu[1].strip('%') if len(sbu) > 1 else "none"
                    try:
                        float(perb)
                    except (ValueError, TypeError):
                        buffer = ""
                        continue

                    var = float(perb) / 100.0
                    self.progbar.after(0, lambda: self.progbar.set(var))

                    buffer = ""
                else:
                    buffer += char
            
            self.progbar.after(0, lambda: self.progbar.set(0))
            the.Thread(target=add_cover, daemon=True).start()
            
        def add_cover():
            try:
                acargs = [self.ffmpeg,'-y','-i',os.path.join(self.tmp, f'song.{fileformat.lower()}'),'-i',os.path.join(self.tmp, 'thumb.jpg'),'-map','0','-map','1','-c','copy','-disposition:v:0','attached_pic',f"{os.path.join(savepath, title)}.{fileformat.lower()}"]
                sub.run(acargs)
            finally:
                self.is_working = False
                self.download_button.configure(state='normal')

                os.makedirs(self.tmp, exist_ok=True)
                if os.path.exists(os.path.join(self.tmp, f'song.{fileformat.lower()}')):
                    os.remove(os.path.join(self.tmp, f'song.{fileformat.lower()}'))
        
        if not self.is_working:
            self.is_working = True
            self.download_button.configure(state='disabled')
            the.Thread(target=load, args=(ytdargs,), daemon=True).start()
        
    def get_savepath(self):
        if self.zenity_check:
            getdat = sub.run(['zenity','--file-selection','--directory'],capture_output=True, text=True)
            dat = getdat.stdout.strip()
        else:
            dat = filedialog.askdirectory()
        if not dat:
            dat = "."
        self.fpe.delete("0", tk.END)
        self.fpe.insert("0", dat)


if __name__ == "__main__":
    app = Window()
    app.mainloop()