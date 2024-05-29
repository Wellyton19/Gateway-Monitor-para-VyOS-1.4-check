#!/bin/bash

# Endereços IP externos para verificação
external_ips=("8.8.8.8" "200.160.2.3" "157.240.222.35")
log_file="/var/log/gateway_monitor.log"
lock_file="/var/run/link_10.py.lock"  # Arquivo de bloqueio

# Variáveis para tabela 10
interface_10="eth0.100"
gateway_10="10.70.100.1"  # Substitua pelos seus gateways reais
gateway_11="10.70.200.1"  # Substitua pelos seus gateways reais

# Variáveis para notificação por WhatsApp
api_url="http://10.70.30.31:3000/client/sendMessage/c88af53241b2451ca3609f3260d73bbc24052024"
chat_id="556799673621@c.us"  # Substitua pelo seu chat ID

# Função para adicionar log
log() {
    echo "$(date): $1" >> $log_file
}

# Função para verificar conectividade
check_connectivity() {
    local interface=$1
    local gateway=$2
    local ping_attempts=3  # Número de tentativas de ping
    for ip in "${external_ips[@]}"; do
        for (( i=0; i<$ping_attempts; i++ )); do
            ping -I $interface -c 1 -w 1 $ip > /dev/null
            if [ $? -eq 0 ]; then
                ping -I $interface -c 1 -w 1 $gateway > /dev/null
                if [ $? -eq 0 ]; then
                    return 0
                fi
            fi
        done
    done
    return 1
}

# Função para enviar mensagem via WhatsApp (corrigida)
send_whatsapp_message() {
    local message=$1
    curl -X POST "$api_url" \
        -H "accept: */*" \
        -H "Content-Type: application/json" \
        -d "{\"chatId\": \"$chat_id\",\"contentType\": \"string\",\"content\": \"$message\"}" > /dev/null 2>&1
}

# Verificar se o script já está em execução
if [ -f "$lock_file" ]; then
    echo "O script link_10.py já está em execução."
    exit 1
fi

# Criar o arquivo de bloqueio
touch "$lock_file"

last_gateway=""  # Armazenar o último gateway ativo

# Trap para remover o arquivo de bloqueio ao receber SIGINT ou SIGTERM
trap 'rm "$lock_file"; exit 0' SIGINT SIGTERM

while true; do
    # Verificar a rota padrão atual na tabela 10
    current_gateway=$(ip route show table 10 | awk '/default/ {print $3}') 

    ping_success=0  # Contador de pings bem-sucedidos
    for (( i=0; i<3; i++ )); do  # Tentar 3 pings antes de considerar inativo
        ping -I $interface_10 -c 1 -w 1 $gateway_10 > /dev/null && check_connectivity $interface_10 $gateway_10
        if [ $? -eq 0 ]; then
            ping_success=$((ping_success + 1))
        fi
        sleep 1  # Aguardar 1 segundo entre os pings
    done

    if [ $ping_success -lt 2 ]; then  # Considerar inativo se menos de 2 pings forem bem-sucedidos
        if [ "$current_gateway" != "$gateway_11" ]; then  # Rota ainda não foi alterada
            log "Gateway da tabela 10 ($gateway_10) inativo ou sem conectividade externa, alterando para $gateway_11."
            ip route replace default via $gateway_11 table 10 || log "Erro ao substituir a rota na tabela 10."
            send_whatsapp_message "Gateway principal ($gateway_10) inativo, alternado para o secundário ($gateway_11)."
            last_gateway="$gateway_11"
        fi
    else  # Gateway principal está ativo
        if [ "$current_gateway" != "$gateway_10" ]; then  # Rota precisa ser corrigida para o gateway principal
            log "Gateway da tabela 10 ($gateway_10) ativo e com conectividade externa, alterando para $gateway_10."
            ip route replace default via $gateway_10 table 10 || log "Erro ao substituir a rota na tabela 10."
            if [ "$last_gateway" == "$gateway_11" ]; then  # Só enviar mensagem se estava no gateway secundário
                send_whatsapp_message "Gateway principal ($gateway_10) voltou a funcionar, alternado de volta."
            fi
            last_gateway="$gateway_10"
        fi
    fi

    sleep 5  # Intervalo de verificação (5 segundos)
done

# Remover o arquivo de bloqueio ao finalizar o script (não será mais necessário com o trap)
