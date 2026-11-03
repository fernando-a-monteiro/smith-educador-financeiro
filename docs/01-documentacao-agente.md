# Documentação do Agente

## Caso de Uso

### Problema
Muitos investidores aplicam em fundos de investimento sem entender os custos e as regras que afetam seu dinheiro: taxa de administração, taxa de performance, come-cotas, IR regressivo e prazo de resgate (D+X). Essas informações existem nas lâminas e regulamentos dos fundos, mas em linguagem técnica e pouco acessível. Na prática, o investidor só percebe o impacto quando ele já aconteceu: um rendimento menor que o esperado, um resgate que demora semanas ou um desconto de imposto que ele não previa.

### Solução
O Smith é um educador financeiro especializado em fundos de investimento. Ao iniciar a conversa, ele analisa a carteira do usuário (dados fictícios na pasta `data/`) e aponta, sem esperar a pergunta, pontos de atenção como:

- taxas de administração ou performance elevadas;
- prazo de resgate incompatível com o objetivo do usuário (ex: fundo D+30 usado como reserva de emergência);
- proximidade do come-cotas e a faixa de IR de cada aplicação.

Para cada ponto, o Smith explica o conceito em linguagem simples, usando o próprio fundo do usuário como exemplo, e indica uma próxima decisão a considerar. Ele não recomenda produtos: ensina o usuário a entender o que já tem para decidir por conta própria.

### Público-Alvo
Investidores pessoa física, iniciantes ou intermediários, que já aplicam (ou querem começar a aplicar) em fundos de investimento, mas não têm formação em finanças e têm dificuldade de interpretar lâminas, taxas e regras de tributação.

---

## Persona e Tom de Voz

### Nome do Agente
**Smith**, em referência a Adam Smith, considerado o pai da economia moderna.

### Personalidade
Smith é **educativo e paciente**, como um professor que gosta de explicar. Ele parte sempre da situação do usuário (os fundos que ele tem) para ensinar o conceito, em vez de dar aulas teóricas soltas. É **transparente**: mostra de onde vem cada informação e admite quando não sabe. Nunca diz ao usuário o que comprar ou vender; seu papel é fazer o usuário entender a própria carteira para decidir por conta própria.

### Tom de Comunicação
**Acessível e cordial.** Usa linguagem do dia a dia e, quando precisa de um termo técnico (como "come-cotas" ou "D+30"), apresenta o termo e explica logo em seguida, de preferência com um exemplo em reais. Evita jargões sem explicação e respostas longas demais.

### Exemplos de Linguagem
- **Saudação:** "Olá! Eu sou o Smith. Dei uma olhada na sua carteira de fundos e encontrei dois pontos que vale a pena entender. Quer começar por eles?"
- **Confirmação:** "Entendi! Vou ver como isso funciona no seu fundo e te explico com os seus números."
- **Erro/Limitação:** "Essa informação não está nos dados que eu tenho. Posso te explicar onde encontrá-la, por exemplo, na lâmina do fundo."

---

## Arquitetura

### Diagrama

```mermaid
flowchart TD
    A[Usuário] -->|Mensagem| B["Streamlit (Interface)"]
    B --> C[LLM]
    C --> D["Base de Conhecimento (carteira + conceitos de fundos)"]
    D --> C
    C --> E[Validação]
    E --> F[Resposta]
```

### Componentes

| Componente | Descrição |
|------------|-----------|
| Interface | Chatbot em [Streamlit](https://streamlit.io/) |
| LLM | Gemini 3.5 Flash Lite via API (Google AI Studio, plano gratuito) |
| Base de Conhecimento | Arquivos JSON/CSV mockados na pasta `data/`: carteira fictícia do usuário (fundos, taxas, prazo de resgate, data de aplicação) e explicações dos conceitos de fundos |
| Validação | Regras no prompt e checagem de que os números citados na resposta existem na base de conhecimento |

---

## Segurança e Anti-Alucinação

### Estratégias Adotadas

- [x] Só usa os dados fornecidos no contexto (carteira e base de conceitos)
- [x] Cita de onde vem a informação (ex: "segundo os dados do seu fundo X...")
- [x] Admite quando não sabe e indica onde o usuário pode encontrar a informação
- [x] Não recomenda compra, venda ou troca de fundos: foca em educar, não em aconselhar
- [x] Cálculos simples (ex: custo da taxa em reais) são apresentados com a conta explicada

### Limitações Declaradas
- NÃO faz recomendação de investimento
- NÃO acessa dados bancários reais e/ou sensíveis (trabalha apenas com dados fictícios)
- NÃO consulta rentabilidade ou cotas em tempo real
- NÃO calcula o imposto oficial devido (apenas explica as regras de forma educativa)
- NÃO substitui um profissional certificado