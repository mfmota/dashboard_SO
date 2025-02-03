import os #interação com o sistemas de arquivo
import pwd # mapear UIDs com nomes de usuários
import stat 
import subprocess
from datetime import datetime
import threading
import time

class SystemInfo:
    def __init__(self):
        self.stop_directory_size_thread = threading.Event()
        self.processed_directories = set()
        self.dir_lock = threading.Lock()
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
                    try:    
                        process_count += 1
                        with open(f"/proc/{pid}/status", "r") as f:
                            lines = f.readlines()
                        for line in lines:
                            if line.startswith("Threads:"): # Encontra a contagem de threads para o processo
                                thread_count += int(line.split()[1])
                                break
                    except FileNotFoundError:
                        # O processo pode ter sido encerrado antes de lermos
                        continue

            return process_count, thread_count
        except Exception as e:
            print(f"Error counting processes and threads: {e}")
            return 0, 0
        
    def get_filesystem_info(self):
        try:
            partitions = []
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    device = parts[0]
                    mountpoint = parts[1]
                    fstype = parts[2]


                    if True:  
                        # Obtém estatísticas do sistema de arquivos
                        stats = os.statvfs(mountpoint)
                        total_size = (stats.f_blocks * stats.f_frsize) // (1024 * 1024)  # Em MB
                        free_size = (stats.f_bfree * stats.f_frsize) // (1024 * 1024)  # Em MB
                        used_size = total_size - free_size
                        percent_used = round((used_size / total_size) * 100, 2) if total_size > 0 else 0

                        partitions.append({
                            "device": device,
                            "mountpoint": mountpoint,
                            "fstype": fstype,
                            "total_size": total_size,
                            "used_size": used_size,
                            "free_size": free_size,
                            "percent_used": percent_used,
                        })
            return partitions
        except Exception as e:
            print(f"Error getting filesystem info: {e}")
            return []

    def list_directory(self, path):
        ##Lista arquivos e informações dos diretórios 
        try:
            entries = []
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                try:
                    stats = os.stat(entry_path)  
                    if os.path.isdir(entry_path):
                        entry_type = "directory"
                        size = 0
                    else:
                        entry_type = "file"
                        size = os.path.getsize(entry_path) 

                    entries.append({
                        "name": entry,
                        "type": entry_type,
                        "size": size, 
                        "permissions": self._get_permissions(stats.st_mode),
                        "last_modified": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        "tree_id": entry_path
                    })
                except Exception as e:
                    print(f"Error reading {entry_path}: {e}")
            return entries
        except Exception as e:
            print(f"Error listing directory {path}: {e}")
            return []

    def _get_permissions(self, mode):
        ##Permissões do arquivo
        return stat.filemode(mode)
    
    def get_directory_size(self, directory): 
        ##Pega o tamanho do arquivo com o comando du do linux
        try:
            output = subprocess.check_output(['du', '-sb', directory], stderr=subprocess.DEVNULL)
            return int(output.split()[0])
        except subprocess.CalledProcessError:
            print(f"Erro ao acessar {directory} com 'du'. Ignorando.")
            return 0
        except FileNotFoundError:
            print("O comando 'du' não está disponível no sistema.")
            return 0
        except Exception as e:
            print(f"Erro inesperado ao calcular tamanho de {directory}: {e}")
            return 0

    #Atualiza o tamanho em um thread separada
    def update_directory_size(self, directory, entries,callback):

        if self.stop_directory_size_thread.is_set() or directory in self.processed_directories:
            return

        with self.dir_lock:
            if directory in self.processed_directories:
                return
            self.processed_directories.add(directory)

        try: 
            size = self.get_directory_size(directory)
            for entry in entries:
                if entry["name"] == os.path.basename(directory):
                    entry["size"] = size
                    if callback:
                        callback(entry)
                    break

        except Exception as e:
            print(f"Erro ao atualizar entrada {entry['name']}: {e}")

    #Para a thread caso mude o diretório selecionado   
    def stop_directory_size_update(self):
        self.stop_directory_size_thread.set()

    #Começa a thread para calculo do tamanho
    def start_directory_size_update(self):
        self.stop_directory_size_thread.clear()
        self.processed_directories.clear()


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
            with open(f"/proc/{pid}/smaps", "r") as f:
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

    #Acesssa os recursos abertos/alocados pelo processo
    def get_open_files(self):
        open_files = []
        fd_path = f"/proc/{self.pid}/fd/"
        try:
            if os.path.exists(fd_path):
                for fd in os.listdir(fd_path):
                    try:
                        file_path = os.readlink(os.path.join(fd_path, fd))
                        open_files.append({
                            "fd": fd,
                            "file_path": file_path
                        })
                    except OSError:
                        continue
        except Exception as e:
            print(f"Erro ao obter arquivos abertos para PID {self.pid}: {e}")
        return open_files
    
    #Acessa as informações de entrada e saída do processo com /proc
    def get_io_stats(self):
        io_stats = {}
        io_path = f"/proc/{self.pid}/io"
        try:
            with open(io_path, "r") as f:
                for line in f:
                    key, value = line.strip().split(":")
                    io_stats[key.strip()] = int(value.strip())
        except Exception as e:
            print(f"Erro ao obter estatísticas de E/S para PID {self.pid}: {e}")
        return io_stats

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
            "uptime": self.get_uptime(),
            "open_files": self.get_open_files(), 
            "io_stats": self.get_io_stats()
        }

# Lista todos os processos disponíveis no sistema
def list_all_processes():
    process_lock = threading.Lock()
    processes = []
    with process_lock:
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
