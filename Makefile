# Nome do interpretador Python
PYTHON = python3

# Nome do arquivo principal
MAIN = main.py

# Instalar dependências (com sudo, se necessário)
install:
	sudo pip install -r requirements.txt

# Rodar o arquivo principal (com privilégios elevados)
run:
	sudo $(PYTHON) $(MAIN)

# Verificar estilo de código com flake8 (não requer sudo)
lint:
	flake8 . --exclude=env,venv --max-line-length=88

# Limpar arquivos compilados ou temporários (não requer sudo)
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Criar ou atualizar o arquivo requirements.txt (não requer sudo)
freeze:
	pip freeze > requirements.txt

# Ajuda para lembrar comandos
help:
	@echo "Comandos disponíveis:"
	@echo "  install    - Instala as dependências listadas em requirements.txt (requer sudo)"
	@echo "  run        - Executa o arquivo main.py como root"
	@echo "  lint       - Verifica o estilo do código"
	@echo "  clean      - Remove arquivos temporários e compilados"
	@echo "  freeze     - Atualiza o arquivo requirements.txt com as dependências instaladas"
