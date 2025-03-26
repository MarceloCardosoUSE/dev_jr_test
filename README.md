## 🚀 Tecnologias
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [OpenWeatherMap API](https://openweathermap.org/api)

---

## 📋 Instruções de Uso

### 1️⃣ Instale os requisitos do projeto
```bash
pip install -r requirements.txt
```

### 2️⃣ Configure o ambiente
Crie um arquivo `.env` na raiz do projeto seguindo o modelo abaixo:
```env
DB_USERNAME=
DB_PASSWORD=
DB_PORT=
DB_NAME=
DB_HOST=
```

### 3️⃣ Execute o projeto
Inicie a aplicação em ambiente de desenvolvimento com:
```bash
fastapi dev main.py
```

A API estará disponível em `http://127.0.0.1:8000`.

---

## 📌 Considerações
- Os dados recebidos são previsões de até **5 dias** à frente, pois essa é a única opção disponível no plano gratuito da API.
- Foram escolhidos apenas os seguintes dados para retorno: **nome da cidade, temperatura, descrição e data**. A API retorna mais informações, mas essas foram selecionadas para otimizar a usabilidade.
- A rota `POST` possui uma verificação para impedir a **duplicidade de dados**.
- A rota `GET` foi consolidada para permitir consulta tanto com quanto sem parâmetros.
- Os **IDs** gerados para os dados são do tipo **UUID**, garantindo unicidade.
- O **appid** está na main para maior facilidade, mas, idealmente, em um ambiente de trabalho, deveria ser posto juntamente às outras variáveis de ambiente no `.env`