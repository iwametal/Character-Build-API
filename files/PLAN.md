# PLAN.md — Plano Diretor de Implementação Técnica (SDD + ORM + Auth)
## Character Build API v2 (FastAPI + SQLAlchemy 2.0 + Pydantic v2 + JWT / RBAC)

**Papel Ativo:** `[Backend Coder]`  
**Status do Plano:** Todas as 8 fases concluídas com sucesso (48/48 testes no pytest, Docker + Kubernetes com 5 réplicas, Gitflow e CI/CD GitHub Actions -> AWS estruturados e prontos para ativação futura).  
**Metodologia:** Spec-Driven Development (SDD) baseado em `files/SPEC.md`, `files/STYLEGUIDE.md` e `files/character_build.openapi.json`.

---

## Sumário Executivo das Fases
- [x] **Fase 1:** Estrutura de diretórios e dependências (`requirements.txt`)
- [x] **Fase 2:** Extração e consolidação de schemas Pydantic v2 (Apidog + DTOs de Auth + RFC 9457)
- [x] **Fase 3:** Modelos ORM SQLAlchemy 2.0, relacionamentos (1:N, 1:1, N:1) e `database.py` com seed idempotente
- [x] **Fase 4:** Camada de exceções semânticas RFC 9457 e segurança (`security.py` com JWT + RBAC)
- [x] **Fase 5:** Implementação dos routers modulares (Auth, Characters, Equipamentos, Catálogo) e `main.py`
- [x] **Fase 6:** Suíte de testes automatizados com `pytest` (Auth, RBAC, Contratos das coleções e RFC 9457)
- [x] **Fase 7:** Conteinerização (Docker), Orquestração (Kubernetes com 5 réplicas & Docker Compose) e Gerenciador de Instâncias/Threads
- [x] **Fase 8:** Estratégia Gitflow (`.gitflow`) e Pipeline de CI/CD Estruturado (GitHub Actions -> AWS ECR/EKS)

---

## Checklist Granular de Execução Técnica

### Fase 1: Estrutura de Diretórios e requirements.txt
- [x] **1.1. Inicialização da Árvore de Diretórios da Aplicação**
  - [x] Criar diretório base `src/api/` e arquivo `src/api/__init__.py`.
  - [x] Criar subdiretório de roteamento `src/api/routers/` e arquivo `src/api/routers/__init__.py`.
  - [x] Criar subdiretório de testes `src/api/tests/` e arquivo `src/api/tests/__init__.py`.
- [x] **1.2. Especificação Estrita de Dependências (`src/api/requirements.txt`)**
  - [x] Declarar `fastapi>=0.115.0`
  - [x] Declarar `uvicorn[standard]>=0.30.0`
  - [x] Declarar `pydantic>=2.9.0`
  - [x] Declarar `pydantic-settings>=2.4.0`
  - [x] Declarar `sqlalchemy>=2.0.35`
  - [x] Declarar `pyjwt[crypto]>=2.9.0`
  - [x] Declarar `passlib[bcrypt]>=1.7.4` e/ou `bcrypt>=4.0.0`
  - [x] Declarar `python-multipart>=0.0.9`
  - [x] Declarar `httpx>=0.27.0`
  - [x] Declarar `pytest>=8.3.0`
- [x] **1.3. Validação do Ambiente Virtual e Instalação**
  - [x] Executar instalação no ambiente Python 3.12+ isolado (`pip install -r src/api/requirements.txt`).
  - [x] Validar importações preliminares sem conflitos de dependências.

---

### Fase 2: Extração de Schemas Pydantic v2 (Apidog + DTOs de Auth)
*Arquivo alvo:* `src/api/schemas.py`

- [x] **2.1. Configuração Base e Modelos Padrão Pydantic v2**
  - [x] Definir classe base ou `ConfigDict(populate_by_name=True, from_attributes=True)` para interoperabilidade com o ORM SQLAlchemy e suporte a `camelCase`/`snake_case`.
  - [x] Mapear o Enum de Segurança e Papéis: `UserRole(str, Enum)` com valores `"ADMIN"` e `"MEMBER"`.
- [x] **2.2. Schemas de Erro Semântico (RFC 9457 / Problem Details)**
  - [x] Criar `InvalidParam`: `name: str`, `reason: str`.
  - [x] Criar `ApiError`:
    - `type: str` (ex.: `"https://api.character-build.dev/errors/validation-error"`)
    - `title: str`
    - `status: int`
    - `detail: str`
    - `instance: str`
    - `invalidParams: list[InvalidParam] | None = None`
  - [x] Criar schema de compatibilidade com Apidog: `ErrorResponseSchema(status, code, message, details)`.
- [x] **2.3. DTOs de Autenticação e Usuário**
  - [x] `LoginRequestDTO` / `LoginRequestSchema`: aceitar `email` (formato email) ou `username`, e `password` (`min_length=6`).
  - [x] `UserResponse`: `id: str` (UUID), `name: str`, `email: str`, `role: UserRole`.
  - [x] `TokenResponseDTO` / `LoginResponseSchema`:
    - `accessToken` / `access_token: str`
    - `tokenType` / `token_type: str = "bearer"`
    - `expiresIn` / `expires_in: int = 3600`
    - `user: UserResponse | None = None`
- [x] **2.4. Schemas das Entidades de Catálogo e Referência (Apidog)**
  - [x] `GenderSchema`: `id: int | None`, `gender: str`.
  - [x] `RaritySchema`: `id: int | None`, `rarity: str`.
  - [x] `BodyPartSchema`: `id: int | None`, `body_part: str`.
  - [x] `StatusEffectSchema`: `id: int | None`, `status: str`, `duration: int | None`.
  - [x] `ElementSchema`: `id: int | None`, `element: str`, `strength: int | None`, `weakness: int | None`.
  - [x] `ElementResponseSchema`: `id: int`, `element: str`, `strength: ElementSchema | None`, `weakness: ElementSchema | None`.
  - [x] `JobAttributesSchema` e `JobResponseSchema`: `id: int | None`, `job: str`, `atk: int`, `def: int`, `hp: int`, `vigor: int`, `intelligence: int`.
  - [x] `RaceSchema` e `RaceResponseSchema`: `id: int | None`, `race: str`, `atk: int`, `def: int`, `hp: int`, `intelligence: int`, `mana: int`, `vigor: int`.
- [x] **2.5. Schemas de Habilidades e Magias**
  - [x] `MagicAbilitySchema`: `id: int | None`, `magic: str`, `damage: int`, `element: int`, `lv_required: int`, `mana_consumption: int`, `shield: int`, `status: int | None`.
  - [x] `MagicResponseSchema` / `MagicAbilityResponseSchema`: `id: int`, `magic: str`, `damage: int`, `element: ElementSchema | None`, `lv_required: int`, `mana_consumption: int`, `shield: int`, `status: StatusEffectSchema | None`.
  - [x] `PhysicalAbilitySchema`: `id: int | None`, `damage: int`, `lv_required: int`, `shield: int`, `status: int | None`.
  - [x] `PhysicalAbilityResponseSchema`: `id: int`, `damage: int`, `lv_required: int`, `shield: int`, `status: StatusEffectSchema | None`.
  - [x] `AbilitySchema`: `id: int | None`, `character: str | int` (UUID ou ID do personagem), `magic: int | None`, `physical: int | None`.
  - [x] `AbilityResponseSchema`: `id: int`, `character: CharacterResponseSchema | None`, `magic: MagicAbilityResponseSchema | None`, `physical: PhysicalAbilityResponseSchema | None`.
- [x] **2.6. Schemas de Equipamentos e Combate**
  - [x] `ArmorSchema`: `id: int | None`, `body_part: int`, `atk: int`, `def: int`, `hp: int`, `intelligence: int`, `vigor: int`, `rarity: int`.
  - [x] `ArmorResponseSchema`: `id: int`, `body_part: BodyPartSchema | None`, `atk: int`, `def: int`, `hp: int`, `intelligence: int`, `vigor: int`, `rarity: RaritySchema | None`.
  - [x] `WeaponSchema`: `id: int | None`, `name: str`, `atk: int`, `def: int`, `hp: int`, `intelligence: int`, `vigor: int`, `magic: int | None`.
  - [x] `WeaponResponseSchema`: `id: int`, `name: str`, `atk: int`, `def: int`, `hp: int`, `intelligence: int`, `vigor: int`, `magic: MagicAbilityResponseSchema | None`.
- [x] **2.7. Schemas Centrais: Character e Monster**
  - [x] `CharacterSchema`: `id: str | None` (UUID opcional na criação, gerado na API), `name: str`, `last_name: str`, `age: int`, `level: int`, `extra_mana: int = 0`, `gender: int`, `job: int`, `race: int`.
  - [x] `CharacterResponseSchema`: `id: str` (UUID), `name: str`, `last_name: str`, `age: int`, `level: int`, `extra_mana: int`, `gender: GenderSchema | None`, `job: JobAttributesSchema | None`, `race: RaceSchema | None`.
  - [x] `MonsterSchema`: `id: str | None` (UUID), `name: str`, `race: int | str`, `atk: int`, `def: int`, `hp: int`, `intelligence: int`, `vigor: int`.
  - [x] `MonsterResponseSchema`: `id: str` (UUID), `name: str`, `race: RaceSchema | None`, `atk: int`, `def: int`, `hp: int`, `intelligence: int`, `vigor: int`.

---

### Fase 3: Modelos ORM SQLAlchemy 2.0 e database.py com Seed
*Arquivos alvo:* `src/api/models.py`, `src/api/database.py`

- [x] **3.1. Configuração de Persistência (`src/api/database.py`)**
  - [x] Definir a classe declarativa base moderna `class Base(DeclarativeBase): pass`.
  - [x] Criar a engine SQLAlchemy apontando para `sqlite:///./character-build.db` com `connect_args={"check_same_thread": False}`.
  - [x] Configurar a fábrica de sessões `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`.
  - [x] Implementar a dependência `get_db()` usando gerador com bloco `try/finally` garantindo fechamento da sessão.
- [x] **3.2. Modelo de Autenticação e Usuário (`UserModel`)**
  - [x] Tabela: `users`.
  - [x] Campos:
    - `id: Mapped[str] = mapped_column(String(36), primary_key=True)` (UUID).
    - `name: Mapped[str] = mapped_column(String(100), nullable=False)`.
    - `email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)`.
    - `hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)`.
    - `role: Mapped[str] = mapped_column(String(20), nullable=False, default="MEMBER")`.
    - `created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)`.
    - `updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)`.
- [x] **3.3. Modelos ORM de Domínio (SQLAlchemy 2.0 Sintaxe Declarativa com `Mapped[...]`)**
  - [x] `GenderModel` (`genders`): `id: Mapped[int]`, `gender: Mapped[str]`.
  - [x] `RarityModel` (`rarities`): `id: Mapped[int]`, `rarity: Mapped[str]`.
  - [x] `BodyPartModel` (`body_parts`): `id: Mapped[int]`, `body_part: Mapped[str]`.
  - [x] `ElementModel` (`elements`): `id: Mapped[int]`, `element: Mapped[str]`, `strength_id: Mapped[int | None] = mapped_column(ForeignKey("elements.id"))`, `weakness_id: Mapped[int | None] = mapped_column(ForeignKey("elements.id"))`, e auto-relacionamentos `relationship`.
  - [x] `StatusEffectModel` (`status_effects`): `id: Mapped[int]`, `status: Mapped[str]`, `duration: Mapped[int]`.
  - [x] `JobModel` (`jobs`): `id: Mapped[int]`, `job: Mapped[str]`, `atk: Mapped[int]`, `def: Mapped[int]`, `hp: Mapped[int]`, `vigor: Mapped[int]`, `intelligence: Mapped[int]`.
  - [x] `RaceModel` (`races`): `id: Mapped[int]`, `race: Mapped[str]`, `atk: Mapped[int]`, `def: Mapped[int]`, `hp: Mapped[int]`, `intelligence: Mapped[int]`, `mana: Mapped[int]`, `vigor: Mapped[int]`.
  - [x] `MagicModel` (`magics`): `id: Mapped[int]`, `magic: Mapped[str]`, `damage: Mapped[int]`, `lv_required: Mapped[int]`, `mana_consumption: Mapped[int]`, `shield: Mapped[int]`, `element_id: Mapped[int] = mapped_column(ForeignKey("elements.id"))`, `status_id: Mapped[int | None] = mapped_column(ForeignKey("status_effects.id"))`, com `relationship("ElementModel")` e `relationship("StatusEffectModel")`.
  - [x] `PhysicalAbilityModel` (`physical_abilities`): `id: Mapped[int]`, `damage: Mapped[int]`, `lv_required: Mapped[int]`, `shield: Mapped[int]`, `status_id: Mapped[int | None] = mapped_column(ForeignKey("status_effects.id"))`, com `relationship("StatusEffectModel")`.
  - [x] `ArmorModel` (`armors`): `id: Mapped[int]`, `body_part_id: Mapped[int] = mapped_column(ForeignKey("body_parts.id"))`, `rarity_id: Mapped[int] = mapped_column(ForeignKey("rarities.id"))`, atributos de combate, com `relationship("BodyPartModel")` e `relationship("RarityModel")`.
  - [x] `WeaponModel` (`weapons`): `id: Mapped[int]`, `name: Mapped[str]`, atributos de combate, `magic_id: Mapped[int | None] = mapped_column(ForeignKey("magics.id"))`, com `relationship("MagicModel")`.
  - [x] `CharacterModel` (`characters`):
    - `id: Mapped[str] = mapped_column(String(36), primary_key=True)` (UUID gerado com `uuid4`).
    - `name: Mapped[str]`, `last_name: Mapped[str]`, `age: Mapped[int]`, `level: Mapped[int]`, `extra_mana: Mapped[int]`.
    - `gender_id: Mapped[int] = mapped_column(ForeignKey("genders.id"))`.
    - `job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))`.
    - `race_id: Mapped[int] = mapped_column(ForeignKey("races.id"))`.
    - Relacionamentos: `relationship("GenderModel")`, `relationship("JobModel")`, `relationship("RaceModel")` e `relationship("AbilityModel", back_populates="character")`.
  - [x] `AbilityModel` (`abilities`):
    - `id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)`.
    - `character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), nullable=False)`.
    - `magic_id: Mapped[int | None] = mapped_column(ForeignKey("magics.id"), nullable=True)`.
    - `physical_id: Mapped[int | None] = mapped_column(ForeignKey("physical_abilities.id"), nullable=True)`.
    - Relacionamentos: `relationship("CharacterModel", back_populates="abilities")`, `relationship("MagicModel")`, `relationship("PhysicalAbilityModel")`.
  - [x] `MonsterModel` (`monsters`): `id: Mapped[str] = mapped_column(String(36), primary_key=True)` (UUID), `name: Mapped[str]`, `race_id: Mapped[int] = mapped_column(ForeignKey("races.id"))`, atributos de combate, `relationship("RaceModel")`.
- [x] **3.4. Função de Seed Inicial e Idempotente (`init_db` e `seed_data`)**
  - [x] Criar tabelas com `Base.metadata.create_all(bind=engine)`.
  - [x] Criar ou atualizar os usuários de teste de forma idempotente:
    - **Admin:** `admin@fatec.sp.gov.br` / `Admin@2026` / Role `ADMIN`.
    - **Member:** `aluno@fatec.sp.gov.br` / `Aluno@2026` / Role `MEMBER`.
  - [x] Popular dados de referência base necessários para garantir a integridade referencial nas FKs durante execuções e testes:
    - Genders (ex.: "Feminino", "Masculino", "Não-binário")
    - Rarities (ex.: "Comum", "Raro", "Épico", "Lendário")
    - Body Parts (ex.: "Cabeça", "Tronco", "Membros", "Pés")
    - Elements (ex.: "Fogo", "Água", "Terra", "Vento")
    - Races (ex.: "Humano", "Elfo", "Anão", "Orc")
    - Jobs (ex.: "Guerreiro", "Mago", "Ladino", "Clérigo")
    - Status Effects (ex.: "Queimadura", "Congelamento", "Veneno")

---

### Fase 4: Exceções RFC 9457 e security.py (JWT + RBAC)
*Arquivos alvo:* `src/api/exceptions.py`, `src/api/security.py`

- [x] **4.1. Hierarquia de Exceções de Domínio RFC 9457 (`src/api/exceptions.py`)**
  - [x] Classe base `DomainException(Exception)` contendo `status_code`, `type_uri`, `title`, `detail`, `invalid_params`.
  - [x] `BadRequestException` (`400 Bad Request`, type: `https://api.character-build.dev/errors/bad-request`).
  - [x] `UnauthorizedException` (`401 Unauthorized`, type: `https://api.character-build.dev/errors/unauthorized`).
  - [x] `ForbiddenException` (`403 Forbidden`, type: `https://api.character-build.dev/errors/forbidden`).
  - [x] `NotFoundException` (`404 Not Found`, type: `https://api.character-build.dev/errors/not-found`).
  - [x] `ValidationException` (`422 Unprocessable Entity`, type: `https://api.character-build.dev/errors/validation-error`).
- [x] **4.2. Handlers Globais de Erro no Padrão RFC 9457 (`register_exception_handlers`)**
  - [x] Handler para `DomainException`: retornar `JSONResponse` com corpo `ApiError` estritamente tipado.
  - [x] Handler para `RequestValidationError` do FastAPI: interceptar falhas de validação do Pydantic, mapear erros para lista `invalidParams` com `name` e `reason`, retornando `status=422` com `ApiError`.
  - [x] Handler para `HTTPException` do FastAPI: converter erros padrão para o formato RFC 9457 com a URI de tipo adequada.
  - [x] Handler genérico para `Exception`: capturar exceções não tratadas retornando `500 Internal Server Error` sem vazar traces confidenciais.
- [x] **4.3. Implementação da Camada de Segurança (`src/api/security.py`)**
  - [x] Configurar contexto criptográfico para hash e verificação de senhas com `bcrypt` / `passlib` (`verify_password`, `get_password_hash`).
  - [x] Configurar parâmetros JWT: `SECRET_KEY`, `ALGORITHM = "HS256"`, `ACCESS_TOKEN_EXPIRE_MINUTES = 60`.
  - [x] Implementar `create_access_token(data: dict, expires_delta: timedelta | None = None) -> str`:
    - Inserir claims padrão: `sub` (ID do usuário), `email`, `role`, `iat`, `exp`.
  - [x] Implementar dependência `get_current_user`:
    - Extrair token via `HTTPBearer(auto_error=False)`.
    - Se token ausente, malformado ou expirado, lançar `UnauthorizedException` (401 RFC 9457).
    - Decodificar e validar token com `jwt.decode(..., algorithms=["HS256"])`.
    - Obter usuário no banco de dados; se não encontrado, lançar `UnauthorizedException` (401 RFC 9457).
  - [x] Implementar dependência `get_optional_current_user`:
    - Para rotas GET públicas ou semi-públicas: decodificar se token estiver presente; se ausente, retornar `None` sem bloquear.
  - [x] Implementar fábrica de dependência RBAC `require_role(required_roles: list[str])`:
    - Depende de `get_current_user`.
    - Verificar se `user.role` consta na lista de papéis autorizados.
    - Se usuário for `MEMBER` e a rota exigir `ADMIN` (ex.: deleção), lançar `ForbiddenException` (403 RFC 9457).

---

### Fase 5: Routers e main.py
*Arquivos alvo:* `src/api/routers/`, `src/api/main.py`

- [x] **5.1. Router de Autenticação (`src/api/routers/auth.py`)**
  - [x] `POST /api/v1/auth/login`:
    - Receber `LoginRequestDTO` (suportando email ou username).
    - Buscar usuário no banco pelo email/username.
    - Validar senha com `verify_password`. Se inválida, lançar `UnauthorizedException` (401 RFC 9457).
    - Gerar JWT com claims (`sub`, `email`, `role`) e responder `200 OK` com `TokenResponseDTO`.
  - [x] `GET /api/v1/auth/me`:
    - Protegido por `Depends(get_current_user)`.
    - Retornar `UserResponse` do usuário autenticado.
- [x] **5.2. Routers de Domínio — Padrão de Segurança e Transações**
  - [x] Regra de Segurança unificada em todas as coleções:
    - `GET` público (`get_optional_current_user`).
    - `POST`, `PUT`, `PATCH` autenticado (`require_role(["ADMIN", "MEMBER"])`).
    - `DELETE` restrito a administradores (`require_role(["ADMIN"])`).
  - [x] Regra Transacional: gerenciar `db.commit()`, `db.refresh()`, `db.rollback()` explicitamente.
  - [x] Prevenção de Queries N+1: aplicar `selectinload` ou `joinedload` em todas as relações mapeadas.
- [x] **5.3. Implementação dos Routers de Catálogo e Dados de Referência**
  - [x] `routers/genders.py`: CRUD `/api/v1/genders` e `/api/v1/genders/{id}`.
  - [x] `routers/rarities.py`: CRUD `/api/v1/rarities` e `/api/v1/rarities/{id}`.
  - [x] `routers/body_parts.py` (ou `body-parts.py`): CRUD `/api/v1/body-parts` e `/api/v1/body-parts/{id}`.
  - [x] `routers/elements.py`: CRUD `/api/v1/elements` e `/api/v1/elements/{id}` com `selectinload` para `strength` e `weakness`.
  - [x] `routers/status_effects.py` (ou `status-effects.py`): CRUD `/api/v1/status-effects` e `/api/v1/status-effects/{id}`.
  - [x] `routers/jobs.py`: CRUD `/api/v1/jobs` e `/api/v1/jobs/{id}`.
  - [x] `routers/races.py`: CRUD `/api/v1/races` e `/api/v1/races/{id}`.
- [x] **5.4. Implementação dos Routers de Magias, Habilidades e Equipamentos**
  - [x] `routers/magics.py`: CRUD `/api/v1/magics` e `/api/v1/magics/{id}` com `selectinload(MagicModel.element)` e `selectinload(MagicModel.status_effect)`.
  - [x] `routers/armors.py`: CRUD `/api/v1/armors` e `/api/v1/armors/{id}` com `selectinload(ArmorModel.body_part)` e `selectinload(ArmorModel.rarity)`.
  - [x] `routers/weapons.py`: CRUD `/api/v1/weapons` e `/api/v1/weapons/{id}` com `selectinload(WeaponModel.magic)`.
  - [x] `routers/monsters.py`: CRUD `/api/v1/monsters` e `/api/v1/monsters/{id}` (com IDs UUID e `selectinload(MonsterModel.race)`).
  - [x] `routers/abilities.py`: CRUD `/api/v1/abilities` e `/api/v1/abilities/{id}` com `selectinload` para `character`, `magic` e `physical`.
- [x] **5.5. Implementação do Router Central de Personagens (`src/api/routers/characters.py`)**
  - [x] `POST /api/v1/characters`:
    - Validação de existência de `gender_id`, `job_id`, `race_id` no banco (lançar 404/400 RFC 9457 caso inexistente).
    - Gerar UUID v4 se não fornecido.
    - Persistir `CharacterModel`, comitar, carregar relacionamentos e retornar `201 Created` com cabeçalho `Location: /api/v1/characters/{id}`.
  - [x] `GET /api/v1/characters`:
    - Listagem otimizada com `options(selectinload(CharacterModel.gender), selectinload(CharacterModel.job), selectinload(CharacterModel.race))` para prevenir consultas N+1.
  - [x] `GET /api/v1/characters/{id}`:
    - Consulta por UUID; se não encontrado, lançar `NotFoundException` (404 RFC 9457).
  - [x] `PUT /api/v1/characters/{id}`:
    - Substituição integral dos dados do personagem e atualização transacional.
  - [x] `PATCH /api/v1/characters/{id}`:
    - Atualização parcial dos campos presentes no payload.
  - [x] `DELETE /api/v1/characters/{id}`:
    - Restrito a role `ADMIN`. Se usuário autenticado for `MEMBER`, retornar `403 Forbidden` (RFC 9457).
    - Remove o personagem e habilidades vinculadas (ou cascata) retornando `204 No Content`.
- [x] **5.6. Configuração e Inicialização da Aplicação (`src/api/main.py`)**
  - [x] Criar gerenciador de contexto `lifespan` assíncrono para executar `init_db()` e `seed_data()`.
  - [x] Instanciar aplicação `FastAPI` com títulos, descrições e versões conforme o OpenAPI do projeto.
  - [x] Configurar middleware de CORS com permissões seguras para requisições de front-ends.
  - [x] Registrar os handlers globais de exceção RFC 9457.
  - [x] Incluir todos os routers no app sob o prefixo unificado `/api/v1`.

---

### Fase 6: Suíte Completa de Testes pytest
*Arquivos alvo:* `src/api/tests/`

- [x] **6.1. Infraestrutura e Fixtures de Testes Isolados (`src/api/tests/conftest.py`)**
  - [x] Configurar engine SQLite em memória isolada para a suíte de testes (`sqlite:///:memory:`).
  - [x] Implementar fixture de sessão de banco de teste com rollback automático ou reconstrução de tabelas a cada teste.
  - [x] Aplicar `app.dependency_overrides[get_db] = override_get_db`.
  - [x] Implementar fixtures para geração de tokens JWT:
    - `admin_token`: token assinado válido com role `"ADMIN"`.
    - `member_token`: token assinado válido com role `"MEMBER"`.
    - `admin_headers`: `{"Authorization": f"Bearer {admin_token}"}`.
    - `member_headers`: `{"Authorization": f"Bearer {member_token}"}`.
  - [x] Fixture `client` instanciando `TestClient(app)`.
- [x] **6.2. Testes de Autenticação e RBAC (`src/api/tests/test_auth.py`)**
  - [x] Teste de login com sucesso para usuário `ADMIN` (`200 OK` e retorno de JWT válido).
  - [x] Teste de login com sucesso para usuário `MEMBER` (`200 OK` e retorno de JWT válido).
  - [x] Teste de login com senha incorreta (deve retornar `401 Unauthorized` no formato `ApiError`).
  - [x] Teste de login com usuário inexistente (deve retornar `401 Unauthorized` no formato `ApiError`).
  - [x] Teste de `GET /api/v1/auth/me` com token válido (retorna dados do usuário logado).
  - [x] Teste de acesso a endpoints protegidos sem cabeçalho Authorization (esperado: `401 Unauthorized` RFC 9457).
  - [x] Teste de acesso a endpoints protegidos com token malformado ou expirado (esperado: `401 Unauthorized` RFC 9457).
  - [x] **Teste de RBAC Crítico:** Usuário `MEMBER` tentando executar `DELETE` (deve retornar `403 Forbidden` no formato `ApiError`).
  - [x] **Teste de RBAC Crítico:** Usuário `ADMIN` executando `DELETE` (deve ter sucesso com `204 No Content`).
- [x] **6.3. Testes de Conformidade RFC 9457 (`src/api/tests/test_errors.py`)**
  - [x] Testar formato de erro `400 Bad Request` validando schema `ApiError` (`type`, `title`, `status`, `detail`, `instance`).
  - [x] Testar formato de erro `401 Unauthorized` validando URI `https://api.character-build.dev/errors/unauthorized`.
  - [x] Testar formato de erro `403 Forbidden` validando URI `https://api.character-build.dev/errors/forbidden`.
  - [x] Testar formato de erro `404 Not Found` validando URI `https://api.character-build.dev/errors/not-found`.
  - [x] Testar formato de erro `422 Unprocessable Entity` ao enviar body inválido, validando lista `invalidParams` (`name`, `reason`).
  - [x] Garantir ausência total de respostas contendo a chave genérica `{"detail": "..."}` nas falhas tratadas.
- [x] **6.4. Testes de Contrato e Persistência das Entidades de Domínio**
  - [x] `test_characters.py`: criação de personagem com UUID, validação de chaves estrangeiras, listagem sem N+1, atualização parcial `PATCH`, atualização completa `PUT`, deleção por admin.
  - [x] `test_abilities.py`: relacionamento entre personagem e habilidades mágicas/físicas.
  - [x] `test_armors.py` e `test_weapons.py`: integridade referencial com partes do corpo, raridades e magias.
  - [x] `test_monsters.py`: persistência com UUID e vínculo de raça.
  - [x] Testes das coleções de referência (`test_genders.py`, `test_races.py`, `test_jobs.py`, `test_elements.py`, `test_rarities.py`, `test_body_parts.py`, `test_status_effects.py`, `test_magics.py`).
- [x] **6.5. Homologação da Suíte Completa**
  - [x] Executar `pytest -v` no terminal e assegurar 100% de taxa de aprovação de todos os testes unitários e de integração.

---

### Fase 7: Conteinerização (Docker), Orquestração (Kubernetes com 5 Réplicas & Docker Compose) e Gerenciador de Instâncias/Threads
*Arquivos alvo:* `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `nginx/nginx.conf`, `k8s/*`, `src/api/requirements.txt`, `src/api/main.py`, `src/api/database.py`

- [x] **7.1. Dependências do Ambiente de Produção (`src/api/requirements.txt`)**
  - [x] Declarar `psutil>=6.0.0` para inspeção e telemetria de processos, métricas de memória (RSS/VMS), CPU e rastreamento de threads por container.
  - [x] Declarar `gunicorn>=23.0.0` para gerenciamento robusto de processos/workers Uvicorn em containers de produção.
- [x] **7.2. Especificação do Dockerfile Otimizado e `.dockerignore`**
  - [x] Criar `.dockerignore` excluindo `.venv`, `__pycache__`, `.pytest_cache`, `tests`, `*.db`, `.git`, `.env` e logs.
  - [x] Criar `Dockerfile` multi-estágio ou enxuto baseado na imagem oficial `python:3.12-slim`:
    - Definir variáveis de ambiente padrão: `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`, `PORT=8000`.
    - Criar usuário e grupo sem privilégios de root (`appuser:appgroup` / UID 10001) para conformidade com padrões de segurança em Pods Kubernetes (`securityContext.runAsNonRoot: true`).
    - Instalar dependências a partir de `src/api/requirements.txt` com flag `--no-cache-dir`.
    - Criar diretório de dados persistentes `/app/data` com propriedade concedida a `appuser`.
    - Expor a porta `8000`.
    - Definir `HEALTHCHECK` Docker chamando script de health check em `http://localhost:8000/health`.
    - Configurar `ENTRYPOINT` executando Uvicorn gerenciando workers/threads via variáveis de ambiente (`WORKERS=1`, `THREADS=4`).
- [x] **7.3. Adaptação do Código da Aplicação para Containers e Gerenciamento Multi-instância**
  - [x] **Adaptação em `src/api/main.py`:**
    - Identificação de Ambiente e Instância:
      - Extrair identificador único da instância a partir de variáveis de ambiente (`INSTANCE_ID`, `POD_NAME`, `HOSTNAME`, ou fallback para UUID gerado no startup).
      - Extrair metadados de execução: Process ID (`os.getpid()`), contagem de threads (`threading.active_count()`), lista de threads ativas (`threading.enumerate()`), uso de memória e CPU via `psutil`.
    - Middleware de Identificação de Tráfego (`InstanceIdentifierMiddleware`):
      - Adicionar headers de resposta HTTP `X-Instance-ID: <instance_id>` e `X-Instance-PID: <pid>` em todas as respostas HTTP para auditoria e rastreamento de balanceamento de carga entre os 5 containers.
    - Endpoints de Saúde e Introspecção de Instâncias/Threads:
      - `GET /health`: Retorno estruturado para probes do Kubernetes e Docker (`status`, `instanceId`, `environment`).
      - `GET /api/v1/cluster/status`: Retorno detalhado para o gerenciador de instâncias:
        - `instanceId`: str (ID do container ou Pod).
        - `podName`: str | None (nome do Pod K8s via Downward API).
        - `podIp`: str | None (IP do Pod K8s).
        - `nodeName`: str | None (Nó K8s alocado).
        - `pid`: int.
        - `activeThreads`: int.
        - `threadNames`: list[str].
        - `memoryRssMb`: float.
        - `cpuPercent`: float.
        - `uptimeSeconds`: float.
  - [x] **Adaptação em `src/api/database.py`:**
    - Garantir compatibilidade do SQLite em volumes compartilhados entre múltiplas instâncias:
      - Respeitar variável de ambiente `DATABASE_URL` (ex.: `sqlite:////app/data/character-build.db`).
      - Ativar `connect_args={"check_same_thread": False, "timeout": 30.0}` para evitar timeouts imediatos em escritas concorrentes.
      - Executar `PRAGMA journal_mode=WAL;` e `PRAGMA busy_timeout=30000;` na inicialização da conexão para habilitar concorrência leitor-escritor eficiente.
- [x] **7.4. Orquestração com Docker Compose e Rede de 5 Instâncias (`docker-compose.yml`)**
  - [x] Criar rede bridge dedicada `character-net` para comunicação interna isolada.
  - [x] Criar volume nomeado persistente `character_data` montado em `/app/data` para reter os dados do SQLite.
  - [x] Configurar serviço `api`:
    - Build apontando para o `Dockerfile` raiz.
    - Modo escalonado: `deploy.replicas: 5` (gerando 5 instâncias isoladas do container).
    - Variáveis de ambiente configurando `DATABASE_URL=sqlite:////app/data/character-build.db`, `ENVIRONMENT=docker-compose`, `JWT_SECRET=supersecretjwtkey...`.
  - [x] Configurar serviço de Load Balancer / Reverse Proxy (`gateway` via `nginx:alpine`):
    - Mapear porta externa `8000:80`.
    - Arquivo de configuração `nginx/nginx.conf` distribuindo as requisições em round-robin balanceado para os 5 contêineres do serviço `api` na rede interna `character-net`.
- [x] **7.5. Manifestos Kubernetes para 5 Instâncias em Cluster (`k8s/`)**
  - [x] Criar diretório `k8s/` na raiz do projeto.
  - [x] `k8s/namespace.yaml`: Definição do namespace isolado `character-build`.
  - [x] `k8s/configmap.yaml`: ConfigMap contendo configurações não sensíveis (`ENVIRONMENT: kubernetes`, `DATABASE_URL: sqlite:////app/data/character-build.db`, `PORT: "8000"`).
  - [x] `k8s/secret.yaml`: Secret contendo chaves sensíveis (`JWT_SECRET` codificado em Base64).
  - [x] `k8s/pvc.yaml`: PersistentVolumeClaim com storage class local para compartilhamento e retenção de estado do SQLite em `/app/data`.
  - [x] `k8s/deployment.yaml`:
    - `replicas: 5` (especificação explícita de 5 réplicas/Pods simultâneos).
    - `securityContext`: `runAsNonRoot: true`, `runAsUser: 10001`.
    - Injeção de metadados do Kubernetes via Downward API:
      - `POD_NAME` mapeado de `metadata.name`.
      - `POD_IP` mapeado de `status.podIP`.
      - `NODE_NAME` mapeado de `spec.nodeName`.
      - `INSTANCE_ID` mapeado de `metadata.name`.
    - Configuração de Probes:
      - `readinessProbe`: `httpGet` em `/health`, porta 8000, `initialDelaySeconds: 5`, `periodSeconds: 5`.
      - `livenessProbe`: `httpGet` em `/health`, porta 8000, `initialDelaySeconds: 10`, `periodSeconds: 10`.
    - Definição de limites de recursos:
      - `resources.requests`: CPU 100m, Memória 128Mi.
      - `resources.limits`: CPU 500m, Memória 512Mi.
  - [x] `k8s/service.yaml`:
    - `Service` do tipo `NodePort` (ou `LoadBalancer`) apontando para porta 8000 dos Pods com seletor `app: character-build-api`, distribuindo a carga entre as 5 réplicas ativas.
- [x] **7.6. Homologação e Guia de Execução Local**
  - [x] Validar inicialização das 5 instâncias via Docker Compose e demonstrar balanceamento com script de requisições sequenciais.
  - [x] Validar deployment das 5 réplicas no Kubernetes local (Minikube ou Kind) e comprovar distribuição de chamadas entre os 5 Pods distintos.

---

### Fase 8: Estratégia Gitflow (`.gitflow`) e Pipeline de CI/CD Estruturado (GitHub Actions -> AWS)
*Arquivos alvo:* `.gitflow`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/workflows/ci.yml`, `.github/workflows/cd-staging.yml`, `.github/workflows/cd-production.yml`

> **Escopo de Prontidão:** Os pipelines serão arquitetados de forma completa, modular e aderente às boas práticas de nuvem (OIDC, Amazon ECR e Amazon EKS/5 réplicas), utilizando `secrets` e `vars` parametrizados no GitHub para ativação imediata assim que a conta e os recursos da AWS forem provisionados.

- [x] **8.1. Configuração e Convenção Gitflow (`.gitflow` e Governança de Branches)**
  - [x] Criar o arquivo `.gitflow` na raiz do projeto formalizando a topologia de branches e prefixos padrão do repositório:
    - `main`: branch de produção (código estável e versionado com tags `vX.Y.Z`).
    - `develop`: branch de integração contínua (ambiente de staging/homologação).
    - `feature/*`: desenvolvimento de novas funcionalidades a partir de `develop` (merge via Pull Request de volta para `develop`).
    - `release/*`: preparação de nova versão a partir de `develop` (ajustes finais, bump de versão e merge para `main` e `develop`).
    - `hotfix/*`: correções emergenciais em produção a partir de `main` (merge obrigatório em `main` e `develop`).
    - `bugfix/*` e `support/*`: suporte complementar opcional.
    - Prefixo de tags de versão: `v` (SemVer `vMAJOR.MINOR.PATCH`).
  - [x] Criar `.github/PULL_REQUEST_TEMPLATE.md` contendo checklist SDD obrigatório:
    - Tipo de mudança (`feature`, `bugfix`, `release`, `hotfix`).
    - Checklist de qualidade (`PLAN.md` atualizado, conformidade RFC 9457, cobertura `pytest` 100%, sem segredos commitados).
  - [x] Documentar regras recomendadas de *Branch Protection* no GitHub para `main` e `develop` (exigir status check do CI verde, bloquear *force push*, exigir revisão de PR).
- [x] **8.2. Pipeline de Integração Contínua — CI (`.github/workflows/ci.yml`)**
  - [x] Configurar gatilhos (`on`) para `push` e `pull_request` nas branches `main`, `develop`, `feature/**`, `release/**` e `hotfix/**`, com controle de concorrência (`concurrency` + `cancel-in-progress: true`).
  - [x] **Job 1 (`quality-and-lint`):**
    - `actions/checkout@v4` e `actions/setup-python@v5` (Python `3.12`) com cache de dependências `pip`.
    - Validação de sintaxe Python (`python -m compileall src/`), checagem de estilo/lint (ex.: `ruff check src/` opcional/configurável) e validação estrutural dos YAML do Kubernetes (`k8s/`).
  - [x] **Job 2 (`unit-and-contract-tests`):**
    - Instalação das dependências de `src/api/requirements.txt`.
    - Execução completa da suíte `pytest -v` cobrindo Auth JWT (`200`/`401`), RBAC (`403`/`204`), RFC 9457 (`400`/`404`/`422`), ORM SQLAlchemy 2.0 e introspecção de cluster (`/health`, `/api/v1/cluster/status`).
  - [x] **Job 3 (`docker-build-validation` — depende de `quality-and-lint` e `unit-and-contract-tests`):**
    - Setup do Docker Buildx (`docker/setup-buildx-action@v3`).
    - Build de validação da imagem a partir do `Dockerfile` (`push: false`) garantindo que mudanças de código ou dependências não quebrem o empacotamento em container.
- [x] **8.3. Pipeline de Entrega Contínua — CD Staging / AWS (`.github/workflows/cd-staging.yml`)**
  - [x] Configurar gatilhos (`on`) para `push` na branch `develop` e disparo manual (`workflow_dispatch`).
  - [x] Configurar `permissions: { id-token: write, contents: read }` para suportar autenticação sem chaves fixas na AWS via **GitHub OIDC**.
  - [x] Associar ao ambiente `environment: staging` no GitHub Actions.
  - [x] **Etapas do Pipeline Staging -> AWS:**
    - Reexecução de gate de testes (`pytest -q`) antes de publicar artefatos.
    - Autenticação na AWS via `aws-actions/configure-aws-credentials@v4` (`role-to-assume: ${{ secrets.AWS_ROLE_ARN_STAGING }}`, `aws-region: ${{ vars.AWS_REGION }}`).
    - Login no **Amazon ECR** (`aws-actions/amazon-ecr-login@v2`).
    - Build e Push da imagem Docker para o ECR com tags `staging-${GITHUB_SHA::7}` e `staging-latest`.
    - Atualização do `kubeconfig` do **Amazon EKS** (`aws eks update-kubeconfig --name ${{ vars.EKS_CLUSTER_STAGING }}`).
    - Aplicação dos manifestos `k8s/` e atualização da imagem no `Deployment` (`kubectl set image`), seguida de verificação `kubectl rollout status --timeout=180s`.
- [x] **8.4. Pipeline de Entrega Contínua — CD Produção / AWS (`.github/workflows/cd-production.yml`)**
  - [x] Configurar gatilhos (`on`) para `push` na branch `main`, criação de tags semânticas `v*.*.*` e `workflow_dispatch`.
  - [x] Associar ao ambiente `environment: production` (preparado para exigir aprovação manual de *Required Reviewers* no GitHub).
  - [x] Configurar `permissions: { id-token: write, contents: read, security-events: write }`.
  - [x] **Etapas do Pipeline Produção -> AWS:**
    - **Gate de Testes e Segurança:** Execução da suíte `pytest` + scan de vulnerabilidades na imagem Docker com Trivy (`aquasecurity/trivy-action`, configurado de forma clara e extensível).
    - **Autenticação AWS (OIDC) e Login no Amazon ECR:** Isolado com role dedicada de produção (`${{ secrets.AWS_ROLE_ARN_PROD }}`).
    - **Build & Push de Artefato Imutável:** Publicação no ECR com tags `${VERSION_TAG}` (tag Git ou SHA curto) e `latest`.
    - **Deploy RollingUpdate no Amazon EKS (5 Réplicas):**
      - Aplicação de `k8s/namespace.yaml`, `k8s/configmap.yaml`, `k8s/pvc.yaml`, `k8s/deployment.yaml` e `k8s/service.yaml`.
      - Injeção segura do `JWT_SECRET` a partir do GitHub Secret (ou integração futura com AWS Secrets Manager / External Secrets Operator).
      - Atualização da imagem do `character-build-deployment` preservando as **5 réplicas** sem downtime (`kubectl set image` + `kubectl rollout status`).
    - **Rollback Automático em Falha (`if: failure()`):**
      - Execução de `kubectl rollout undo deployment/character-build-deployment -n ${{ vars.K8S_NAMESPACE }}` garantindo restauração automática da versão anterior estável.
- [x] **8.5. Mapeamento de Variáveis, Secrets e Pré-requisitos AWS para Ativação Futura**
  - [x] Documentar no `PLAN.md` (e em comentários claros nos YAMLs) todas as `Secrets` e `Variables` exigidas no GitHub:
    - **Secrets:** `AWS_ROLE_ARN_STAGING`, `AWS_ROLE_ARN_PROD`, `JWT_SECRET_STAGING`, `JWT_SECRET_PROD`.
    - **Variables:** `AWS_REGION` (ex.: `sa-east-1` ou `us-east-1`), `ECR_REPOSITORY` (`character-build-api`), `EKS_CLUSTER_STAGING`, `EKS_CLUSTER_PROD`, `K8S_NAMESPACE` (`character-build`).
  - [x] Documentar os recursos mínimos a provisionar futuramente na AWS:
    - Repositório **Amazon ECR** (`character-build-api`).
    - Cluster **Amazon EKS** (ou adaptação alternativa para **Amazon ECS Fargate**).
    - Provedor OIDC (`token.actions.githubusercontent.com`) e IAM Roles com permissões mínimas (Least Privilege) para ECR e EKS.
- [x] **8.6. Validação dos Arquivos de Workflow e Integridade do Projeto**
  - [x] Validar sintaxe YAML de `.github/workflows/ci.yml`, `cd-staging.yml` e `cd-production.yml` via parser Python/YAML.
  - [x] Confirmar que o arquivo `.gitflow` e o template de PR estão bem formatados.
  - [x] Reexecutar `pytest -q` garantindo que os 48 testes permanecem 100% aprovados.

---

## Guia de Comandos para Execução Local

### Opção A: Execução Local com Docker Compose (5 Instâncias + Balanceador Nginx)

1. **Construir as imagens e subir as 5 réplicas em segundo plano:**
   ```bash
   docker compose up --build -d
   ```

2. **Verificar os 5 contêineres da API e o balanceador em execução:**
   ```bash
   docker compose ps
   ```

3. **Verificar os logs distribuídos dos contêineres:**
   ```bash
   docker compose logs -f api
   ```

4. **Testar o balanceamento e inspecionar a identificação das instâncias e threads (executar múltiplas vezes para observar a rotação de `X-Instance-ID` e `instanceId`):**
   ```bash
   # Teste do endpoint de saúde com header de instância
   curl -i http://localhost:8000/health

   # Teste do gerenciador de instâncias e threads
   curl -s http://localhost:8000/api/v1/cluster/status | jq .
   ```

5. **Parar e remover os contêineres e volumes:**
   ```bash
   docker compose down -v
   ```

---

### Opção B: Execução Local com Kubernetes (Minikube ou Kind com 5 Pods)

#### Com Minikube:
1. **Iniciar o cluster local:**
   ```bash
   minikube start
   ```

2. **Construir a imagem Docker e carregá-la no Minikube:**
   ```bash
   docker build -t character-build-api:v2 .
   minikube image load character-build-api:v2
   ```

3. **Aplicar todos os manifestos do Kubernetes:**
   ```bash
   kubectl apply -f k8s/
   ```

4. **Acompanhar a criação das 5 réplicas dos Pods:**
   ```bash
   kubectl get pods -n character-build -w
   ```

5. **Expor o Service para acesso local na máquina host:**
   ```bash
   kubectl port-forward -n character-build svc/character-build-service 8000:8000
   ```

6. **Efetuar requisições demonstrando o balanceamento entre os 5 Pods distintos:**
   ```bash
   # Enviar 10 requisições sequenciais para demonstrar o balanceamento entre os 5 Pods
   for i in {1..10}; do
     curl -s http://localhost:8000/api/v1/cluster/status | jq -r '.podName, .instanceId'
     sleep 0.5
   done
   ```

7. **Limpar os recursos do Kubernetes:**
   ```bash
   kubectl delete -f k8s/
   ```

---

### Opção C: Fluxo Gitflow e Ativação Futura do CI/CD (GitHub Actions -> AWS)

#### Fluxo Diário com Gitflow:
```bash
# 1. Inicializar o repositório com as convenções do .gitflow (caso ainda não iniciado)
git checkout -b develop

# 2. Criar uma nova funcionalidade a partir de develop
git checkout -b feature/minha-feature develop
# ... commits ...
git push -u origin feature/minha-feature
# Abrir Pull Request para develop -> dispara automaticamente o CI (.github/workflows/ci.yml)

# 3. Merge em develop -> dispara o CD de Staging (.github/workflows/cd-staging.yml)

# 4. Preparar uma release e promover para produção
git checkout -b release/v2.1.0 develop
# Abrir Pull Request para main -> após aprovação e tag v2.1.0, dispara o CD de Produção (.github/workflows/cd-production.yml)
```

#### Checklist de Ativação Futura na AWS (GitHub Settings -> Secrets and variables -> Actions):
- **Secrets:**
  - `AWS_ROLE_ARN_STAGING`: ARN da IAM Role AWS OIDC para homologação.
  - `AWS_ROLE_ARN_PROD`: ARN da IAM Role AWS OIDC para produção.
  - `JWT_SECRET_STAGING` / `JWT_SECRET_PROD`: Segredos JWT por ambiente.
- **Variables:**
  - `AWS_REGION`: ex. `sa-east-1` ou `us-east-1`.
  - `ECR_REPOSITORY`: `character-build-api`.
  - `EKS_CLUSTER_STAGING` / `EKS_CLUSTER_PROD`: nomes dos clusters Amazon EKS.
  - `K8S_NAMESPACE`: `character-build`.

---

## Próximos Passos (Transição de Persona)
1. **Revisão Humana:** O usuário deve revisar e aprovar o planejamento da **Fase 8** (Gitflow + CI/CD GitHub Actions -> AWS) em `PLAN.md`.
2. **Implementação Guiada:** Uma vez aprovado, invocar `[Backend Coder]` para criar `.gitflow`, `.github/PULL_REQUEST_TEMPLATE.md` e os workflows em `.github/workflows/`.
3. **Validação:** Validar a sintaxe dos arquivos YAML e manter a suíte `pytest` 100% aprovada.
