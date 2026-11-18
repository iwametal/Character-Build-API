***Integrantes da Equipe***
Felipe Mendonça da Cruz - RA: 2840482411044
Leonardo de Andrade Ferreira - RA: 2840482523035 
Felipe Delchiaro Malzoni - RA: 2840482421025

# Character Build API

## Sobre

A Character Build API é uma interface REST projetada para o gerenciamento completo de sistemas de RPG. A API resolve o problema de estruturar, validar e persistir informações sobre personagens, suas raças, vocações (classes), itens equipáveis (armas e armaduras), magias e efeitos de status.

Público-alvo: Jogadores e Mestres de RPG
 
## Principais Funcionalidades:
  Cadastro e customização de personagens com atributos dinâmicos calculados pela vocação e raça.
  Gerenciamento de inventário e equipamentos (Armor, Weapon).
  Catálogo de magias, elementos e efeitos de status.
  Validação de regras de negócio de criação e evolução de personagens.

**Arquitetura de Recursos e Relacionamentos**
A API foi estruturada de forma modular, desacoplando o personagem de seus atributos e itens:

**Character (Entidade Principal)**:Representa o personagem do jogador. Relaciona-se com: Race, Job, Armor, Weapon e Magic.
**Race & Job:** Definem a base de atributos iniciais (HP, ATK, DEF, Inteligência, Vigor).
**Armor & Weapon:** Representam os equipamentos. Cada item possui raridade e aplica modificadores (boosts) de atributos ao personagem.
Magic & Status-Effects: Definem o grimório de habilidades disponíveis e as condições aplicadas em combate.

## Dependências
**Rodando localmente**
- Python [>=3.12]
- - Pip
- - Pyenv (Ou outro ambiente de preferência)

**Caso deseje subir um container ou cluster**
- Docker
- Docker-Compose
- Kubernets [kubectl, minikube e kind (Ou outro cluster de preferência)]

## Funcionamento

### Subindo em um ambiente virtual (pyenv)

Crie um novo ambiente virtual
```
python -m venv .venv
```

Ative o ambiente
```
source .venv/bin/activate
```

Rode o projeto
```
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

### Subindo um novo cluster

Crie um novo cluster kube
```
kind create cluster
```

Verifique os nodes criados e o contexto
```
kubectl get nodes && echo "=" && kubectl config current-context
```

Inicie o minikube
```
minikube start
```

Build a nova imagem do projeto
```
docker build -t character-build-api:v2 .
minikube image load character-build-api:v2
```

Carregue a imagem no kind
```
kind load docker-image character-build-api:v2
```

Aplique os manifestos no kube
```
kubectl apply -f k8s/
```

Exporte a porta da máquina para as instâncias
```
kubectl port-forward -n character-build svc/character-build-service 8000:8000
```


## Testes

health check
```
curl -i http://localhost:8000/health
```

Inspecionar detalhes de threads, memória e status da instância atual
```
curl -s http://localhost:8000/api/v1/cluster/status | jq .
```

