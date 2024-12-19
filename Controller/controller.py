import threading
import time
from Model.model import SystemInfo, list_all_processes, ProcessInfo
from View.view import DashboardView, ProcessDetailView

class DashboardController:
    def __init__(self):
        self.system_info = SystemInfo()
        self.view = DashboardView(self)
        self.running = False

    def start(self):
        self.running = True
        self.update_thread = threading.Thread(target=self.update_data, daemon=True)
        self.update_thread.start()
        self.view.run()

    def stop(self):
        self.running = False
        self.view.stop()

    def update_data(self):
        while self.running:
       
            cpu_usage, idle_percentage = self.system_info.get_cpu_usage()
            
            memory_info = self.system_info.get_memory_info()

            total_processes, total_threads = self.system_info.get_total_processes_and_threads()

            self.view.update_system_info(
            cpu_usage=cpu_usage,
            idle_percentage=idle_percentage,
            memory_info=memory_info,
            total_processes=total_processes,
            total_threads=total_threads
        )

            processes = list_all_processes()

            self.view.update_process_list(processes)

            time.sleep(5)

    def show_process_details(self, pid):
        process_info = ProcessInfo(pid)
        process_info.get_process_details()

        threads_info = process_info.get_thread_info()
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
