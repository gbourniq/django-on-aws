# Makefile helpers

# Cosmetics
RED := "\e[1;31m"
YELLOW := "\e[1;33m"
GREEN := "\033[32m"
NC := "\e[0m"
INFO := bash -c 'printf ${YELLOW}; echo "[INFO] $$1"; printf ${NC}' MESSAGE
MESSAGE := bash -c 'printf ${NC}; echo "$$1"; printf ${NC}' MESSAGE
SUCCESS := bash -c 'printf ${GREEN}; echo "[SUCCESS] $$1"; printf ${NC}' MESSAGE
WARNING := bash -c 'printf ${RED}; echo "[WARNING] $$1"; printf ${NC}' MESSAGEs
