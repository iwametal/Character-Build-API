## Descrição da Alteração
<!-- Resuma de forma clara e objetiva o que foi implementado ou corrigido neste Pull Request -->

## Tipo de Mudança (Gitflow)
- [ ] `feature/*` — Nova funcionalidade (destino: `develop`)
- [ ] `bugfix/*` — Correção de bug não emergencial (destino: `develop`)
- [ ] `release/*` — Preparação de nova versão (destino: `main` e `develop`)
- [ ] `hotfix/*` — Correção crítica em produção (destino: `main` e `develop`)
- [ ] `chore` / `docs` — Infraestrutura, CI/CD ou documentação

## Checklist de Governança SDD & Qualidade
- [ ] O arquivo `files/PLAN.md` foi atualizado com o progresso da tarefa correspondente.
- [ ] Os contratos Pydantic v2 e rotas respeitam `files/SPEC.md`, `files/STYLEGUIDE.md` e `files/character_build.openapi.json`.
- [ ] Todos os erros HTTP seguem o padrão **RFC 9457 (Problem Details / `ApiError`)**.
- [ ] Consultas ORM utilizam SQLAlchemy 2.0 com `selectinload`/`joinedload` prevenindo queries N+1.
- [ ] A suíte automatizada (`pytest -v`) foi executada localmente e obteve **100% de aprovação**.
- [ ] Nenhuma credencial, token JWT real ou chave AWS foi commitada no repositório.

## Como Testar
```bash
pytest -v
```
