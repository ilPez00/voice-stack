import os, sys, subprocess, threading, shutil
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "bin")


def find_voice():
    for name in ("voice", "voice-lesson"):
        p = os.path.join(BIN, name)
        if os.path.exists(p):
            return p
    return None




def _to_wsl(path):
    if os.name != "nt":
        return path
    try:
        return subprocess.check_output(["wsl", "wslpath", "-u", path], text=True).strip()
    except Exception:
        return None


def voice_command(script_name, args):
    script = os.path.join(BIN, script_name)
    if os.name == "nt":
        if not shutil.which("wsl"):
            raise RuntimeError("WSL is required to run voice-stack on Windows")
        wsl_script = _to_wsl(script)
        if not wsl_script:
            raise RuntimeError("could not convert path for WSL")
        wsl_args = [_to_wsl(a) if (isinstance(a, str) and os.path.exists(a)) else a for a in args]
        return ["wsl", "bash", wsl_script] + wsl_args
    return [script] + list(args)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice Stack")
        self.geometry("900x620")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self.transcribe_tab = TranscribeTab(nb)
        self.lesson_tab = LessonTab(nb)
        self.say_tab = SayTab(nb)
        self.settings_tab = SettingsTab(nb)
        nb.add(self.transcribe_tab, text="Transcribe")
        nb.add(self.lesson_tab, text="Lessons")
        nb.add(self.say_tab, text="Say")
        nb.add(self.settings_tab, text="Settings")

    def run_cmd(self, cmd, log_widget, btn=None):
        if btn:
            btn.config(state="disabled")

        def worker():
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                out = proc.stdout + (("\nSTDERR:\n" + proc.stderr) if proc.stderr else "")
                if proc.returncode != 0:
                    out += f"\n(exit {proc.returncode})"
            except Exception as e:
                out = f"ERROR: {e}"
            self.after(0, lambda: self._finish(log_widget, out, btn))

        threading.Thread(target=worker, daemon=True).start()

    def _finish(self, log_widget, out, btn):
        log_widget.delete("1.0", "end")
        log_widget.insert("end", out)
        log_widget.see("end")
        if btn:
            btn.config(state="normal")


class TranscribeTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        row = ttk.Frame(self)
        row.pack(fill="x", padx=8, pady=8)
        ttk.Label(row, text="Audio file:").pack(side="left")
        self.file_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.file_var, width=60).pack(side="left", padx=4)
        ttk.Button(row, text="Browse", command=self.browse).pack(side="left")
        self.btn = ttk.Button(row, text="Transcribe", command=self.run)
        self.btn.pack(side="left", padx=4)
        self.log = scrolledtext.ScrolledText(self, wrap="word")
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

    def browse(self):
        p = filedialog.askopenfilename()
        if p:
            self.file_var.set(p)

    def run(self):
        f = self.file_var.get().strip()
        if not f:
            messagebox.showwarning("Missing", "Pick an audio file")
            return
        try:
            cmd = voice_command("voice", ["transcribe", f])
        except RuntimeError as e:
            messagebox.showerror("Unsupported", str(e)); return
        self.master.run_cmd(cmd, self.log, self.btn)


class LessonTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        row = ttk.Frame(self)
        row.pack(fill="x", padx=8, pady=8)
        ttk.Label(row, text="Audio file:").pack(side="left")
        self.file_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.file_var, width=60).pack(side="left", padx=4)
        ttk.Button(row, text="Browse", command=self.browse).pack(side="left")
        self.srt_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row, text="SRT/VTT", variable=self.srt_var).pack(side="left", padx=4)
        self.btn = ttk.Button(row, text="Transcribe lesson", command=self.run)
        self.btn.pack(side="left", padx=4)
        self.log = scrolledtext.ScrolledText(self, wrap="word")
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

    def browse(self):
        p = filedialog.askopenfilename()
        if p:
            self.file_var.set(p)

    def run(self):
        f = self.file_var.get().strip()
        if not f:
            messagebox.showwarning("Missing", "Pick an audio file")
            return
        args = [f]
        if self.srt_var.get():
            args = ["--srt"] + args
        try:
            cmd = voice_command("voice-lesson", args)
        except RuntimeError as e:
            messagebox.showerror("Unsupported", str(e)); return
        self.master.run_cmd(cmd, self.log, self.btn)


class SayTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        row = ttk.Frame(self)
        row.pack(fill="x", padx=8, pady=8)
        ttk.Label(row, text="Text:").pack(side="left")
        self.text_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.text_var, width=70).pack(side="left", padx=4)
        self.btn = ttk.Button(row, text="Say", command=self.run)
        self.btn.pack(side="left", padx=4)
        self.log = scrolledtext.ScrolledText(self, wrap="word", height=8)
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

    def run(self):
        t = self.text_var.get().strip()
        if not t:
            return
        try:
            cmd = voice_command("voice", ["say", t])
        except RuntimeError as e:
            messagebox.showerror("Unsupported", str(e)); return
        self.master.run_cmd(cmd, self.log, self.btn)




class SettingsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        keys = ["VOICE_VENV_PY", "VOICE_WHISTLE_WEIGHTS", "VOICE_ESPEAK", "VOICE_HERMES_URL", "VOICE_LESSONS_DIR"]
        frm = ttk.Frame(self); frm.pack(fill="x", padx=8, pady=8)
        existing = {}
        if os.path.exists(self.env_path):
            for line in open(self.env_path):
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    existing[k] = v
        self.vars = {}
        for k in keys:
            row = ttk.Frame(frm); row.pack(fill="x", pady=2)
            ttk.Label(row, text=k, width=22).pack(side="left")
            v = tk.StringVar(value=existing.get(k, os.environ.get(k, "")))
            self.vars[k] = v
            ttk.Entry(row, textvariable=v, width=60).pack(side="left", padx=4)
        ttk.Button(frm, text="Salva .env", command=self.save).pack(pady=8, anchor="w")
        self.status = tk.StringVar(value="")
        ttk.Label(frm, textvariable=self.status).pack(anchor="w")
        guide = "Guida: installa con voice-install, poi imposta i path se necessario. Windows richiede WSL."
        ttk.Label(self, text=guide, justify="left").pack(anchor="w", padx=8, pady=8)

    def save(self):
        lines = [f"{k}={v.get().strip()}" for k, v in self.vars.items()]
        with open(self.env_path, "w") as f:
            f.write("\n".join(lines) + "\n")
        self.status.set(f"salvato: {self.env_path}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
