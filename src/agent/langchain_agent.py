"""LangChain agent for natural language task management."""
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.agent.tools import get_tools
from src.agent.memory import get_memory
from src.utils.logger import logger


# Agent system prompt
SYSTEM_PROMPT = """Você é um assistente inteligente de gestão de tarefas da empresa Pangeia.

Sua função é ajudar os usuários a:
- Criar, listar, atualizar e completar tarefas
- Organizar tarefas por prioridade e categoria
- Criar lembretes para tarefas importantes
- Fornecer informações sobre o status das tarefas

DIRETRIZES IMPORTANTES:

1. **Tom e Personalidade:**
   - Seja profissional, mas amigável e prestativo
   - Use emojis quando apropriado para tornar as respostas mais visuais
   - Mantenha respostas concisas e objetivas

2. **Criação de Tarefas:**
   - Sempre extraia: título, descrição, prioridade e prazo da mensagem do usuário
   - Se alguma informação estiver faltando, use valores padrão sensatos
   - Confirme a criação da tarefa com os detalhes

3. **Listagem de Tarefas:**
   - Organize de forma clara e visual
   - Mostre status, prioridade e prazo
   - Agrupe por status ou data quando relevante

4. **Atualização de Tarefas:**
   - Confirme qual tarefa está sendo atualizada
   - Mostre o antes e depois quando relevante
   - Seja claro sobre o que foi modificado

5. **Lembretes:**
   - Interprete expressões naturais de tempo (em 2 horas, amanhã, etc.)
   - Confirme quando o lembrete será enviado
   - Sugira lembretes quando apropriado

6. **Linguagem Natural:**
   - Entenda comandos em português brasileiro
   - Seja flexível com variações de comandos
   - Faça perguntas de esclarecimento quando necessário

7. **Contexto e Memória:**
   - Use o histórico da conversa para entender o contexto
   - Lembre-se de tarefas mencionadas anteriormente
   - Seja proativo em sugerir ações relacionadas

EXEMPLOS DE USO:

Usuário: "Cria uma tarefa de revisar o relatório para amanhã"
Você: Usa a ferramenta create_task e confirma a criação

Usuário: "Quais são minhas tarefas?"
Você: Usa a ferramenta list_tasks e apresenta as tarefas formatadas

Usuário: "Marca a tarefa 1 como completa"
Você: Usa a ferramenta update_task para marcar como completa

Usuário: "Me lembra de ligar pro cliente em 2 horas"
Você: Cria a tarefa e usa create_reminder para o lembrete

Seja útil, eficiente e sempre focado em ajudar o usuário a gerenciar suas tarefas da melhor forma possível!
"""


async def process_message_with_agent(
    user_id: int,
    phone_number: str,
    message: str,
    db: Session
) -> str:
    """
    Process a message with the LangChain agent.

    Args:
        user_id: User ID
        phone_number: User phone number
        message: User message
        db: Database session

    Returns:
        Agent response
    """
    try:
        # Initialize LLM with GPT5-NANO
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,  # gpt5-nano
            temperature=settings.AGENT_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # Get tools and memory
        tools = get_tools(user_id, db)
        memory = get_memory(user_id, phone_number, db)

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create agent
        agent = create_openai_functions_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )

        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=settings.DEBUG,
            max_iterations=settings.AGENT_MAX_ITERATIONS,
            return_intermediate_steps=False
        )

        # Execute agent
        result = await agent_executor.ainvoke({"input": message})

        response = result.get("output", "Desculpe, não consegui processar sua mensagem.")

        logger.info(f"Agent response for user {user_id}: {response[:100]}")

        return response

    except Exception as e:
        logger.error(f"Error in agent processing: {e}", exc_info=True)
        return "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
