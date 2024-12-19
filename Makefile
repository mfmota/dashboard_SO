# Nome do interpretador Python
PYTHON = python3

# Nome do arquivo principal
MAIN = main.py

# Instalar dependências
install:
	pip install -r requirements.txt

# Rodar o arquivo principal
run:
	$(PYTHON) $(MAIN)

# Verificar estilo de código com flake8
lint:
	flake8 . --exclude=env,venv --max-line-length=88

# Limpar arquivos compilados ou temporários
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Criar um gráfico de dependências
freeze:
	pip freeze > requirements.txt

# Ajuda para lembrar comandos
help:
	@echo "Comandos disponíveis:"
	@echo "  install    - Instala as dependências listadas em requirements.txt"
	@echo "  run        - Executa o arquivo main.py"
	@echo "  lint       - Verifica o estilo do código"
	@echo "  clean      - Remove arquivos temporários e compilados"
	@echo "  freeze     - Atualiza o arquivo requirements.txt com as dependências instaladas"
