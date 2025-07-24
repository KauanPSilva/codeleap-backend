# 📝 CodeLeap Backend

Repositório do back-end para a aplicação de rede social integrada com a API pública da CodeLeap.  
Desenvolvido com Django e Django REST Framework, este projeto oferece autenticação via JWT, gerenciamento de posts, comentários, likes e sistema de menções de usuário com `@`.

---

## 🚀 Tecnologias

- Python 3.11+
- Django 5.2+
- Django REST Framework
- SimpleJWT
- Requests

---

## 🛠️ Instalação e execução

```bash
# Clone o repositório
git clone https://github.com/KauanPSilva/codeleap-backend.git
cd codeleap-backend

# Crie o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Aplique as migrações
python manage.py migrate

# Rode o servidor
python manage.py runserver

```

🔐 Autenticação
Utiliza JWT (via djangorestframework-simplejwt).

POST /api/token/
Autentica o usuário e retorna o par access/refresh.

Exemplo de body:

```
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```
POST /api/token/refresh/
Gera novo access token a partir de um refresh válido.

Exemplo de body:
```
{
  "refresh": "<seu_refresh_token>"
}
```

📌 Endpoints da API
Todos os endpoints exigem token JWT no header:
```
Authorization: Bearer <access_token>
```
🔹 GET /api/posts/
Lista posts da API pública da CodeLeap, com filtros e ordenação.

Query params:

Parâmetros:

username:	Filtra posts de um usuário
title:	Filtra posts por título
ordering:	Ordenação por data (created, -created)

🔹 POST /api/posts/
Cria um novo post na API externa.

Body:

```
{
  "username": "seu_usuario",
  "title": "Título do post",
  "content": "Conteúdo do post"
}
```
🔹 PUT /api/posts/<int:post_id>/
Atualiza título e conteúdo de um post.

Body:
```
{
  "title": "Novo título",
  "content": "Novo conteúdo"
}
```
🔹 DELETE /api/posts/<int:post_id>/
Deleta um post.

🔹 POST /api/posts/<int:post_id>/like/
Adiciona um like ao post (armazenado localmente).

🔹 GET /api/posts/<int:post_id>/comments/
Retorna todos os comentários locais do post.

🔹 POST /api/posts/<int:post_id>/comments/
Cria um comentário no post.

Body:
```
{
  "content": "Comentário do usuário"
}
```
🔹 GET /api/mentions/
Retorna todos os posts e comentários locais que mencionam o usuário autenticado com @username.

Exemplo de resposta:
```
{
  "posts": [
    {
      "id": 12,
      "username": "ana",
      "title": "Olá @kauan",
      "content": "Veja isso @kauan",
      "created": "2025-07-24T14:00:00Z",
      "likes": 3
    }
  ],
  "comments": [
    {
      "id": 8,
      "post_id": 12,
      "content": "Muito bom @kauan"
    }
  ]
}
```
📁 Estrutura do Projeto
codeleap-backend/
│
├── codeleap_backend/         # Configurações principais do projeto Django
│   ├── settings.py           # Configurações do projeto
│   ├── urls.py               # URLs globais do projeto
│   ├── asgi.py / wsgi.py     # Configurações para servidores ASGI/WSGI
│
├── posts/                    # Aplicação principal com lógica de posts
│   ├── admin.py              # Registro dos modelos no admin
│   ├── apps.py               # Configuração do app 'posts'
│   ├── models.py             # Modelos: Post, Comentário, Like, Mention
│   ├── serializers.py        # Serializadores para API REST
│   ├── urls.py               # Rotas específicas do app
│   ├── utils.py              # Funções auxiliares reutilizáveis
│   ├── views.py              # Regras de negócio e manipulação de requests
│   └── tests.py              # Testes automatizados do app
│
├── db.sqlite3                # Banco de dados SQLite local
├── manage.py                 # Script de gerenciamento do Django
└── requirements.txt          # Dependências do projeto

🧪 Testes
Para rodar os testes unitários basta rodar no terminal: "python manage.py test"

💬 Contato
Para dúvidas ou sugestões:
LinkedIn: www.linkedin.com/in/kauan-silva-9328a1251
Email: kauanpsilva66@gmail.com
whatsapp: (24)992247844
