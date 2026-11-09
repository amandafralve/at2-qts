# Transparência de uso de IA

- **Ferramenta:** assistente de IA integrado ao Copilot SDK no VS Code.
- **Uso nesta revisão:** análise dos requisitos, correção da aplicação e dos teste, criação da página.
- **Alterações auxiliadas por IA:** rotas e schemas da API, repositório em memória, integração do template Jinja2, fixtures, factory, cenário Locust e instruções do README.
- **Auditoria:** a suíte `uv run pytest -v` foi executada; os 22 testes passaram sem warnings. O cenário Locust foi executado com 20 usuários, spawn rate de 5/s e duração de 60 s; os resultados medidos e o limite não atingido estão registrados no README. 

