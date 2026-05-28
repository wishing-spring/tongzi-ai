# -*- coding: utf-8 -*-
"""Child Dialog Window — Tkinter GUI · zero deps · v0.6 dream-speak + recall"""
import sys, os, threading, time
)
from .lingxi_fusion import LingxiFusion

try:
    import tkinter as tk
    from tkinter import scrolledtext
except ImportError:
    print("tkinter required (bundled with Python; reinstall with tcl/tk if missing)")
    sys.exit(1)


class ChildWindow:
    def __init__(self):
        self.child = LingxiFusion()
        self.running = True
        self._last_share_tick = 0

        # load saved state
        if os.path.exists('child_state.json'):
            loaded = self.child.load('child_state.json')
            if loaded:
                print(f'[awake] tick={self.child.tick}')

        # boot dream
        self.child.dream(5, quiet=True)

        # ── window setup ──
        self.root = tk.Tk()
        self.root.title("Child · age 10")
        self.root.geometry("520x620")
        self.root.configure(bg='#f5f0e8')
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # mood bar
        title_frame = tk.Frame(self.root, bg='#e8d5b7', height=50)
        title_frame.pack(fill='x')
        self.mood_label = tk.Label(title_frame, text='😴 Dreaming...',
                                    font=('Segoe UI', 14), bg='#e8d5b7', fg='#5d4037')
        self.mood_label.pack(pady=10)

        # chat display
        chat_frame = tk.Frame(self.root, bg='#f5f0e8')
        chat_frame.pack(fill='both', expand=True, padx=12, pady=(12, 0))
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame, wrap='word', font=('Segoe UI', 11),
            bg='#fffef9', fg='#3e2723', bd=0, padx=12, pady=12,
            state='disabled', height=18
        )
        self.chat_area.pack(fill='both', expand=True)

        # input bar
        input_frame = tk.Frame(self.root, bg='#f5f0e8')
        input_frame.pack(fill='x', padx=12, pady=12)
        self.input_box = tk.Entry(input_frame, font=('Segoe UI', 13),
                                   bg='white', fg='#3e2723', bd=1,
                                   relief='solid', insertbackground='#8d6e63')
        self.input_box.pack(side='left', fill='x', expand=True, ipady=6, padx=(0, 8))
        self.input_box.bind('<Return>', self._on_send)
        self.input_box.focus_set()

        send_btn = tk.Button(input_frame, text='Send', command=self._on_send_btn,
                             font=('Segoe UI', 11), bg='#a1887f', fg='white',
                             bd=0, padx=16, pady=6, cursor='hand2',
                             activebackground='#8d6e63')
        send_btn.pack(side='right')

        # status bar
        status_frame = tk.Frame(self.root, bg='#e8d5b7', height=28)
        status_frame.pack(fill='x', side='bottom')
        self.status_label = tk.Label(status_frame,
                                      text='Ctrl+Enter newline · Enter to send',
                                      font=('Segoe UI', 9), bg='#e8d5b7', fg='#8d6e63')
        self.status_label.pack(pady=4)

        # welcome message
        self._append('Tongzi', 'Hi! I am Tongzi, ten years old~', 'system')

        # ── background dream loop ──
        self._dream_thread = threading.Thread(target=self._dream_loop, daemon=True)
        self._dream_thread.start()
        self._update_status()

    def _dream_loop(self):
        """Low-frequency dream — 2s per breath, occasional dream-speak"""
        ticks = 0
        while self.running:
            with threading.Lock():
                try:
                    self.child.dream(1, quiet=True)
                    ticks += 1
                except Exception:
                    pass
            if ticks % 15 == 0 and self.child.dream_synthesis:
                share = self.child.dream_share()
                if share:
                    self.root.after(0, lambda s=share: self._append('Tongzi', f'💭 {s}', 'dream'))
            time.sleep(2.0)

    def _update_status(self):
        """Refresh mood display"""
        if not self.running:
            return
        mood = self.child.xiaotianyuan.get('mood', '安')
        mood_map = {'安': '😊 Calm', '乐': '😄 Happy', '哀': '😢 Sad',
                     '怒': '😠 Angry', '好奇': '🤔 Curious'}
        self.mood_label.config(text=mood_map.get(mood, f'😊 {mood}'))
        self.root.after(3000, self._update_status)

    def _on_send_btn(self):
        self._on_send(None)

    def _on_send(self, event):
        text = self.input_box.get().strip()
        if not text:
            return
        self.input_box.delete(0, 'end')

        if text == '/state':
            edges = sum(len(v) for v in self.child.pool.cooccur.values())
            grown = len([b for _, b in self.child.rules.branches.items()
                        if b.category == 'HARVESTED'])
            self._append('System',
                        f'Stars 195 · Rules {len(self.child.rules.branches)}(+{grown}) · Edges {edges}',
                        'system')
            return
        if text == '/dream':
            mems = self.child.dream_recall(3)
            if mems:
                for m in mems:
                    self._append('System', f'💤 {m}', 'system')
            return

        self._append('You', text, 'user')

        dream_kw = {'梦到', '梦什么', '做什么梦', '在想什么', '在想啥', '想什么', '刚才'}
        if any(kw in text for kw in dream_kw):
            self._handle_dream_question(text)
            return

        def _respond():
            with threading.Lock():
                result = self.child.receive(text)
                reply = self.child.speak(result)
            if reply:
                self.root.after(0, lambda: self._append('Tongzi', reply, 'child'))
                self.root.after(0, lambda: self._flash_mood())
            else:
                self.root.after(0, lambda: self._append('Tongzi', 'Hmm...', 'child'))

        threading.Thread(target=_respond, daemon=True).start()

    def _handle_dream_question(self, text):
        """Recall: share dream memories"""
        mems = self.child.dream_recall(2)
        if mems:
            reply = 'I ' + mems[0] if mems[0].startswith('梦') else mems[0]
        else:
            reply = "I didn't dream much just now..."
        self._append('Tongzi', reply, 'child')

    def _flash_mood(self):
        mood = self.child.xiaotianyuan.get('mood', '安')
        mood_map = {'安': '😊 Calm', '乐': '😄 Happy', '哀': '😢 Sad',
                     '怒': '😠 Angry', '好奇': '🤔 Curious'}
        self.mood_label.config(text=mood_map.get(mood, f'😊 {mood}'))

    def _append(self, speaker, msg, tag):
        self.chat_area.config(state='normal')
        FONT = ('Segoe UI', 11)
        FONT_B = ('Segoe UI', 11, 'bold')
        FONT_I = ('Segoe UI', 10, 'italic')
        FONT_S = ('Segoe UI', 9)

        if tag == 'user':
            self.chat_area.insert('end', f'\n{speaker}: ', 'user_name')
            self.chat_area.insert('end', msg + '\n', 'user_msg')
        elif tag == 'child':
            self.chat_area.insert('end', f'\n{speaker}: ', 'child_name')
            self.chat_area.insert('end', msg + '\n', 'child_msg')
        elif tag == 'dream':
            self.chat_area.insert('end', f'\n{speaker}: ', 'dream_name')
            self.chat_area.insert('end', msg + '\n', 'dream_msg')
        else:
            self.chat_area.insert('end', f'\n[{msg}]\n', 'system_msg')

        self.chat_area.config(state='disabled')
        self.chat_area.see('end')

    def _on_close(self):
        self.running = False
        self.child.save('child_state.json')
        self.root.destroy()

    def run(self):
        self.chat_area.tag_configure('user_name', foreground='#1565c0',
                                      font=('Segoe UI', 11, 'bold'))
        self.chat_area.tag_configure('user_msg', foreground='#333333',
                                      font=('Segoe UI', 11))
        self.chat_area.tag_configure('child_name', foreground='#c62828',
                                      font=('Segoe UI', 11, 'bold'))
        self.chat_area.tag_configure('child_msg', foreground='#3e2723',
                                      font=('Segoe UI', 11))
        self.chat_area.tag_configure('dream_name', foreground='#6a1b9a',
                                      font=('Segoe UI', 11, 'bold'))
        self.chat_area.tag_configure('dream_msg', foreground='#7b1fa2',
                                      font=('Segoe UI', 10, 'italic'))
        self.chat_area.tag_configure('system_msg', foreground='#9e9e9e',
                                      font=('Segoe UI', 9))
        self.root.mainloop()


def launch():
    """Entry point for package-level start(gui=True)"""
    app = ChildWindow()
    app.run()


if __name__ == '__main__':
    launch()
