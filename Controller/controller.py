import threading
import time
import os
import stat
from Model.model import SystemInfo, list_all_processes, ProcessInfo
from View.view import DashboardView, ProcessDetailView


class DashboardController:
    def __init__(self):
        self.system_info = SystemInfo()  # Inicializa a classe para obter informações do sistema.
        self.view = DashboardView(self)  # Cria a interface do dashboard associada ao controlador.
        self.running = False  # Indica se o loop de atualização está ativo.

        self.navigate_to_directory(os.getcwd())

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
    
    def navigate_to_directory(self, directory):
        """Atualiza a visualização com o conteúdo do diretório especificado."""
        def update_view():
            print(f"Navegando para: {directory}")
            if os.path.isdir(directory):
                try:
                    print(f"Listando arquivos em {directory}...")
                    items = os.listdir(directory)
                    print(f"Arquivos encontrados: {items}")
                    file_info = self.system_info.list_directory(directory)
                    print("Atualizando a visualização...")
                    self.view.update_filesystem_view(directory, file_info)
                    print("Visualização atualizada com sucesso.")
                except PermissionError:
                    self.view.show_error_message("Permissão negada ao acessar este diretório.")
                except Exception as e:
                    print(f"Erro ao navegar para {directory}: {e}")
            else:
                print(f"Caminho inválido: {directory}")
                self.view.show_error_message("Caminho inválido ou não é um diretório.")
        
        # Executa a atualização em uma thread separada
        threading.Thread(target=update_view).start()


    def open_path(self, path):
        """Navega para o caminho especificado."""
        if os.path.isdir(path):
            self.navigate_to_directory(path)
        else:
            self.view.show_error_message("Caminho inválido ou não é um diretório.")


    def open_file_or_directory(self,item_name):
        """Abre um arquivo ou navega para o diretório clicado."""
        current_path = self.view.path_entry.get()
        full_path = os.path.join(current_path, item_name)
        if os.path.isdir(full_path):
            self.navigate_to_directory(full_path)
        else:
            # Aqui você pode implementar ações adicionais, como abrir arquivos com um programa específico.
            self.view.show_error_message(f"Abrir arquivos ainda não está implementado para: {full_path}")

    def go_up_directory(self, current_path):
        """Navega para o diretório pai."""
        
        parent_directory = os.path.dirname(current_path)
        print(f"Diretório atual: {current_path}, Diretório pai: {parent_directory}")
        self.navigate_to_directory(parent_directory)

    def start_periodic_update(self, interval=3000):
        """Inicia a atualização periódica da view a cada 'interval' milissegundos."""
        current_path = self.view.path_entry.get()
        
        if os.path.isdir(current_path):
            def update_view():
                print(f"Atualizando a view para o caminho: {current_path}")
                file_info = self.system_info.list_directory(current_path)
                self.view.update_filesystem_view(current_path, file_info)
                # Reagendar a atualização
                self.view.filesystem_tab.after(interval, update_view)
            
            # Primeira execução
            self.view.filesystem_tab.after(interval, update_view)
        else:
            print(f"Caminho inválido para atualização periódica: {current_path}")