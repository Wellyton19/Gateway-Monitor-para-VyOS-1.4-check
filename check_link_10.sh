#!/bin/bash

# ... (endereços IP externos, log_file, variáveis para tabela 10, variáveis para WhatsApp)

# Funções log(), check_connectivity() e send_whatsapp_message() (sem alterações)

# Nome do script principal (com caminho absoluto)
script_name="/home/vyos/link_10_com_whattapp"
lock_file="/var/run/$script_name.lock"  # Arquivo de bloqueio

# Verificar se o script principal está em execução e se o arquivo de bloqueio existe
if ! pgrep -f "$script_name" > /dev/null && [ -f "$lock_file" ]; then
    echo "$(date): O script $script_name não está em execução, mas o arquivo de bloqueio existe. Removendo o bloqueio e iniciando..." >> /var/log/gateway_monitor.log
    rm "$lock_file"
    nohup bash "$script_name.py" >> /var/log/gateway_monitor.log 2>&1 &
    disown
elif ! pgrep -f "$script_name" > /dev/null; then
    echo "$(date): O script $script_name não está em execução. Iniciando..." >> /var/log/gateway_monitor.log
    nohup bash "$script_name.py" >> /var/log/gateway_monitor.log 2>&1 &
    disown
else
    echo "$(date): O script $script_name já está em execução." >> /var/log/gateway_monitor.log
fi

sleep 5  # Aguardar 5 segundos antes de remover o bloqueio (se necessário)
rm -f "$lock_file"  # Forçar a remoção do arquivo de bloqueio
