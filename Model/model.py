import os #interação com o sistemas de arquivo
import pwd # mapear UIDs com nomes de usuários

class SystemInfo:
    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.prev_total_time = 0
        self.prev_idle_time = 0
    # uso da CPU
    def get_cpu_usage(self):
        try:
            # lê as informações de cpu do arquivo /proc/stat
            with open("/proc/stat", "r") as f:
                lines = f.readlines()
            cpu_line = lines[0].split()
            total_time = sum(int(x) for x in cpu_line[1:])
            idle_time = int(cpu_line[4])
            total_diff = 0
            # Calcula a diferença desde a última leitura
            if self.prev_total_time:
                total_diff = total_time - self.prev_total_time
                idle_diff = idle_time - self.prev_idle_time
                self.cpu_usage = 100 * (1 - idle_diff / total_diff)

            self.prev_total_time = total_time
            self.prev_idle_time = idle_time
             # Calcula a porcentagem ociosa como referência
            idle_percentage = (idle_diff / total_diff) * 100 if total_diff > 0 else 0

            return round(self.cpu_usage, 2), round(idle_percentage, 2)
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            return 0.0

    #informações detalhadas da memória
    def get_memory_info(self):
        try:
             # Lê informações de memória do arquivo /proc/meminfo
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            mem_total = int(lines[0].split()[1])
            mem_free = int(lines[1].split()[1])
            mem_available = int(lines[2].split()[1])
            mem_virtual = int(lines[14].split()[1])  
            mem_virtual_free = int(lines[15].split()[1]) 

            self.memory_usage = 100 * (1 - mem_free / mem_total)
           
            return {
                "total_memory": mem_total,
                "free_memory": mem_free,
                "available_memory": mem_available,
                "virtual_memory": mem_virtual,
                "virtual_memory_free": mem_virtual_free,
                "memory_usage_percent": round(self.memory_usage, 2),
                "memory_free_percent": round((mem_free / mem_total) * 100, 2)
            }
        except Exception as e:
            print(f"Error getting memory info: {e}")
            return {
                "total_memory": 0,
                "free_memory": 0,
                "available_memory": 0,
                "virtual_memory": 0,
                "virtual_memory_free": 0,
                "memory_usage_percent": 0,
                "memory_free_percent": 0
            }

    # Obtém o número total de processos e threads no sistema
    def get_total_processes_and_threads(self):
        try:
            process_count = 0
            thread_count = 0

            # Percorre todos os PIDs no diretório /proc
            for pid in os.listdir("/proc"):
                if pid.isdigit():  # Verifica se o nome do diretório é um PID válido
                    process_count += 1
                    with open(f"/proc/{pid}/status", "r") as f:
                        lines = f.readlines()
                    for line in lines:
                        if line.startswith("Threads:"): # Encontra a contagem de threads para o processo
                            thread_count += int(line.split()[1])
                            break

            return process_count, thread_count
        except Exception as e:
            print(f"Error counting processes and threads: {e}")
            return 0, 0
#informações específicas sobre um projeto 
class ProcessInfo:
    def __init__(self, pid):
        self.pid = pid
        self.name = None
        self.user = None
        self.state = None
        self.memory = 0
        self.memory_details = {}
        self.threads = []
        self.command = None

    # Obtém o nome do usuário que executa o processo
    def get_process_user(self):
        try:
            with open(f"/proc/{self.pid}/loginuid", "r") as f:
                uid = int(f.read().strip())
            return pwd.getpwuid(uid).pw_name
        except Exception:
            return "Unknown"

    # detalhes sobre o processo
    def get_process_details(self):
        try:
            with open(f"/proc/{self.pid}/status", "r") as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith("Name:"):
                    self.name = line.split()[1]
                elif line.startswith("Threads:"):
                    self.threads = int(line.split()[1])
                elif line.startswith("VmRSS:"):
                    self.memory = int(line.split()[1])
                elif line.startswith("State:"):
                    self.state = line.split()[1]

            self.user = self.get_process_user()

            with open(f"/proc/{self.pid}/cmdline", "r") as f:
                self.command = f.read().replace('\x00', ' ').strip()

        except FileNotFoundError:
            pass
    
     # detalhes específicos de memória do processo
    def get_memory_details(self,pid):
        
        try:
            memory_details = {
            "Memória Total (KB)": 0,
            "Páginas de Código (KB)": 0,
            "Memória Heap (KB)": 0,
            "Memóra de Pilha (KB)": 0
            }
            with open(f"/proc/{self.pid}/smaps", "r") as f:
                for line in f:
                    if line.startswith("Size:"):
                        memory_details["Memória Total (KB)"] += int(line.split()[1])
                    elif line.startswith("VmCode:"):
                        memory_details["Páginas de Código (KB)"] += int(line.split()[1])
                    elif line.startswith("VmData:"):  
                        memory_details["Memória Heap (KB)"] += int(line.split()[1])
                    elif line.startswith("VmStack:"):
                        memory_details["Memória de Pilha (KB)"] += int(line.split()[1])
            return memory_details
            
        except Exception as e:
            print(f"Error getting memory details for PID {self.pid}: {e}")
        
    #informações sobre as threads do processo
    def get_thread_info(self):
        thread_info = []
        try:
            thread_dir = f"/proc/{self.pid}/task/"
            if os.path.exists(thread_dir):
                for tid in os.listdir(thread_dir):
                    with open(f"{thread_dir}{tid}/stat", "r") as f:
                        stats = f.read().split()
                        state = stats[2]
                        cpu_time = self.get_cpu_time(tid)
                    thread_info.append({
                        "tid": tid,
                        "state": state,
                        "cpu_time": cpu_time
                    })
        except Exception as e:
            print(f"Error getting thread info for PID {self.pid}: {e}")
        return thread_info

    # calcular o tempo de CPU de uma thread
    @staticmethod
    def get_cpu_time(tid):
        try:
            with open(f"/proc/{tid}/stat", "r") as f:
                stats = f.read().split()
                utime = int(stats[13])  # Tempo de CPU em modo usuário
                stime = int(stats[14])  # Tempo de CPU em modo kernel
                return utime + stime
        except Exception:
            return 0

    # Calcula o tempo de execução do processo desde o início
    def get_uptime(self):
        try:
            with open("/proc/uptime", "r") as f:
                system_uptime = float(f.readline().split()[0])

            with open(f"/proc/{self.pid}/stat", "r") as f:
                stats = f.read().split()
                start_time = int(stats[21]) / os.sysconf(os.sysconf_names['SC_CLK_TCK'])

            return round(system_uptime - start_time, 2)
        except Exception:
            return 0.0

    def to_dict(self):
        return {
            "pid": self.pid,
            "name": self.name,
            "user": self.user,
            "state": self.state,
            "memory": f"{self.memory} KB",
             "memory_details": self.memory_details,
            "threads": self.threads,
            "command": self.command,
            "uptime": self.get_uptime()
        }

# Lista todos os processos disponíveis no sistema
def list_all_processes():
    processes = []
    for pid in os.listdir("/proc"):
        if pid.isdigit(): # Filtra apenas diretórios que são números (PIDs)
            process = ProcessInfo(pid)
            process.get_process_details()
            thread_info = process.get_thread_info()
            if process.name:
                processes.append({
                    **process.to_dict(),
                    "threads_info": thread_info
                })
    return processes
