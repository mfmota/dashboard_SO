import tkinter as tk  #  interface gráfica.
from tkinter import ttk  # widgets estilizados.
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  #  integrar gráficos matplotlib ao tkinter.
import matplotlib.pyplot as plt  # criação de gráficos.

class DashboardView:
    def __init__(self, controller):
        self.controller = controller  
        self.root = tk.Tk()  
        self.root.title("Painel do Sistema")  
        self.root.geometry("1200x800")  

        self.system_frame = tk.Frame(self.root)
        self.system_frame.pack(pady=10)

        # Cria os rótulos de resumo do sistema.
        self.create_summary_labels()

        # Frame gráfico e tabela.
        self.row2_frame = tk.Frame(self.root)
        self.row2_frame.pack(fill=tk.BOTH, expand=True)

        # Cria o gráfico de CPU.
        self.create_cpu_graph()

        # Cria a tabela de processos.
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

        self.details_frame = tk.Frame(self.window)
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if details:
            for key, value in details.items():
                if key != "Threads" and key != "Memory Details":
                    # Tratamento para o campo Estado.
                    if key == "Estado":
                        state_description = {
                            "R": "Ativo",
                            "S": "Inativo",
                            "D": "Aguardando E/S",
                            "Z": "Zombie",
                            "T": "Parado",
                            "X": "Terminou",
                        }.get(value, "Desconhecido")

                        label = tk.Label(self.details_frame, text=f"{key}: {state_description}", font=("Arial", 12), anchor="w")
                        label.pack(fill=tk.X, padx=5, pady=2)
                    else:
                        label = tk.Label(self.details_frame, text=f"{key}: {value}", font=("Arial", 12), anchor="w")
                        label.pack(fill=tk.X, padx=5, pady=2)

            # Exibe detalhes de memória, caso estejam disponíveis.
            if "Memory Details" in details:
                mem_details_label = tk.Label(self.details_frame, text="Detalhes de Memória:", font=("Arial", 14, "bold"))
                mem_details_label.pack(anchor="w", padx=5, pady=5)

                if details["Memory Details"] is not None:
                    for mem_key, mem_value in details["Memory Details"].items():
                        label = tk.Label(self.details_frame, text=f"{mem_key}: {mem_value} KB", font=("Arial", 12), anchor="w")
                        label.pack(fill=tk.X, padx=5, pady=2)

            # Exibe a seção de threads do processo.
            threads_label = tk.Label(self.details_frame, text="Threads:", font=("Arial", 14, "bold"))
            threads_label.pack(anchor="w", padx=5, pady=5)

            table_frame = tk.Frame(self.details_frame)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Configura a tabela de threads.
            self.threads_table = ttk.Treeview(
                table_frame,
                columns=("TID", "Estado", "Tempo de CPU"),
                show="headings",
                yscrollcommand=scrollbar.set
            )
            self.threads_table.heading("TID", text="TID")
            self.threads_table.column("TID", anchor=tk.CENTER, width=50)
            self.threads_table.heading("Estado", text="Estado")
            self.threads_table.column("Estado", anchor=tk.W, width=100)
            self.threads_table.heading("Tempo de CPU", text="Tempo de CPU (s)")
            self.threads_table.column("Tempo de CPU", anchor=tk.E, width=100)
            self.threads_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            scrollbar.config(command=self.threads_table.yview)

            # Preenche a tabela de threads com os dados fornecidos.
            if "Threads" in details and isinstance(details["Threads"], list):
                for thread in details["Threads"]:
                    # Tratamento para Estado.
                    state_description = {
                        "R": "Ativo",
                        "S": "Inativo",
                        "D": "Aguardando E/S",
                        "Z": "Zombie",
                        "T": "Parado",
                        "X": "Terminou",
                    }.get(thread["state"], "Desconhecido")

                    # Adiciona a thread à tabela.
                    self.threads_table.insert("", "end", values=(thread["tid"], state_description, thread["cpu_time"]))
            else:
                self.threads_table.insert("", "end", values=("N/A", "N/A", "N/A"))
        else:
            label = tk.Label(self.details_frame, text="Nenhum detalhe disponível para este processo.", font=("Arial", 12), anchor="center")
            label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show(self):
        self.window.mainloop()
