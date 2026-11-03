# Aplicação do Smith

Chatbot em Streamlit que conversa com o Gemini usando a carteira fictícia da pasta `data/`.

## Arquivos

| Arquivo | Função |
|---------|--------|
| `app.py` | Interface do chat em Streamlit, abertura proativa e alerta de valores não encontrados |
| `agente.py` | Carrega os dados, faz os cálculos (dias de aplicação, faixa de IR, custo das taxas, come-cotas), monta o contexto, chama o Gemini e valida a resposta |
| `config.py` | Lê a chave e o modelo do arquivo `.env` e define os caminhos do projeto |

O system prompt é lido diretamente de [`docs/03-prompts.md`](../docs/03-prompts.md), então documentação e código usam sempre o mesmo texto.

## Como Rodar

**1. Instale as dependências** (na raiz do projeto):

```bash
pip install -r requirements.txt
```

**2. Crie uma chave de API gratuita** em [Google AI Studio](https://aistudio.google.com/) (sem ativar faturamento).

**3. Crie o arquivo `.env` na raiz do projeto:**

```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.5-flash-lite
```

O `.env` está no `.gitignore` e nunca deve ser enviado ao GitHub.

**4. Rode a aplicação** (na raiz do projeto):

```bash
python -m streamlit run src/app.py
```

O chat abre no navegador em `http://localhost:8501`.

## Observações

- **Modelo:** foi usado o `gemini-3.5-flash-lite` por ter limite gratuito maior (500 requisições por dia) que o `gemini-3.8-flash` (20 por dia). Para trocar, basta alterar `GEMINI_MODEL` no `.env`.
- **Erros da API:** se o Gemini estiver sobrecarregado (erro 503) ou o limite gratuito for atingido (erro 429), o app mostra um aviso e pede para tentar de novo.
- **Privacidade:** no plano gratuito, o Google pode usar as mensagens para melhorar seus modelos. Por isso o projeto usa apenas dados fictícios. Não digite dados reais no chat.