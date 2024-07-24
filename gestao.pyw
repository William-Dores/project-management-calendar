import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime
import pandas as pd

# Inicializando o DataFrame
agenda = pd.DataFrame(columns=["Data", "Reunião", "Realizada"])
alteracoes_nao_salvas = False

# Função para adicionar reuniões
def adicionar_reuniao():
    global alteracoes_nao_salvas
    data = entry_data.get()
    descricao = entry_descricao.get()
    try:
        data = datetime.datetime.strptime(data, "%d/%m/%Y").date()
        nova_reuniao = {"Data": data, "Reunião": descricao, "Realizada": False}
        global agenda
        agenda = pd.concat([agenda, pd.DataFrame([nova_reuniao])], ignore_index=True)
        agenda = agenda.sort_values(by="Data").reset_index(drop=True)
        alteracoes_nao_salvas = True
        messagebox.showinfo("Sucesso", f"Reunião adicionada: {data} - {descricao}")
        entry_data.delete(0, tk.END)
        entry_descricao.delete(0, tk.END)
        visualizar_reunioes()
    except ValueError:
        messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")

# Função para visualizar as reuniões
def visualizar_reunioes():
    for row in tree.get_children():
        tree.delete(row)
    hoje = datetime.date.today()
    for index, row in agenda.iterrows():
        if row["Data"] == hoje:
            color = "blue"
        else:
            color = "green" if row["Realizada"] else "red"
        tree.insert("", "end", values=(row["Data"].strftime("%d/%m/%Y"), row["Reunião"], "Sim" if row["Realizada"] else "Não"), tags=(color,))
    tree.tag_configure('blue', background='lightblue')
    tree.tag_configure('green', background='lightgreen')
    tree.tag_configure('red', background='lightcoral')

# Função para marcar reunião como realizada
def marcar_realizada():
    global alteracoes_nao_salvas
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Selecione uma reunião para marcar como realizada.")
        return
    item = tree.item(selected_item)
    data_str, descricao, realizada_str = item['values']
    data = datetime.datetime.strptime(data_str, "%d/%m/%Y").date()
    global agenda
    index = agenda[(agenda["Data"] == data) & (agenda["Reunião"] == descricao)].index[0]
    agenda.at[index, "Realizada"] = True
    alteracoes_nao_salvas = True
    visualizar_reunioes()

# Função para excluir reunião
def excluir_reuniao():
    global alteracoes_nao_salvas
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Selecione uma reunião para excluir.")
        return
    item = tree.item(selected_item)
    data_str, descricao, realizada_str = item['values']
    data = datetime.datetime.strptime(data_str, "%d/%m/%Y").date()
    global agenda
    agenda = agenda.drop(agenda[(agenda["Data"] == data) & (agenda["Reunião"] == descricao)].index)
    alteracoes_nao_salvas = True
    visualizar_reunioes()

# Função para salvar as reuniões em um arquivo de texto
def salvar_agenda():
    global alteracoes_nao_salvas
    agenda.to_csv("agenda.txt", index=False, sep='|')
    alteracoes_nao_salvas = False
    messagebox.showinfo("Sucesso", "Agenda salva com sucesso em agenda.txt")

# Função para carregar as reuniões de um arquivo de texto
def carregar_agenda():
    global agenda, alteracoes_nao_salvas
    try:
        agenda = pd.read_csv("agenda.txt", sep='|', parse_dates=["Data"])
        agenda["Data"] = agenda["Data"].dt.date
        agenda = agenda.sort_values(by="Data").reset_index(drop=True)
        visualizar_reunioes()
        alteracoes_nao_salvas = False
        messagebox.showinfo("Sucesso", "Agenda carregada com sucesso de agenda.txt")
        verificar_atividades_do_dia()
    except FileNotFoundError:
        messagebox.showerror("Erro", "Arquivo agenda.txt não encontrado")

# Função para verificar atividades do dia
def verificar_atividades_do_dia():
    hoje = datetime.date.today()
    atividades_do_dia = agenda[agenda["Data"] == hoje]
    if atividades_do_dia.empty:
        messagebox.showinfo("Atividades do Dia", "Não há atividades para hoje.")
    else:
        atividades = "\n".join([f"{row['Data'].strftime('%d/%m/%Y')} - {row['Reunião']}" for index, row in atividades_do_dia.iterrows()])
        messagebox.showinfo("Atividades do Dia", f"Atividades para hoje:\n{atividades}")

# Função para verificar alterações não salvas antes de fechar a aplicação
def on_closing():
    if alteracoes_nao_salvas:
        if messagebox.askyesno("Salvar", "Há alterações não salvas. Deseja salvar antes de sair?"):
            salvar_agenda()
    root.destroy()

# Função para editar a descrição de uma reunião
def editar_descricao():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Selecione uma reunião para editar.")
        return
    item = tree.item(selected_item)
    data_str, descricao, realizada_str = item['values']
    data = datetime.datetime.strptime(data_str, "%d/%m/%Y").date()
    nova_descricao = entry_descricao.get()
    global agenda
    index = agenda[(agenda["Data"] == data) & (agenda["Reunião"] == descricao)].index[0]
    agenda.at[index, "Reunião"] = nova_descricao
    agenda = agenda.sort_values(by="Data").reset_index(drop=True)
    entry_descricao.delete(0, tk.END)
    global alteracoes_nao_salvas
    alteracoes_nao_salvas = True
    visualizar_reunioes()
    messagebox.showinfo("Sucesso", "Descrição da reunião atualizada.")

# Criando a interface gráfica
root = tk.Tk()
root.title("Agenda de Reuniões")
root.protocol("WM_DELETE_WINDOW", on_closing)

tk.Label(root, text="Data (DD/MM/AAAA):").grid(row=0, column=0)
entry_data = tk.Entry(root)
entry_data.grid(row=0, column=1)

tk.Label(root, text="Descrição:").grid(row=1, column=0)
entry_descricao = tk.Entry(root)
entry_descricao.grid(row=1, column=1)

btn_adicionar = tk.Button(root, text="Adicionar Reunião", command=adicionar_reuniao)
btn_adicionar.grid(row=2, column=0, columnspan=2)

btn_realizada = tk.Button(root, text="Marcar como Realizada", command=marcar_realizada)
btn_realizada.grid(row=3, column=0, columnspan=2)

btn_excluir = tk.Button(root, text="Excluir Reunião", command=excluir_reuniao)
btn_excluir.grid(row=4, column=0, columnspan=2)

btn_editar = tk.Button(root, text="Editar Descrição", command=editar_descricao)
btn_editar.grid(row=5, column=0, columnspan=2)

btn_salvar = tk.Button(root, text="Salvar Agenda", command=salvar_agenda)
btn_salvar.grid(row=6, column=0, columnspan=2)

btn_carregar = tk.Button(root, text="Carregar Agenda", command=carregar_agenda)
btn_carregar.grid(row=7, column=0, columnspan=2)

cols = ("Data", "Reunião", "Realizada")
tree = ttk.Treeview(root, columns=cols, show="headings")
for col in cols:
    tree.heading(col, text=col)
tree.grid(row=8, column=0, columnspan=2)

visualizar_reunioes()

root.mainloop()