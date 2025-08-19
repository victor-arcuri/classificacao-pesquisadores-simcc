# Sistema de Classificação de Pesquisquisadores do Projeto Simcc
Essa atividade tem como objetivo o desenvolvimento de um sistema de classificação de pesquisadores a partir de tags, permitindo um melhor sistema de busca para a plataforma Simcc. Para tanto, utilizaremos uma LLM que criará as tags e classificará os pesquisadores. 

## Informações ℹ️

### Data de entrega 📆
O projeto não possui uma data de entrega definida, possuindo como limite um período de 3 semanas. Para fins de organização, a data **09/09** será utilizada como deadline.

### Objetivos 🎯
As atividades serão explicitadas no Trello *(inserir link)*, permitindo maior organização. A seguir, uma generalização das atividades a serem desenvolvidas:
- Criação de um sistema de scrapping de dados dos pesquisadores do banco de dados, currículo lattes e outras fontes
- Criação de um banco de tags otimizado que englobe uma grande variade, sem repetição
- Classificação dos pesquisadores a partir do banco de tags criado
- Criação de uma API simples para acessar o banco e extrair alguns dados
- Criação de um front-end para permitir a busca de pesquisadores por suas tags.

## Como Contribuir 🚀
Nesse projeto, adotaremos o padrão Gitflow para manutenção de repositório remoto e trabalho assíncrono, e utilizaremos a metodologia Kanban de desenvilvimento ágil a partir da ferramenta Trello. Para contribuir, antes é necessário um bom conhcimento sobre essas práticas e ferramentas. 

### Clonando o Repositório
O primeiro passo para contribuir é clonar o repositório remoto em um ambiente de desenvolvimento local. 
```
git clone https://github.com/victor-arcuri/classificacao-pesquisadores-simcc.git
cd classificacao-pesquisadores-simcc
```
Com o repositório clonado, mude para a branch de desenvolvimento (develop):
```
git checkout develop
```
Com o repositório clonado, adicione as variáveis de ambiente necessárias.

### Adicionando uma Feature
Quando for adicionar uma feature nova, é necessário primeiro olhar o Trello e reparar se ninguém já está trabalhando nisso. Se estiver livre, adicione o card referente a feature, se não existir, e aloque-a para a área de desenvolvimento. Com isso, é hora de criar a branch.
```
git checkout develop
git pull
git checkout -b feature/<nome-da-feature>
```
> [!WARNING]
> Não esqueça de mudar para develop e fazer o pull das mudanças antes de criar qualquer branch nova!

Com a branch criada, é só começar a trabalhar na feature, fazendo commits até terminar. Com tudo finalizado, basta dar o git push.

> [!TIP]
> O padrão de nome de branches e commits será explicado abaixo

Com a branch no repositório remoto, crie um Pull Request, tomando cuidado para definir o alvo do Merge como a branch de desenvolvimento develop. Lembrando que, para que sua feature entre em develop, primeiro outro dev precisa aceitar o pedido, então não esqueça de solicitar revisão de todos da equipe! Também é importante sempre ler os PRs dos outros da equipe e revisar! Os PRs da develop pra main só podem ser liberados para merge quando todos da equipe aprovarem. 

> [!WARNING]
> Lembre de não adicionar nenhuma informação sensível ao código diretamente (chaves de API, conexões com banco, etc), deixe sempre em arquivos .env!

### Alguns links para aprender mais
#### Gitflow
- [Artigo sobre padrão de nomeação de branches e boas práticas](https://gist.github.com/paulo-raoni/1a8f52138f67fd40379f454ee61aa4ce)
- [Artigo sobre padrão de nomeação de commits](https://github.com/iuricode/padroes-de-commits)
#### Kanban
- [Artigo explicando mais sobre Kanban](https://www.totvs.com/blog/negocios/kanban/)

