"""
Duolingo-like app em Python usando Tkinter (arquivo único)
Arquivo: Duolingo_Clone_Tkinter.py

Funcionalidades incluídas (versão inicial):
- Cadastro / login de usuário (SQLite)
- Dashboard com XP, nível, streak e progresso de lições
- Sistema de lições (várias unidades) com exercícios: múltipla escolha e digitação
- Sistema simples de SRS (repetição espaçada) para agendar revisões
- Histórico de respostas e salvamento de progresso local
- Exportar/Importar perfil (JSON)

Requisitos: Python 3.8+ (usa apenas stdlib)
Como executar:
$ python Duolingo_Clone_Tkinter.py

Como gerar um executável (opcional):
$ pip install pyinstaller
$ pyinstaller --onefile Duolingo_Clone_Tkinter.py

OBS: Este projeto é um protótipo educativo — adaptar e incrementar será necessário para ter todos os recursos do Duolingo.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from datetime import datetime, timedelta
import random
import json
import os

# ------------------------------
# Banco de dados local (SQLite)
# ------------------------------
DB_FILE = 'duo_clone.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Usuários
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        streak INTEGER DEFAULT 0,
        last_login TEXT
    )
    ''')

    # Lições / Cards
    c.execute('''
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit INTEGER,
        title TEXT,
        type TEXT,
        prompt TEXT,
        choices TEXT,
        answer TEXT
    )
    ''')

    # Progresso do usuário por lição
    c.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        lesson_id INTEGER,
        correct INTEGER DEFAULT 0,
        attempts INTEGER DEFAULT 0,
        next_review TEXT,
        interval INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(lesson_id) REFERENCES lessons(id)
    )
    ''')

    # Histórico de respostas
    c.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        lesson_id INTEGER,
        correct INTEGER,
        when_ts TEXT,
        answer TEXT
    )
    ''')

    conn.commit()
    conn.close()

# Se banco novo, inserir lições de exemplo
def seed_lessons():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM lessons')
    if c.fetchone()[0] == 0:
        sample = [
            (1, 'Saudações: Olá', 'mcq', 'Como se diz "Olá" em inglês?', json.dumps(['Hello','Goodbye','Please','Thanks']), 'Hello'),
            (1, 'Saudações: Obrigado', 'mcq', 'Como se diz "Obrigado" em inglês?', json.dumps(['Sorry','Thanks','Yes','No']), 'Thanks'),
            (1, 'Verbo to be: I am', 'type', 'Traduza: "Eu sou" (em inglês)', None, 'I am'),
            (2, 'Objetos: Mesa', 'mcq', 'Qual a tradução de "mesa"?', json.dumps(['Table','Chair','Window','Door']), 'Table'),
            (2, 'Números: Um', 'type', 'Traduza: "Um"', None, 'One'),
            (3, 'Frases: Como vai?', 'mcq', 'Como se diz "Como vai?" em inglês?', json.dumps(['How are you?','See you','What','Where']), 'How are you?'),
        ]
        c.executemany('INSERT INTO lessons (unit, title, type, prompt, choices, answer) VALUES (?,?,?,?,?,?)', sample)
        conn.commit()
    conn.close()

# ------------------------------
# Modelo de dados e lógica
# ------------------------------
class DataStore:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row

    def find_user(self, username):
        c = self.conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        return c.fetchone()

    def create_user(self, username, password):
        c = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        try:
            c.execute('INSERT INTO users (username,password,last_login) VALUES (?,?,?)', (username, password, now))
            self.conn.commit()
            return c.lastrowid
        except sqlite3.IntegrityError:
            return None

    def verify_user(self, username, password):
        row = self.find_user(username)
        if row and row['password'] == password:
            return row
        return None

    def update_login(self, user_id):
        c = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute('UPDATE users SET last_login = ? WHERE id = ?', (now, user_id))
        self.conn.commit()

    def get_lessons(self, unit=None):
        c = self.conn.cursor()
        if unit is None:
            c.execute('SELECT * FROM lessons ORDER BY unit, id')
        else:
            c.execute('SELECT * FROM lessons WHERE unit = ? ORDER BY id', (unit,))
        return c.fetchall()

    def get_lesson(self, lesson_id):
        c = self.conn.cursor()
        c.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
        return c.fetchone()

    def ensure_progress(self, user_id, lesson_id):
        c = self.conn.cursor()
        c.execute('SELECT * FROM progress WHERE user_id=? AND lesson_id=?', (user_id, lesson_id))
        row = c.fetchone()
        if not row:
            c.execute('INSERT INTO progress (user_id, lesson_id) VALUES (?,?)', (user_id, lesson_id))
            self.conn.commit()
            c.execute('SELECT * FROM progress WHERE user_id=? AND lesson_id=?', (user_id, lesson_id))
            row = c.fetchone()
        return row

    def record_result(self, user_id, lesson_id, correct, answer_text):
        c = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute('INSERT INTO history (user_id, lesson_id, correct, when_ts, answer) VALUES (?,?,?,?,?)', (user_id, lesson_id, int(correct), now, answer_text))

        # atualizar progress e SRS simples
        c.execute('SELECT * FROM progress WHERE user_id=? AND lesson_id=?', (user_id, lesson_id))
        p = c.fetchone()
        if not p:
            c.execute('INSERT INTO progress (user_id, lesson_id, correct, attempts) VALUES (?,?,?,?)', (user_id, lesson_id, int(correct), 1))
        else:
            attempts = p['attempts'] + 1
            corrects = p['correct'] + (1 if correct else 0)
            # SRS: se correto, aumentar intervalo (dias) *2, se errado, reset para 1
            interval = p['interval']
            if correct:
                interval = max(1, interval) * 2
            else:
                interval = 1
            next_review = (datetime.utcnow() + timedelta(days=interval)).isoformat()
            c.execute('''UPDATE progress SET correct=?, attempts=?, next_review=?, interval=? WHERE id=?''', (corrects, attempts, next_review, interval, p['id']))

        # adicionar XP e possíveis nível
        c.execute('SELECT xp, level FROM users WHERE id=?', (user_id,))
        u = c.fetchone()
        xp = u['xp'] + (10 if correct else 2)
        level = u['level']
        # simples: subir de nível a cada 100 XP
        while xp >= level * 100:
            level += 1
        c.execute('UPDATE users SET xp=?, level=? WHERE id=?', (xp, level, user_id))

        self.conn.commit()

    def get_user_progress_summary(self, user_id):
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*) as total FROM lessons')
        total = c.fetchone()['total']
        c.execute('SELECT COUNT(DISTINCT lesson_id) as done FROM history WHERE user_id=? AND correct=1', (user_id,))
        done = c.fetchone()['done']
        return {'total_lessons': total, 'completed': done}

    def get_due_lessons(self, user_id):
        c = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute("SELECT l.* FROM lessons l JOIN progress p ON l.id=p.lesson_id WHERE p.user_id=? AND (p.next_review IS NULL OR p.next_review<=?) ORDER BY l.unit", (user_id, now))
        return c.fetchall()

    def export_user(self, user_id, filepath):
        c = self.conn.cursor()
        c.execute('SELECT * FROM users WHERE id=?', (user_id,))
        user = dict(c.fetchone())
        c.execute('SELECT * FROM history WHERE user_id=?', (user_id,))
        history = [dict(r) for r in c.fetchall()]
        c.execute('SELECT * FROM progress WHERE user_id=?', (user_id,))
        progress = [dict(r) for r in c.fetchall()]
        data = {'user': user, 'history': history, 'progress': progress}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_user(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        user = data.get('user')
        c = self.conn.cursor()
        try:
            c.execute('INSERT INTO users (username,password,xp,level,streak,last_login) VALUES (?,?,?,?,?,?)',
                      (user['username'], user.get('password',''), user.get('xp',0), user.get('level',1), user.get('streak',0), user.get('last_login')))
            new_id = c.lastrowid
        except sqlite3.IntegrityError:
            # usuario já existe, encontrar id
            c.execute('SELECT id FROM users WHERE username=?', (user['username'],))
            new_id = c.fetchone()['id']
        # importar progresso e histórico (associa ao novo_id)
        for p in data.get('progress', []):
            try:
                c.execute('INSERT INTO progress (user_id,lesson_id,correct,attempts,next_review,interval) VALUES (?,?,?,?,?,?)',
                          (new_id, p['lesson_id'], p.get('correct',0), p.get('attempts',0), p.get('next_review'), p.get('interval',0)))
            except Exception:
                pass
        for h in data.get('history', []):
            try:
                c.execute('INSERT INTO history (user_id,lesson_id,correct,when_ts,answer) VALUES (?,?,?,?,?)',
                          (new_id, h['lesson_id'], h.get('correct',0), h.get('when_ts'), h.get('answer','')))
            except Exception:
                pass
        self.conn.commit()
        return new_id

# ------------------------------
# Interface Gráfica (Tkinter)
# ------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Duolingo Clone - Tkinter')
        self.geometry('900x600')
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        self.store = DataStore()
        self.user = None  # linha do usuário logado

        # frames
        self.container = ttk.Frame(self)
        self.container.pack(fill='both', expand=True)

        self.frames = {}
        for F in (LoginFrame, RegisterFrame, DashboardFrame, LessonFrame, ProfileFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('LoginFrame')

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()

    def login(self, username, password):
        row = self.store.verify_user(username, password)
        if row:
            self.user = row
            self.store.update_login(row['id'])
            messagebox.showinfo('Sucesso', f'Bem vindo, {username}!')
            self.show_frame('DashboardFrame')
        else:
            messagebox.showerror('Erro', 'Usuário ou senha inválidos')

    def register(self, username, password):
        uid = self.store.create_user(username, password)
        if uid:
            messagebox.showinfo('Sucesso', 'Usuário criado. Faça login.')
            self.show_frame('LoginFrame')
        else:
            messagebox.showerror('Erro', 'Nome de usuário já existe')

# ------------------------------
# Frames
# ------------------------------
class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build()

    def build(self):
        pad = 12
        frm = ttk.Frame(self)
        frm.place(relx=0.5, rely=0.4, anchor='center')

        ttk.Label(frm, text='Duolingo Clone', font=('Helvetica', 20, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(frm, text='Usuário').grid(row=1, column=0, sticky='w')
        self.user_entry = ttk.Entry(frm)
        self.user_entry.grid(row=1, column=1)
        ttk.Label(frm, text='Senha').grid(row=2, column=0, sticky='w')
        self.pass_entry = ttk.Entry(frm, show='*')
        self.pass_entry.grid(row=2, column=1)

        ttk.Button(frm, text='Entrar', command=self.try_login).grid(row=3, column=0, columnspan=2, pady=pad)
        ttk.Button(frm, text='Criar conta', command=lambda: self.controller.show_frame('RegisterFrame')).grid(row=4, column=0, columnspan=2)

    def try_login(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()
        if not u or not p:
            messagebox.showwarning('Aviso', 'Preencha usuário e senha')
            return
        self.controller.login(u, p)

class RegisterFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build()

    def build(self):
        frm = ttk.Frame(self)
        frm.place(relx=0.5, rely=0.4, anchor='center')
        ttk.Label(frm, text='Criar Conta', font=('Helvetica', 18, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(frm, text='Usuário').grid(row=1, column=0, sticky='w')
        self.user_entry = ttk.Entry(frm)
        self.user_entry.grid(row=1, column=1)
        ttk.Label(frm, text='Senha').grid(row=2, column=0, sticky='w')
        self.pass_entry = ttk.Entry(frm, show='*')
        self.pass_entry.grid(row=2, column=1)
        ttk.Button(frm, text='Criar', command=self.create).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frm, text='Voltar', command=lambda: self.controller.show_frame('LoginFrame')).grid(row=4, column=0, columnspan=2)

    def create(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()
        if not u or not p:
            messagebox.showwarning('Aviso', 'Preencha usuário e senha')
            return
        self.controller.register(u, p)

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build()

    def build(self):
        header = ttk.Frame(self)
        header.pack(fill='x', pady=8)
        self.lbl_user = ttk.Label(header, text='Usuário: -')
        self.lbl_user.pack(side='left', padx=8)
        ttk.Button(header, text='Perfil', command=lambda: self.controller.show_frame('ProfileFrame')).pack(side='right', padx=8)
        ttk.Button(header, text='Sair', command=self.logout).pack(side='right')

        self.content = ttk.Frame(self)
        self.content.pack(fill='both', expand=True, padx=12, pady=12)

        # Esquerda: lista de lições / unidades
        left = ttk.Frame(self.content)
        left.pack(side='left', fill='y', padx=(0,12))
        ttk.Label(left, text='Unidades').pack(anchor='w')
        self.units_list = tk.Listbox(left, height=10)
        self.units_list.pack()
        self.units_list.bind('<<ListboxSelect>>', self.unit_selected)

        # Centro: progresso e cards
        center = ttk.Frame(self.content)
        center.pack(side='left', fill='both', expand=True)
        self.progress_var = tk.DoubleVar()
        ttk.Label(center, text='Progresso').pack(anchor='w')
        self.progress = ttk.Progressbar(center, variable=self.progress_var, maximum=100)
        self.progress.pack(fill='x')

        self.xp_label = ttk.Label(center, text='XP: 0 | Level: 1 | Streak: 0')
        self.xp_label.pack(anchor='w', pady=8)

        ttk.Button(center, text='Iniciar lição disponível', command=self.start_due_lesson).pack(pady=6)
        ttk.Button(center, text='Ver todas lições', command=self.list_all_lessons).pack(pady=6)

        # Direita: próximo exercício
        right = ttk.Frame(self.content, width=220)
        right.pack(side='right', fill='y')
        ttk.Label(right, text='Opções').pack(anchor='w')
        ttk.Button(right, text='Exportar Perfil', command=self.export_profile).pack(fill='x', pady=4)
        ttk.Button(right, text='Importar Perfil', command=self.import_profile).pack(fill='x', pady=4)

    def on_show(self):
        if not self.controller.user:
            self.controller.show_frame('LoginFrame')
            return
        u = self.controller.user
        self.lbl_user.config(text=f"Usuário: {u['username']}")
        self.update_stats()
        self.populate_units()

    def update_stats(self):
        u = self.controller.user
        summary = self.controller.store.get_user_progress_summary(u['id'])
        total = summary['total_lessons']
        done = summary['completed'] or 0
        pct = (done / total) * 100 if total else 0
        self.progress_var.set(pct)
        self.xp_label.config(text=f"XP: {u['xp']} | Level: {u['level']} | Streak: {u['streak']}")

    def populate_units(self):
        lessons = self.controller.store.get_lessons()
        units = {}
        for l in lessons:
            units.setdefault(l['unit'], []).append(l)
        self.units_list.delete(0, 'end')
        for unit in sorted(units.keys()):
            self.units_list.insert('end', f'Unidade {unit} ({len(units[unit])} lições)')
        self._units_map = units

    def unit_selected(self, event):
        sel = event.widget.curselection()
        if not sel: return
        idx = sel[0]
        key = sorted(self._units_map.keys())[idx]
        lessons = self._units_map[key]
        # abrir lista de lições em janela
        win = tk.Toplevel(self)
        win.title(f'Unidade {key}')
        for l in lessons:
            btn = ttk.Button(win, text=f"{l['title']}", command=lambda lid=l['id']: self.open_lesson(lid))
            btn.pack(fill='x', padx=6, pady=4)

    def open_lesson(self, lesson_id):
        self.controller.frames['LessonFrame'].load_lesson(lesson_id)
        self.controller.show_frame('LessonFrame')

    def list_all_lessons(self):
        lessons = self.controller.store.get_lessons()
        win = tk.Toplevel(self)
        win.title('Todas as lições')
        for l in lessons:
            ttk.Button(win, text=f"U{l['unit']} - {l['title']}", command=lambda lid=l['id']: self.open_lesson(lid)).pack(fill='x', padx=6, pady=3)

    def start_due_lesson(self):
        due = self.controller.store.get_due_lessons(self.controller.user['id'])
        if not due:
            messagebox.showinfo('Nada para revisar', 'Nenhuma lição com revisão pendente. Você pode estudar lições novas.')
            return
        lesson = due[0]
        self.controller.frames['LessonFrame'].load_lesson(lesson['id'])
        self.controller.show_frame('LessonFrame')

    def export_profile(self):
        uid = self.controller.user['id']
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json')])
        if path:
            self.controller.store.export_user(uid, path)
            messagebox.showinfo('Exportado', 'Perfil exportado com sucesso')

    def import_profile(self):
        path = filedialog.askopenfilename(filetypes=[('JSON','*.json')])
        if path:
            new_id = self.controller.store.import_user(path)
            messagebox.showinfo('Importado', f'Perfil importado com sucesso (user id {new_id})')

    def logout(self):
        self.controller.user = None
        self.controller.show_frame('LoginFrame')

class LessonFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.lesson = None
        self.build()

    def build(self):
        top = ttk.Frame(self)
        top.pack(fill='x')
        ttk.Button(top, text='Voltar', command=lambda: self.controller.show_frame('DashboardFrame')).pack(side='left', padx=8)
        self.lbl_title = ttk.Label(top, text='Lição: -', font=('Helvetica', 16, 'bold'))
        self.lbl_title.pack(side='left', padx=12)

        self.body = ttk.Frame(self)
        self.body.pack(fill='both', expand=True, padx=12, pady=12)

        # prompt
        self.prompt_label = ttk.Label(self.body, text='', wraplength=700, font=('Helvetica', 14))
        self.prompt_label.pack(pady=8)

        self.answer_var = tk.StringVar()
        self.entry = ttk.Entry(self.body, textvariable=self.answer_var, font=('Helvetica', 14))

        self.choice_buttons = []

        self.submit_btn = ttk.Button(self.body, text='Enviar', command=self.submit_answer)

        self.feedback = ttk.Label(self.body, text='')

    def load_lesson(self, lesson_id):
        l = self.controller.store.get_lesson(lesson_id)
        if not l:
            messagebox.showerror('Erro', 'Lição não encontrada')
            return
        self.lesson = l
        self.lbl_title.config(text=f"U{l['unit']} - {l['title']}")
        self.prompt_label.config(text=l['prompt'])
        # limpar
        for b in self.choice_buttons:
            b.destroy()
        self.choice_buttons = []
        self.entry.pack_forget()
        self.submit_btn.pack_forget()
        self.feedback.config(text='')

        if l['type'] == 'mcq':
            choices = json.loads(l['choices']) if l['choices'] else []
            random.shuffle(choices)
            for ch in choices:
                b = ttk.Button(self.body, text=ch, command=lambda c=ch: self.choose_answer(c))
                b.pack(fill='x', pady=6)
                self.choice_buttons.append(b)
        elif l['type'] == 'type':
            self.answer_var.set('')
            self.entry.pack(pady=8)
            self.submit_btn.pack()

    def choose_answer(self, choice):
        correct = choice.strip().lower() == self.lesson['answer'].strip().lower()
        self.handle_result(correct, choice)

    def submit_answer(self):
        ans = self.answer_var.get().strip()
        if not ans:
            messagebox.showwarning('Aviso', 'Digite sua resposta')
            return
        correct = ans.lower() == self.lesson['answer'].strip().lower()
        self.handle_result(correct, ans)

    def handle_result(self, correct, answer_text):
        uid = self.controller.user['id']
        self.controller.store.ensure_progress(uid, self.lesson['id'])
        self.controller.store.record_result(uid, self.lesson['id'], correct, answer_text)
        # atualizar usuário na memória
        self.controller.user = self.controller.store.find_user(self.controller.user['username'])
        if correct:
            self.feedback.config(text='✔ Correto! XP ganho.', foreground='green')
        else:
            self.feedback.config(text=f'✖ Errado. Resposta correta: {self.lesson["answer"]}', foreground='red')
        self.feedback.pack(pady=8)
        # mostrar botão continuar
        if hasattr(self, 'next_btn'):
            try: self.next_btn.destroy()
            except: pass
        self.next_btn = ttk.Button(self.body, text='Próxima', command=self.next_lesson)
        self.next_btn.pack(pady=6)

    def next_lesson(self):
        # pegar próxima lição por unidade ou próxima pendente
        uid = self.controller.user['id']
        lessons = self.controller.store.get_lessons()
        ids = [l['id'] for l in lessons]
        try:
            idx = ids.index(self.lesson['id'])
            next_id = ids[idx+1] if idx+1 < len(ids) else None
        except ValueError:
            next_id = None
        if next_id:
            self.load_lesson(next_id)
        else:
            messagebox.showinfo('Fim', 'Você completou todas as lições disponíveis.')
            self.controller.show_frame('DashboardFrame')

class ProfileFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build()

    def build(self):
        top = ttk.Frame(self)
        top.pack(fill='x')
        ttk.Button(top, text='Voltar', command=lambda: self.controller.show_frame('DashboardFrame')).pack(side='left', padx=8)
        ttk.Label(top, text='Perfil', font=('Helvetica', 16, 'bold')).pack(side='left', padx=12)

        self.body = ttk.Frame(self)
        self.body.pack(fill='both', expand=True, padx=12, pady=12)

        self.lbl_info = ttk.Label(self.body, text='-')
        self.lbl_info.pack(anchor='w')

        ttk.Button(self.body, text='Resetar progresso (apagar histórico)', command=self.reset_progress).pack(pady=6)

    def on_show(self):
        if not self.controller.user:
            self.controller.show_frame('LoginFrame')
            return
        u = self.controller.user
        self.lbl_info.config(text=f"Usuário: {u['username']}\nXP: {u['xp']}\nLevel: {u['level']}\nStreak: {u['streak']}")

    def reset_progress(self):
        if messagebox.askyesno('Confirmar', 'Deseja apagar todo o seu histórico e progresso?'):
            c = self.controller.store.conn.cursor()
            c.execute('DELETE FROM history WHERE user_id=?', (self.controller.user['id'],))
            c.execute('DELETE FROM progress WHERE user_id=?', (self.controller.user['id'],))
            c.execute('UPDATE users SET xp=?, level=?, streak=? WHERE id=?', (0,1,0,self.controller.user['id']))
            self.controller.store.conn.commit()
            self.controller.user = self.controller.store.find_user(self.controller.user['username'])
            messagebox.showinfo('Pronto', 'Progresso resetado')
            self.controller.show_frame('DashboardFrame')

# ------------------------------
# Inicialização
# ------------------------------

def main():
    init_db()
    seed_lessons()
    app = App()
    app.mainloop()

if __name__ == '__main__':
    main()
