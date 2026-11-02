# Base de Conhecimento

## Dados Utilizados

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `perfil_investidor.json` | JSON | Conhecer o objetivo, as metas e a tolerância a risco do usuário, para comparar com os fundos que ele tem |
| `carteira_fundos.json` | JSON | Fundos do usuário (taxas, prazos de resgate, datas e valores): base da análise proativa |
| `conceitos_fundos.json` | JSON | Explicações dos conceitos de fundos que o Smith usa para ensinar sem inventar definições |
| `historico_atendimento.csv` | CSV | Dúvidas anteriores do usuário sobre fundos, para dar continuidade às conversas |

---

## Adaptações nos Dados

Os dados originais do repositório foram adaptados para o tema de fundos de investimento:

- **`perfil_investidor.json`**: mantido o cliente fictício João Silva (perfil moderado, não aceita risco, objetivo de reserva de emergência). As datas das metas foram atualizadas e foi adicionado o campo `conhecimento_fundos`, para o Smith ajustar o nível da explicação.
- **`produtos_financeiros.json` → `carteira_fundos.json`**: o catálogo de produtos foi substituído pelos fundos que o cliente já possui. O catálogo trazia o campo `indicado_para`, uma recomendação, o que contradiz a limitação do Smith de não recomendar investimentos.
- **`conceitos_fundos.json`** (novo): definições de taxa de administração, taxa de performance, come-cotas, IR regressivo, tributação de fundos de ações, IOF, prazo de resgate e lâmina.
- **`historico_atendimento.csv`**: os atendimentos genéricos foram trocados por interações sobre fundos.
- **`transacoes.csv`**: removido, pois controle de gastos está fora do escopo do Smith.

A carteira foi montada para gerar situações reais de aprendizado:

| Fundo | Situação que o Smith deve apontar |
|-------|-----------------------------------|
| Fundo DI Conservador | Taxa de administração de 1,5% ao ano em um fundo DI, o que explica a dúvida em aberto no histórico ("rendeu menos que o CDI") |
| Fundo Multimercado Macro | Resgate em D+30 usado como reserva de emergência, taxa de performance e aplicação com menos de 180 dias (faixa de 22,5% de IR) |
| Fundo de Ações Brasil | Saldo abaixo do valor aplicado para um cliente que não aceita risco; não tem come-cotas |
| DI e Multimercado | Come-cotas no fim de novembro |

---

## Estratégia de Integração

### Como os dados são carregados?
Os arquivos JSON e CSV são carregados com Python (`json` e `pandas`) no início da sessão. Antes de chamar o LLM, o código calcula os valores que dependem de conta, para que o modelo não precise fazê-la: dias desde cada aplicação, faixa atual do IR regressivo, custo anual da taxa de administração em reais e dias até o próximo come-cotas.

### Como os dados são usados no prompt?
Como a base é pequena, todo o contexto (perfil, carteira com os valores calculados, conceitos e histórico) é incluído no system prompt a cada conversa. O prompt instrui o Smith a responder apenas com base nesse contexto e a citar de qual fundo ou conceito vem cada informação.

---

## Exemplo de Contexto Montado

```
Data de referência: 02/11/2026

Dados do Cliente:
- Nome: João Silva
- Perfil: Moderado (não aceita risco)
- Conhecimento em fundos: iniciante
- Objetivo principal: Construir reserva de emergência (meta: R$ 15.000 até 06/2027)

Carteira de Fundos:
1. Fundo DI Conservador: saldo R$ 6.420,00 | taxa adm. 1,50% a.a. (≈ R$ 96/ano)
   | resgate D+0 | aplicado há 602 dias (IR: 17,5%) | uso: reserva de emergência
2. Fundo Multimercado Macro: saldo R$ 4.190,00 | taxa adm. 2,00% a.a. (≈ R$ 84/ano)
   + performance 20% acima do CDI | resgate D+30 / D+1 | aplicado há 175 dias (IR: 22,5%)
   | uso: reserva de emergência
3. Fundo de Ações Brasil: saldo R$ 1.910,00 (aplicado R$ 2.000,00)
   | taxa adm. 2,00% a.a. | resgate D+1 / D+2 | IR de 15% no resgate | sem come-cotas

Próximo come-cotas: 30/11/2026 (em 28 dias) | fundos 1 e 2

Última dúvida em aberto:
- 05/10/2026: "Por que o Fundo DI Conservador rendeu menos que o CDI?"
```