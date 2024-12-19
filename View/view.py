import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class DashboardView:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Painel do Sistema")
        self.root.geometry("1200x800")
        
        self.system_frame = tk.Frame(self.root)
        self.system_frame.pack(pady=10)

        self.create_summary_labels()

        self.row2_frame = tk.Frame(self.root)
        self.row2_frame.pack(fill=tk.BOTH, expand=True)

        self.create_cpu_graph()

        self.create_process_table()

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

        for index, (text, value) in enumerate(label_texts):
            row = index // 4  
            col = index % 4  

            frame = tk.Frame(self.labels_frame, borderwidth=2, relief="groove", bg="#f4f4f4")
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew") 

            tk.Label(frame, text=text, font=("Arial", 12), fg="gray", bg="#f4f4f4").pack()
          
            label = tk.Label(frame, text=value, font=("Arial", 18, "bold"), fg="black", bg="#f4f4f4")
            label.pack()
            
            self.summary_labels.append(label)

        (self.cpu_label, self.memory_label, self.memory_free_label, self.memory_physical_label,
        self.memory_virtual_label, self.memory_virtual_free_label, self.idle_time_label,
        self.total_processes_label, self.total_threads_label) = self.summary_labels


    def create_cpu_graph(self):
        self.cpu_frame = tk.Frame(self.row2_frame, borderwidth=2, relief="groove")
        self.cpu_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots()
        self.cpu_pie = self.ax.pie([50, 50], labels=["Uso", "Livre"], autopct="%1.1f%%", startangle=90, colors=["#ff9999", "#66b3ff"])
        self.ax.axis("equal") 

        self.canvas = FigureCanvasTkAgg(self.fig, self.cpu_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        tk.Label(self.cpu_frame, text="Gráfico de Uso de CPU", font=("Arial", 14, "bold")).pack()

    def create_process_table(self):
        self.process_frame = tk.Frame(self.row2_frame, borderwidth=2, relief="groove")
        self.process_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.process_frame, text="Tabela de Processos", font=("Arial", 14, "bold")).pack()

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

        self.process_table.bind("<Double-1>", self.on_process_double_click)

    def update_system_info(self, cpu_usage, idle_percentage, memory_info, total_processes, total_threads):

        self.summary_labels[0].config(text=f"{cpu_usage}%") 
        self.summary_labels[1].config(text=f"{memory_info['memory_usage_percent']}%")  
        self.summary_labels[2].config(text=f"{round((memory_info['free_memory'] / memory_info['total_memory']) * 100, 2)}%")  
        self.summary_labels[3].config(text=f"{memory_info['total_memory'] // 1024} MB")  
        self.summary_labels[4].config(text=f"{memory_info['virtual_memory'] // 1024} MB")  
        self.summary_labels[5].config(text=f"{memory_info['virtual_memory_free'] // 1024} MB") 
        self.summary_labels[6].config(text=f"{idle_percentage}%") 
        self.summary_labels[7].config(text=f"{total_processes}")  
        self.summary_labels[8].config(text=f"{total_threads}")  

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


    def update_process_list(self, processes):
        for row in self.process_table.get_children():
            self.process_table.delete(row)
        for process in processes:
            self.process_table.insert("", "end", values=(process["pid"], process["name"], process["user"], process["memory"], process["threads"]))
    
    def on_process_double_click(self, event):
        selected_item = self.process_table.selection()
        if selected_item:
            pid = self.process_table.item(selected_item[0], "values")[0]
            self.controller.show_process_details(pid)

    def run(self):
        self.root.mainloop()

    def stop(self):
        self.root.quit()

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
                    if key == "Estado":
                        if value ==  "R":
                            label = tk.Label(self.details_frame, text=f"{key}: Ativo", font=("Arial", 12), anchor="w")
                            label.pack(fill=tk.X, padx=5, pady=2)
                        elif value == "S":
                            label = tk.Label(self.details_frame, text=f"{key}: Inativo", font=("Arial", 12), anchor="w")
                            label.pack(fill=tk.X, padx=5, pady=2)
                        elif value == "D":
                            label = tk.Label(self.details_frame, text=f"{key}: Aguardando E/S", font=("Arial", 12), anchor="w")
                            label.pack(fill=tk.X, padx=5, pady=2)
                        elif value == "Z":
                            label = tk.Label(self.details_frame, text=f"{key}: Zombie", font=("Arial", 12), anchor="w")
                            label.pack(fill=tk.X, padx=5, pady=2)    
                        elif value == "T":
                            label = tk.Label(self.details_frame, text=f"{key}: Parado", font=("Arial", 12), anchor="w")
                            label.pack(fill=tk.X, padx=5, pady=2)
                        elif value == "X":
                            label = tk.Label(self.details_frame, text=f"{key}: Terminou", font=("Arial", 12), anchor="w")
                            label.pack(fill=tk.X, padx=5, pady=2)
                    else:
                        label = tk.Label(self.details_frame, text=f"{key}: {value}", font=("Arial", 12), anchor="w")
                        label.pack(fill=tk.X, padx=5, pady=2)

            if "Memory Details" in details:
                mem_details_label = tk.Label(self.details_frame, text="Detalhes de Memória:", font=("Arial", 14, "bold"))
                mem_details_label.pack(anchor="w", padx=5, pady=5)

                if details["Memory Details"] is not None:
                
                    for mem_key, mem_value in details["Memory Details"].items():
                        label = tk.Label(self.details_frame, text=f"{mem_key}: {mem_value} KB", font=("Arial", 12), anchor="w")
                        label.pack(fill=tk.X, padx=5, pady=2)

            threads_label = tk.Label(self.details_frame, text="Threads:", font=("Arial", 14, "bold"))
            threads_label.pack(anchor="w", padx=5, pady=5)

            table_frame = tk.Frame(self.details_frame)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.threads_table = ttk.Treeview(table_frame, columns=("TID", "Estado", "Tempo de CPU"), show="headings", yscrollcommand=scrollbar.set)
            self.threads_table.heading("TID", text="TID")
            self.threads_table.column("TID", anchor=tk.CENTER, width=50)
            self.threads_table.heading("Estado", text="Estado")
            self.threads_table.column("Estado", anchor=tk.W, width=100)
            self.threads_table.heading("Tempo de CPU", text="Tempo de CPU (s)")
            self.threads_table.column("Tempo de CPU", anchor=tk.E, width=100)
            self.threads_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            scrollbar.config(command=self.threads_table.yview)

            if "Threads" in details and isinstance(details["Threads"], list): 
                for thread in details["Threads"]:
                    thread_state = thread["state"]
                    
                    if thread_state == "R":
                        state_description = "Ativo"
                    elif thread_state == "S":
                        state_description = "Inativo"
                    elif thread_state == "D":
                        state_description = "Aguardando E/S"
                    elif thread_state == "Z":
                        state_description = "Zombie"
                    elif thread_state == "T":
                        state_description = "Parado"
                    elif thread_state == "X":
                        state_description = "Terminou"
                    else:
                        state_description = "Desconhecido"
                    
                    self.threads_table.insert("", "end", values=(thread["tid"], state_description, thread["cpu_time"]))

            else:
                self.threads_table.insert("", "end", values=("N/A", "N/A", "N/A"))
        else:
            label = tk.Label(self.details_frame, text="Nenhum detalhe disponível para este processo.", font=("Arial", 12), anchor="center")
            label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show(self):
        self.window.mainloop()
