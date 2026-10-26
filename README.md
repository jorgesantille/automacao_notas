# 📄 Automação de Lançamento de Notas e Recibos (WhatsApp ➡️ Google Drive)

Sistema automatizado em Python/Flask para receção de notas fiscais e recibos enviados via WhatsApp, extração de conteúdos em Base64 e salvamento automático numa pasta específica do **Google Drive**.

O projeto conta com suporte a execução local (via Docker/Waitress) e está configurado para deploy contínuo em ambiente de nuvem (Render).

---

## 🛠️ Arquitetura do Sistema

1. **WhatsApp (Evolution API):** O utilizador envia uma imagem/recibo pelo WhatsApp (com ou sem legenda).
2. **Webhook (Flask App):** O webhook recebe o evento `MESSAGES_UPSERT` contendo os dados da mensagem e a imagem em formato Base64.
3. **Tratamento de Dados:** 
   - Extrai a legenda para categorizar o gasto (ex: *Combustível*, *Alimentação*, *Ferramentas*).
   - Calcula a semana correspondente do ano (`isocalendar`).
   - Gera um nome padronizado para o ficheiro (ex: `Combustivel_Semana_43_20261026_132800.jpg`).
4. **Google Drive API:** Realiza o upload do ficheiro diretamente para a pasta configurada no Google Drive.

---

## 📁 Estrutura do Projeto

```text
automacao_notas/
├── extrair_nota.py      # Aplicação principal (Flask + Google Drive API)
├── run.py               # Script de execução em produção (Waitress WSGI)
├── docker-compose.yml   # Configuração do container Docker (Evolution API + PostgreSQL)
├── credentials.json     # Credenciais OAuth 2.0 do Google Cloud (não versionar)
├── token.json           # Token de acesso do Google Drive gerado (não versionar)
├── requirements.txt     # Dependências do projeto em Python
├── Procfile             # Comando de inicialização no Render
└── README.md            # Documentação do projeto# automacao_notas
