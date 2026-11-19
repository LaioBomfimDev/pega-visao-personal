# Acompanhamento de sessões

O profissional acessa **Treinos → Como sua equipe está treinando**, ou usa **Ver acompanhamento** na tela inicial. Pode filtrar por aluno, registros aguardando resposta, todos os registros, parciais e relatos de desconforto.

Cada sessão mostra aluno, treino, data, quantidade de exercícios realizados, sensação opcional e comentário. “Completo” exige todos os exercícios marcados naquela sessão. Os demais registros são parciais. Ausência de registro não é apresentada como falta. A contagem de registros nos últimos sete dias inclui sessões parciais; não equivale a dias únicos nem a um diagnóstico de frequência.

O aluno marca os exercícios que realizou, informa cargas, pode selecionar como se sentiu e envia um comentário. Ao abrir o treino novamente, os exercícios começam desmarcados; as cargas anteriores permanecem como referência. Cada envio gera uma sessão independente e preserva as anteriores.

**Responder com atenção** abre a conversa daquela sessão, com exercícios e cargas em uma seção expansível. Sugestões de início de mensagem apenas preenchem o campo vazio. O profissional personaliza e clica em **Enviar mensagem**. O aluno recebe uma notificação interna e pode responder em **Treino → Sessões e conversas**. Nova mensagem do aluno devolve a conversa à fila do profissional. Não há envio por WhatsApp, e-mail ou resposta automática.

As conversas são privadas entre o aluno daquela sessão e seu profissional. O servidor verifica a equipe e o dono da sessão em cada envio. Mensagens, sensações e comentários não são adicionados ao ranking. Os registros antigos continuam acessíveis, mesmo sem sensação informada.

Validação: testes de sessões parciais, feedback, histórico independente, conversa em ambos os sentidos, isolamento entre alunos/equipes e CSRF em `test_coaching.py`; regressões de sistema, privacidade e perfis; fluxo completo no navegador e layouts de 320, 390, 768 e 1440 px.
