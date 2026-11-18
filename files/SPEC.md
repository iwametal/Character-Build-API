# SPEC.md — Especificação de Negócio, ORM e Autenticação (TaskFlow API v2)

## 1. Visão Geral e Fonte da Verdade do Contrato
Este projeto implementa o **Character Build API**, uma API RESTful para criação e utilização de personagens em um mundo de RPG, com **persistência relacional via ORM (SQLAlchemy 2.0)** e **controle de acesso Stateless via JWT e RBAC**.
O contrato base de rotas, parâmetros e JSON Schemas das entidades de domínio está definido em `@[character_build.openapi.json](character_build.openapi.json)`.

---

## 2. Prioridade Arquitetural: Extração de Tipos (Schema-First)
O sistema DEVE extrair e consolidar todas as tipagens estáticas (modelos Pydantic v2 em `src/api/schemas.py`) a partir dos `Data Schemas` do Apidog e dos requisitos de Autenticação **antes** de implementar os modelos ORM ou rotas HTTP:

1. **Enums de Domínio e Segurança:**
   - `UserRole`: `"ADMIN"`, `"MEMBER"`
2. **Modelos de Autenticação e Usuário (Aula 08):**
   - `LoginRequestDTO`: `email` (str formato email), `password` (str, min 6 caracteres).
   - `UserResponse`: `id` (UUID str), `name` (str), `email` (str), `role` (`UserRole`).
   - `TokenResponseDTO`: `accessToken` (str JWT), `tokenType` (str, default `"bearer"`), `expiresIn` (int, em segundos), `user` (`UserResponse`).
3. **Modelos de Tarefa (Apidog):**
   - Revisar o character_build.openapi.json para detalhes
4. **Modelos de Projeto (Apidog):**
   - Revisar o character_build.openapi.json para detalhes
5. **Modelos de Erro (RFC 9457):**
   - `InvalidParam`: `name` (str), `reason` (str).
   - `ApiError`: `type` (URI str), `title` (str), `status` (int), `detail` (str), `instance` (str), `invalidParams` (lista opcional de `InvalidParam`).

---

## 3. Mapeamento Objeto-Relacional — ORM (Aula 09)
A camada de persistência (`src/api/models.py` e `src/api/database.py`) deve utilizar **SQLAlchemy 2.0 (`Mapped`, `mapped_column`, `relationship`)** sobre SQLite:

---

## 4. Autenticação JWT, Autorização RBAC e Regras dos Endpoints (Aula 08)

### 4.1. Coleção `Auth` (`/api/v1/auth`)
- **`POST /api/v1/auth/login`**:
  - Recebe `LoginRequestDTO` (`email` e `password`).
  - Se as credenciais forem válidas, retorna `200 OK` com `TokenResponseDTO` contendo o JWT assinado (`HS256`, validade de 3600s) com as claims `sub`, `email` e `role`.
  - Se o e-mail não existir ou a senha estiver incorreta, retorna `401 Unauthorized` no formato `ApiError` (RFC 9457, `type: "https://api.character-build.dev/errors/unauthorized"`).
- **`GET /api/v1/auth/me`**:
  - Requer cabeçalho `Authorization: Bearer <token>`.
  - Retorna `200 OK` com `UserResponse` do usuário autenticado ou `401 Unauthorized` (RFC 9457).

### 4.2. Matriz de Controle de Acesso (RBAC) nas Rotas de Domínio
| Endpoint | Permissão Exigida | Comportamento de Segurança |
| :--- | :--- | :--- |
| `Rotas GET` | Público (ou Token opcional) | Permite leitura sem bloqueio para facilitar testes de contrato do Apidog. |
| `Rotas de POST, PATCH e PUT` | Autenticado (`MEMBER` ou `ADMIN`) | Retorna `401 Unauthorized` (RFC 9457) se o token JWT estiver ausente, inválido ou expirado. |
| **`Rotas de DELETE`** | **Exclusivo `ADMIN`** | Retorna `401 Unauthorized` se sem token, e **`403 Forbidden` (RFC 9457)** caso o usuário autenticado possua role `MEMBER`. |

### 4.3. Comportamento Funcional das rotas
- **`Rotas de GET`**: Paginação no banco via ORM (`offset`/`limit`), filtros por `status`, `priority` e busca case-insensitive (`ILIKE` / `lower()`) em `title` e `description`.
- **`Rotas de POST`**: Persiste no SQLite via SQLAlchemy, retorna `201 Created` e define o cabeçalho `Location: /api/v1/characters/{id}`. Se `id` for informado e não existir no banco, retorna `404 Not Found` (RFC 9457).
- **`Rotas de PUT e PATCH`**: Atualiza parcialmente no banco e renova `updatedAt`.
- **`Rotas de DELETE`**: Restrito a `ADMIN`. Remove do banco e retorna `204 No Content`.
- **`Rotas de GET`**: Usa `selectinload(Characters.tasks)` para buscar o projeto e retornar `{ "data": List[Object] }` (ou `404` se o projeto não existir).

### 4.4. Seed Inicial do Banco de Dados e Expectations
A função de `seed` executada na inicialização do banco deve garantir a criação idempotente de:
1. **Usuários para Teste de Auth/RBAC:**
   - **Admin:** `email: "admin@fatec.sp.gov.br"`, `password: "Admin@2026"`, `role: "ADMIN"`
   - **Member:** `email: "aluno@fatec.sp.gov.br"`, `password: "Aluno@2026"`, `role: "MEMBER"`
2. **Tabelas das rotas referenciadas na spec character_build.openapi.json:**
