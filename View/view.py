import tkinter as tk  #  interface gráfica.
from tkinter import ttk  # widgets estilizados.
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  #  integrar gráficos matplotlib ao tkinter.
import matplotlib.pyplot as plt  # criação de gráficos.
import os

class DashboardView:
    def __init__(self, controller):
        self.controller = controller  
        self.root = tk.Tk()  
        self.root.title("Painel do Sistema")  
        self.root.geometry("1200x800")  

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.system_tab = tk.Frame(self.notebook)
        self.notebook.add(self.system_tab, text="Resumo do Sistema")

        self.navegation_tab = tk.Frame(self.notebook)
        self.notebook.add(self.navegation_tab, text="Navegação de Diretórios")

        self.filesystem_tab = tk.Frame(self.notebook)
        self.notebook.add(self.filesystem_tab, text="Sistema de arquivos")

        # Cria os rótulos de resumo do sistema.
        self.create_system_summary()

        # Criar a aba do sistema de arquivos
        self.create_navegation_tab()

        self.create_filesystem_tab()

    def create_system_summary(self):
        # Frame de informações do sistema
        self.system_frame = tk.Frame(self.system_tab)
        self.system_frame.pack(pady=10)

        # Cria os rótulos de resumo do sistema
        self.create_summary_labels()

        # Frame para gráfico e tabela
        self.row2_frame = tk.Frame(self.system_tab)
        self.row2_frame.pack(fill=tk.BOTH, expand=True)

        # Cria o gráfico de CPU
        self.create_cpu_graph()

        # Cria a tabela de processos
        self.create_process_table()

    # criar rótulos de resumo do sistema.
    def create_summary_labels(self):
        self.labels_frame = tk.Frame(self.system_frame)
        self.labels_frame.pack()

        label_texts = [
            ("Uso de CPU", "--%"),
            ("Uso de Memória", "--%"),
            ("Memória Livre", "--%"),
            ("Memória Física", "--%"),
            ("Memória Virtual", "--%"),
            ("Memória Virtual Livre", "--%"),
            ("Tempo Ocioso", "--%"),
            ("Total de Processos", "--%"),
            ("Total de Threads", "--%"),
        ]

        self.summary_labels = []  

        # Criação dinâmica de rótulos com base nos textos definidos.
        for index, (text, value) in enumerate(label_texts):
            row = index // 4  # Calcula a linha atual.
            col = index % 4  # Calcula a coluna atual.

            # Cria um frame para cada rótulo.
            frame = tk.Frame(self.labels_frame, borderwidth=2, relief="groove", bg="#f4f4f4")
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Rótulo do texto descritivo.
            tk.Label(frame, text=text, font=("Arial", 12), fg="gray", bg="#f4f4f4").pack()

            # Rótulo para o valor do dado.
            label = tk.Label(frame, text=value, font=("Arial", 18, "bold"), fg="black", bg="#f4f4f4")
            label.pack()

            # Armazena o rótulo para atualizações futuras.
            self.summary_labels.append(label)

        # Desestruturação para acesso rápido aos rótulos.
        (self.cpu_label, self.memory_label, self.memory_free_label, self.memory_physical_label,
         self.memory_virtual_label, self.memory_virtual_free_label, self.idle_time_label,
         self.total_processes_label, self.total_threads_label) = self.summary_labels

    # criar o gráfico de uso de CPU.
    def create_cpu_graph(self):
        
        self.cpu_frame = tk.Frame(self.row2_frame, borderwidth=2, relief="groove")
        self.cpu_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configuração inicial do gráfico de CPU.
        self.fig, self.ax = plt.subplots()
        self.cpu_pie = self.ax.pie([50, 50], labels=["Uso", "Livre"], autopct="%1.1f%%", startangle=90, colors=["#ff9999", "#66b3ff"])
        self.ax.axis("equal")  

        self.canvas = FigureCanvasTkAgg(self.fig, self.cpu_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        tk.Label(self.cpu_frame, text="Gráfico de Uso de CPU", font=("Arial", 14, "bold")).pack()

    #  criar a tabela de processos.
    def create_process_table(self):
        
        self.process_frame = tk.Frame(self.row2_frame, borderwidth=2, relief="groove")
        self.process_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.process_frame, text="Tabela de Processos", font=("Arial", 14, "bold")).pack()
        
        # Campo de busca
        search_frame = tk.Frame(self.process_frame)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Buscar:", font=("Arial", 12)).pack(side=tk.LEFT)
        search_entry = tk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, padx=5)

        def filter_table():
            query = search_entry.get().lower()
            for row in self.process_table.get_children():
                values = self.process_table.item(row)["values"]
                if any(query in str(value).lower() for value in values):
                    self.process_table.reattach(row, "", tk.END)
                else:
                    self.process_table.detach(row)

        search_entry.bind("<KeyRelease>", lambda event: filter_table())

        # Configuração da tabela usando Treeview.
        self.process_table = ttk.Treeview(self.process_frame, columns=("PID", "Nome", "Usuário", "Memória", "Threads"), show="headings")
        self.process_table.heading("PID", text="PID")
        self.process_table.column("PID", anchor=tk.CENTER, width=50)
        self.process_table.heading("Nome", text="Nome")
        self.process_table.column("Nome", anchor=tk.W, width=150)
        self.process_table.heading("Usuário", text="Usuário")
        self.process_table.column("Usuário", anchor=tk.W, width=100)
        self.process_table.heading("Memória", text="Memória")
        self.process_table.column("Memória", anchor=tk.E, width=80)
        self.process_table.heading("Threads", text="Threads")
        self.process_table.column("Threads", anchor=tk.CENTER, width=80)
        self.process_table.pack(fill=tk.BOTH, expand=True)

        # Evento de clique duplo na tabela.
        self.process_table.bind("<Double-1>", self.on_process_double_click)

    #ordena a tabela
    def sort_table(self, column):
        data = [(self.process_table.item(child)["values"], child) for child in self.process_table.get_children()]
        index = ["PID", "Nome", "Usuário", "Memória", "Threads"].index(column)
        data.sort(key=lambda x: x[0][index])
        for index, (_, item) in enumerate(data):
            self.process_table.move(item, "", index)

    # Atualiza os rótulos de informações do sistema.
    def update_system_info(self, cpu_usage, idle_percentage, memory_info, total_processes, total_threads):
        # Atualiza os valores de cada rótulo.
        self.cpu_label.config(text=f"{cpu_usage}%")
        self.memory_label.config(text=f"{memory_info['memory_usage_percent']}%")
        self.memory_free_label.config(text=f"{round((memory_info['free_memory'] / memory_info['total_memory']) * 100, 2)}%")
        self.memory_physical_label.config(text=f"{memory_info['total_memory'] // 1024} MB")
        self.memory_virtual_label.config(text=f"{memory_info['virtual_memory'] // 1024} MB")
        self.memory_virtual_free_label.config(text=f"{memory_info['virtual_memory_free'] // 1024} MB")
        self.idle_time_label.config(text=f"{idle_percentage}%")
        self.total_processes_label.config(text=f"{total_processes}")
        self.total_threads_label.config(text=f"{total_threads}")

        # Atualiza o gráfico de CPU.
        self.ax.clear()
        self.cpu_pie = self.ax.pie(
            [cpu_usage, 100 - cpu_usage],
            labels=["Uso", "Livre"],
            autopct="%1.1f%%",
            startangle=90,
            colors=["#ff9999", "#66b3ff"]
        )
        self.ax.axis("equal")
        self.canvas.draw()

    # Atualiza a tabela de processos.
    def update_process_list(self, processes):
        # Remove linhas antigas.
        for row in self.process_table.get_children():
            self.process_table.delete(row)
        # Adiciona novas linhas com dados atualizados.
        for process in processes:
            self.process_table.insert("", "end", values=(process["pid"], process["name"], process["user"], process["memory"], process["threads"]))

    # Evento para lidar com o clique duplo em um processo na tabela.
    def on_process_double_click(self, event):
        selected_item = self.process_table.selection()
        if selected_item:
            pid = self.process_table.item(selected_item[0], "values")[0]
            self.controller.show_process_details(pid)


    def create_navegation_tab(self):
        # Barra de navegação
        navigation_frame = tk.Frame(self.navegation_tab)
        navigation_frame.pack(fill=tk.X)

        self.path_label = tk.Label(navigation_frame, text="Pasta Atual:", font=("Arial", 12))
        self.path_label.pack(side=tk.LEFT, padx=5)

        self.path_entry = tk.Entry(navigation_frame, font=("Arial", 12))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Button(navigation_frame, text="Voltar", command=lambda: self.controller.go_up_directory(self.path_entry.get())).pack(side=tk.LEFT, padx=5)
        tk.Button(navigation_frame, text="Ir", command=lambda: self.controller.open_path(self.path_entry.get())).pack(side=tk.LEFT, padx=5)

        # Lista de arquivos e diretórios
        self.files_table = ttk.Treeview(self.navegation_tab, columns=("Nome", "Tamanho", "Tipo","Permissões", "Modificação"),
        show="headings")
        self.files_table.heading("Nome", text="Nome")
        self.files_table.column("Nome", anchor=tk.W, width=300)
        self.files_table.heading("Tamanho", text="Tamanho")
        self.files_table.column("Tamanho", anchor=tk.E, width=100)
        self.files_table.heading("Tipo", text="Tipo")
        self.files_table.column("Tipo", anchor=tk.CENTER, width=100)
        self.files_table.heading("Permissões", text="Permissões")  
        self.files_table.column("Permissões", anchor=tk.CENTER, width=150)  
        self.files_table.heading("Modificação", text="Modificação")
        self.files_table.column("Modificação", anchor=tk.W, width=200)
        self.files_table.pack(fill=tk.BOTH, expand=True)

        self.files_table.bind("<Double-1>", self.on_file_double_click)

    def update_navegation_view(self, path, files):
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)

        for row in self.files_table.get_children():
            self.files_table.delete(row)

        for file in files:
            tree_id= self.files_table.insert("", "end", values=(
                file["name"],
                file["size"],
                file["type"],
                file["permissions"],
                file["last_modified"],
            ))
            file["tree_id"] = tree_id

    def update_tree_item(self, tree_id, column, value):
        """Atualiza um valor específico de um item no Treeview."""
        current_values = list(self.files_table.item(tree_id, "values"))
        
        # Mapeia colunas para índices (ajuste se necessário)
        column_map = {
            "name": 0,
            "size": 1,
            "type": 2,
            "permissions": 3,
            "last_modified": 4,
            "fstype": 5,
            "total_size": 6,
            "used_size": 7,
            "free_size": 8,
            "percent_used": 9,
        }

        # Atualiza o valor no índice correspondente
        column_index = column_map.get(column)
        if column_index is not None:
            current_values[column_index] = value
            self.files_table.item(tree_id, values=current_values)

    def on_file_double_click(self, event):
        selected_item = self.files_table.selection()
        if not selected_item:
            return
        file_name = self.files_table.item(selected_item[0], "values")[0]
        self.controller.open_file_or_directory(file_name)

    def create_filesystem_tab(self):
        """Cria a aba do sistema de arquivos na interface gráfica."""
        self.filesystem_frame = ttk.Frame(self.filesystem_tab)
        self.filesystem_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Criando a tabela para exibir informações do sistema de arquivos
        columns = ("Device", "Mountpoint", "FSType", "Total (MB)", "Used (MB)", "Free (MB)", "Usage (%)")

        self.filesystem_tree = ttk.Treeview(self.filesystem_frame, columns=columns, show="headings", height=10)
        
        # Configuração das colunas
        for col in columns:
            self.filesystem_tree.heading(col, text=col)
            self.filesystem_tree.column(col, anchor="center", width=100)

        self.filesystem_tree.pack(fill="both", expand=True)

    def update_filesystem_info(self, filesystem_info):
        """Atualiza a tabela com as informações do sistema de arquivos."""
        # Limpando dados antigos
        for row in self.filesystem_tree.get_children():
            self.filesystem_tree.delete(row)

        # Inserindo novas informações
        for partition in filesystem_info:
            self.filesystem_tree.insert("", "end", values=(
                partition["device"],
                partition["mountpoint"],
                partition["fstype"],
                partition["total_size"],
                partition["used_size"],
                partition["free_size"],
                partition["percent_used"]
            ))
    def run(self):
        self.root.mainloop()

    def stop(self):
        self.root.quit()

# Classe responsável por exibir detalhes de um processo específico.
class ProcessDetailView:
    def __init__(self, parent, details):
        self.details = details  
        self.window = tk.Toplevel(parent)  
        self.window.title(f"Detalhes do Processo - PID {details['PID']}")  
        self.window.geometry("800x500")  

        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Aba de Detalhes Básicos
        basic_tab = tk.Frame(notebook)
        notebook.add(basic_tab, text="Detalhes Básicos")

        if details:
            for key, value in details.items():
                if key not in ("Threads", "Memory Details", "Arquivos Abertos","Estatísticas de E/S"):
                    label = tk.Label(basic_tab, text=f"{key}: {value}", font=("Arial", 12), anchor="w")
                    label.pack(fill=tk.X, padx=5, pady=2)

            # Exibe detalhes de memória, caso estejam disponíveis.
            if "Memory Details" in details:
                memory_tab = tk.Frame(notebook)
                notebook.add(memory_tab, text="Detalhes de Memória")

                if details["Memory Details"] is not None:
                    for mem_key, mem_value in details["Memory Details"].items():
                        label = tk.Label(memory_tab, text=f"{mem_key}: {mem_value} KB", font=("Arial", 12), anchor="w")
                        label.pack(fill=tk.X, padx=5, pady=2)

                else:
                    label = tk.Label(memory_tab, text="Sem informações de memória disponíveis", font=("Arial", 12), anchor="w")
                    label.pack(fill=tk.X, padx=5, pady=2)

            #Aba Threads
            threads_tab = tk.Frame(notebook)
            notebook.add(threads_tab, text="Threads")

            threads_table = ttk.Treeview(threads_tab, columns=("TID", "Estado", "Tempo de CPU"), show="headings")
            threads_table.heading("TID", text="TID")
            threads_table.heading("Estado", text="Estado")
            threads_table.heading("Tempo de CPU", text="Tempo de CPU")
            threads_table.pack(fill=tk.BOTH, expand=True)

            for thread in details.get("Threads", []):
                state_description = {
                    "R": "Ativo",
                    "S": "Inativo",
                    "D": "Aguardando E/S",
                    "Z": "Zombie",
                    "T": "Parado",
                    "X": "Terminou",
                }.get(thread["state"], "Desconhecido")
                threads_table.insert("", "end", values=(thread["tid"], state_description, thread["cpu_time"]))

        # Aba de Arquivos Abertos
            open_files_tab = tk.Frame(notebook)
            notebook.add(open_files_tab, text="Arquivos Abertos")

            open_files_listbox = tk.Listbox(open_files_tab, font=("Arial", 12))
            open_files_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            open_files = details.get("Arquivos Abertos", [])
            if open_files:
                for file in open_files:
                    open_files_listbox.insert(tk.END, file)
            else:
                open_files_listbox.insert(tk.END, "Nenhum arquivo aberto.")

            # 🔹 Aba de Estatísticas de E/S
            io_stats_tab = tk.Frame(notebook)
            notebook.add(io_stats_tab, text="Estatísticas de E/S")

            if "Estatísticas de E/S" in details:
                for key, value in details["Estatísticas de E/S"].items():
                    label = tk.Label(io_stats_tab, text=f"{key}: {value}", font=("Arial", 12), anchor="w")
                    label.pack(fill=tk.X, padx=5, pady=2)
            else:
                label = tk.Label(io_stats_tab, text="Sem informações de E/S disponíveis.", font=("Arial", 12), anchor="w")
                label.pack(fill=tk.X, padx=5, pady=2)

    def show(self):
        self.window.mainloop()
