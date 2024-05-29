README - Monitoramento e Failover de Gateway com Notificação por WhatsApp
Este projeto consiste em dois scripts Bash que trabalham em conjunto para monitorar a conectividade de um gateway de rede e realizar failover automático para um gateway secundário em caso de falha. Além disso, o sistema envia notificações por WhatsApp para informar sobre as mudanças de status do gateway.

check_link_10.sh
Função:

Verifica periodicamente se o script principal (link_10.py) está em execução.
Se o script principal não estiver em execução, ele o inicia em segundo plano.
Garante que apenas uma instância do script principal esteja ativa, evitando conflitos.
Remove o arquivo de bloqueio (/var/run/link_10.py.lock) se ele existir e o script principal não estiver em execução.
Registra as ações em um arquivo de log (/var/log/gateway_monitor.log).
Como Usar:

Salve o script como check_link_10.sh.

Dê permissão de execução:. chmod +x check_link_10.sh

Configure o cron para executar o script periodicamente (por exemplo, a cada 5 minutos):

Bash
*/5 * * * * /bin/bash /home/vyos/check_link_10.sh >> /var/log/cron.log 2>&1
Use o código com cuidado.
content_copy
link_10.py
Função:

Monitora a conectividade do gateway principal (gateway_10) da tabela de roteamento 10.
Se o gateway principal falhar (ficar inativo ou sem acesso à internet), alterna automaticamente para o gateway secundário (gateway_11).
Quando o gateway principal volta a funcionar, alterna de volta para ele.
Envia notificações por WhatsApp informando sobre as mudanças de status do gateway (ativo/inativo, alternado para principal/secundário).
Mantém um registro detalhado das verificações e ações no arquivo de log /var/log/gateway_monitor.log.
Como Usar:

Salve o script como link_10.py.
Dê permissão de execução:. chmod +x link_10.py
Personalize as variáveis no início do script:
external_ips: Endereços IP externos para testar a conectividade com a internet.
interface_10: Interface de rede utilizada.
gateway_10: Endereço IP do gateway principal.
gateway_11: Endereço IP do gateway secundário.
api_url: URL da API do WhatsApp que você está usando.
chat_id: ID do chat do WhatsApp para onde as notificações serão enviadas.
Execute o script em segundo plano usando o check_link_10.sh, que será gerenciado pelo cron.
Observações:

Ambos os scripts devem estar no mesmo diretório ou você deve ajustar o caminho no script check_link_10.sh.
Certifique-se de ter permissões suficientes (geralmente root) para executar os comandos nos scripts.
Adapte os endereços IP, interface e chat ID às suas configurações específicas.
Para configurar o envio de mensagens por WhatsApp, você precisará de uma API ou serviço que permita enviar mensagens programaticamente. O script usa o curl para interagir com a API, mas você precisará fornecer a URL e os parâmetros corretos para a sua API específica.
Com este sistema, você terá um monitoramento confiável da sua conexão de internet, com failover automático e notificações em tempo real caso ocorra alguma falha no gateway principal.
