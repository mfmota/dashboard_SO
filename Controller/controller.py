import threading
import time
from Model.model import SystemInfo, list_all_processes, ProcessInfo
from View.view import DashboardView, ProcessDetailView


class DashboardController:
    def __init__(self):
        self.system_info = SystemInfo()  # Inicializa a classe para obter informações do sistema.
        self.view = DashboardView(self)  # Cria a interface do dashboard associada ao controlador.
        self.running = False  # Indica se o loop de atualização está ativo.


    def start(self):
        self.running = True  
        while self.running:
            self.update_thread = threading.Thread(target=self.update_data, daemon=True)  # Thread para atualização periodica dos dados
            self.update_thread.start()  
            self.view.run()  


    def stop(self):
        self.running = False  
        self.view.stop()  


    def update_data(self):
        while self.running:  
            # Obtém as informações de uso da CPU e porcentagem de tempo ocioso.
            cpu_usage, idle_percentage = self.system_info.get_cpu_usage()
           
            # Obtém informações sobre a memória do sistema.
            memory_info = self.system_info.get_memory_info()


            # Obtém o número total de processos e threads no sistema.
            total_processes, total_threads = self.system_info.get_total_processes_and_threads()


            # Atualiza a interface com as informações do sistema.
            self.view.update_system_info(
            cpu_usage=cpu_usage,
            idle_percentage=idle_percentage,
            memory_info=memory_info,
            total_processes=total_processes,
            total_threads=total_threads
        )


            # Lista todos os processos ativos e atualiza a interface com a lista de processos.
            processes = list_all_processes()
            self.view.update_process_list(processes)


            time.sleep(5)  # Aguarda 5 segundos antes de atualizar novamente.


    def show_process_details(self, pid):
        # Cria uma instância da classe para obter detalhes do processo específico.
        process_info = ProcessInfo(pid)
        process_info.get_process_details()


        # Obtém as informações das threads associadas ao processo.
        threads_info = process_info.get_thread_info()


        # Obtém detalhes de memória do processo.
        memory_info = process_info.get_memory_details(pid)
       
        details = {
            "PID": pid,
            "Nome": process_info.name,
            "Usuário": process_info.user,
            "Estado": process_info.state,
            "Memória": f"{process_info.memory} KB",
            "Memory Details": memory_info,
            "Tempo de Atividade (s)": process_info.get_uptime(),
            "Threads": threads_info,
        }
       
        ProcessDetailView(self.view.root, details)

    def filter_process_list(self, query):
        all_processes = list_all_processes()
        filtered_processes = [
            process for process in all_processes
            if any(query.lower() in str(value).lower() for value in process.values())
        ]
        self.view.update_process_list(filtered_processes)

    def sort_process_list(self, column, ascending=True):
        """Ordena os processos ativos com base em uma coluna e ordem especificada."""
        processes = list_all_processes()

        # Mapeia as colunas para os índices correspondentes.
        column_index_map = {
            "PID": "pid",
            "Nome": "name",
            "Usuário": "user",
            "Memória": "memory",
            "Threads": "threads",
        }

        # Ordena os processos pela coluna selecionada.
        sorted_processes = sorted(
            processes,
            key=lambda p: p[column_index_map[column]],
            reverse=not ascending
        )

        # Atualiza a tabela com os processos ordenados.
        self.view.update_process_list(sorted_processes)