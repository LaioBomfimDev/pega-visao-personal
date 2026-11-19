# Proposta de sistema de acompanhamento — Abel Bomfim

Pesquisa realizada em 10/09/2026. Documento de produto: funcionalidades propostas, ainda não implementadas. A versão atual continua sendo o formulário de anamnese local.

## Direção

Criar uma comunidade privada de alunos, com um painel de gestão para Abel e uma área simples para cada aluno acompanhar seu treino, suas orientações e sua evolução. Atender consultoria on-line e presencial. Comunicação por publicações, notificações e respostas vinculadas a atividades, sem caixa de chat ou mensagens diretas.

A anamnese existente passa a integrar a entrada do aluno, com histórico de atualizações. Seu envio cria uma pendência para análise do profissional; não publica automaticamente informações pessoais na comunidade.

## Referências e aprendizados

- [ABC Trainerize — recursos](https://www.trainerize.com/features/): combina programas, hábitos, grupos, desafios e conquistas. Aprendizado: a camada social pode conviver com o acompanhamento individual.
- [Trainerize — configurações de grupos](https://help.trainerize.com/hc/en-us/articles/115004510883-About-Group-Settings): permite controlar quem publica e as notificações. Aprendizado: oferecer grupos em que apenas o profissional publica.
- [Everfit — tarefas com arquivos](https://help.everfit.io/en/articles/2951524-assign-tasks-send-pdfs-check-in-forms-videos-zoom-workouts-livestream-links): tarefas aceitam mídias, documentos e links, com lembretes. Aprendizado: transformar uma instrução em atividade verificável.
- [Everfit — notificações de fórum](https://help.everfit.io/en/articles/9775713-customize-forum-notifications): possui preferências e agrupamento de notificações. Aprendizado: avisar conforme relevância e evitar repetição.
- [Everfit — comparação de formulários](https://help.everfit.io/en/articles/14120947-how-to-compare-form-responses): compara respostas de períodos diferentes. Aprendizado: o check-in semanal deve permitir comparação com semanas anteriores.
- [Everfit — anúncios](https://help.everfit.io/en/articles/3661723-autoflow-announcements): permite programar anúncios com texto e mídia. Aprendizado: separar orientações destacadas das publicações comuns.
- [TrueCoach — gestão de clientes](https://help.truecoach.co/en/articles/2403919-managing-your-clients): filtros de adesão, programação e modalidade. Aprendizado: o painel precisa ajudar Abel a priorizar o trabalho.
- [Hevy Coach — progresso](https://hevycoach.com/features/client-tracker/): histórico por exercício, medidas e fotos. Aprendizado: evolução inclui desempenho e constância, além de aparência.
- [MFIT — funcionalidades](https://blog.mfitpersonal.com.br/5-funcionalidades-do-app-da-mfit-que-talvez-voce-nao-conheca/4/): progresso com fotos, agenda e acompanhamento financeiro. Aprendizado: contemplar a operação cotidiana do personal.
- [Tecnofit — experiência do aluno](https://ajuda.tecnofit.com.br/pt-BR/support/solutions/articles/67000401576-sou-aluno-e-quero-me-cadastrar-no-app-tecnofit-box-como-faco-): reúne resultados, timeline e comunicados. Aprendizado: a comunidade pode fazer parte da jornada de treino.
- [Strava — privacidade de atividades](https://support.strava.com/en-us/articles/15401987-activity-privacy-controls): visibilidade por atividade. Aprendizado: cada publicação deve ter audiência explícita.

As fontes descrevem recursos dos fornecedores. Não foram feitos testes pagos, avaliação de eficácia ou comparação de todos os planos. As funcionalidades abaixo são propostas para Abel; não são alegações de exclusividade no mercado.

## Área do aluno

1. **Hoje:** treino previsto, orientações pendentes, próxima sessão e botão para registrar como foi o dia. Mostrar poucas ações prioritárias.
2. **Treinos:** exercícios com demonstração, séries, repetições, intervalo e instruções de Abel; registro de carga, execução e dificuldade. Alterações preservam o histórico do que foi prescrito e realizado.
3. **Comunidade:** feed cronológico com publicações de Abel, avisos fixados, imagens, vídeos, enquetes e conquistas voluntariamente compartilhadas. Reações e botão salvar. Publicações de alunos podem passar por aprovação. Comentários livres ficam fora da proposta inicial para preservar o uso sem chat.
4. **Minha evolução:** linha do tempo privada, fotos por data, comparação lado a lado, medidas opcionais, evolução de carga, frequência e metas pessoais.
5. **Check-in semanal:** formulário curto sobre realização dos treinos, dificuldade, disposição, limitações relatadas e disponibilidade para a próxima semana.
6. **Biblioteca:** orientações pesquisáveis por exercício ou assunto, vídeos próprios de Abel e materiais salvos.
7. **Agenda:** sessões presenciais, solicitações de remarcação, avaliações e datas de revisão da consultoria. Uma solicitação só se torna confirmada após a regra de agenda ou aprovação de Abel.
8. **Perfil:** modalidade, objetivos, anamnese, preferências de notificação e visibilidade das publicações.

## Painel de Abel

- Lista de alunos com filtros por modalidade, turma, situação e pendências.
- Ficha individual com anamnese, treinos, fotos, registros, avaliações e notas privadas do profissional.
- Caixa de tarefas: novas anamneses, vídeos aguardando avaliação, check-ins recebidos e planos que precisam de revisão.
- Editor de treino com modelos reutilizáveis, personalização e registro de alterações.
- Publicador para aluno específico, grupo ou toda a comunidade, com prévia da audiência antes de publicar.
- Programação de orientações, prazo, anexos e confirmação de leitura quando necessária.
- Visão de agenda e presença para o presencial.
- Relatório periódico compartilhável com o aluno.
- Em etapa posterior: planos contratados, vencimentos, controle de pagamento e integração com cobrança.

## Comunicação sem chat

Cada orientação pode pedir uma resposta específica: “Li”, “Concluí”, “Enviar foto”, “Enviar vídeo” ou “Solicitar revisão”. O aluno também pode registrar uma dificuldade vinculada a um exercício ou check-in. Abel recebe uma tarefa e publica uma devolutiva vinculada ao mesmo registro. Não há conversa livre nem sequência de mensagens instantâneas.

Exemplo: Abel solicita um vídeo de um exercício; o aluno recebe a notificação, abre a tarefa e envia o vídeo; Abel avalia e adiciona uma orientação; o aluno recebe o aviso da devolutiva e confirma a leitura.

## Notificações

| Evento | Destinatário | Ação |
| --- | --- | --- |
| Treino publicado ou alterado | Aluno | Abrir treino e ver o que mudou |
| Orientação individual | Aluno | Ler e responder à ação solicitada |
| Check-in com prazo | Aluno | Preencher formulário |
| Foto ou vídeo enviado | Abel | Abrir fila de avaliação |
| Ausência de registros no período configurado | Abel | Verificar contexto antes de abordar o aluno |
| Sessão confirmada ou alterada | Aluno | Conferir agenda |
| Reações da comunidade | Aluno, se habilitado | Resumo agrupado |

O registro interno de notificações será a referência consultável. Push depende de permissão e condições do dispositivo; não prometer entrega instantânea ou equiparar envio a leitura. Preferências por categoria, horário de silêncio, limite de lembretes e cancelamento de lembrete após conclusão. Texto na tela bloqueada deve ser genérico, sem detalhes de saúde ou fotos pessoais.

## Diferenciais propostos

- **Painel de atenção com motivo:** mostrar “sem registros há sete dias” ou “relatou dificuldade em dois treinos”. Esses sinais geram uma revisão humana; ausência de registro não comprova ausência de treino.
- **Resumo da semana:** comparar planejamento e registros, reunir conquistas e perguntas pendentes. Se usarmos IA, ela prepara um rascunho baseado nos dados registrados para Abel revisar.
- **Orientação junto do exercício:** foto, trecho de vídeo e observação aparecem quando o aluno abre aquele exercício novamente.
- **Plano adaptado à disponibilidade:** aluno informa viagem ou pouco tempo; Abel escolhe e libera uma alternativa previamente preparada.
- **Conquistas pessoais:** reconhecer consistência e metas pactuadas, sem ranking de corpos, peso ou dor. Descanso planejado e pausas não apagam conquistas.
- **História do acompanhamento:** combinar início, revisões, metas e resultados em um resumo visual. Compartilhamento externo requer escolha específica do aluno.

## Visibilidade e operação

Anamnese, relatos de saúde, fotos de avaliação e documentos ficam restritos ao aluno e ao profissional autorizado. Publicar uma conquista na comunidade é uma ação separada e voluntária. Alunos não acessam fichas de colegas. A autorização deve ser aplicada no servidor também para cada arquivo, e não apenas escondendo botões na tela.

Prever recuperação de acesso, cópias de segurança, exclusão/exportação de dados, limites de upload e moderação de conteúdo da comunidade. Definir regras de retenção e acesso antes da utilização com alunos reais.

## Ordem de construção

**Etapa 1 — acompanhamento funcional:** login e convites, perfis Abel/aluno, anamnese integrada, Hoje, treino e registros básicos, orientações com fotos, check-in, evolução privada, notificações internas e feed de comunicados com reações. Incluir armazenamento real, controle de acesso e backup.

**Etapa 2 — experiência completa:** agenda presencial, biblioteca, vídeos de execução com devolutiva, push, tarefas recorrentes, comparação de períodos, publicações voluntárias dos alunos com moderação e relatórios.

**Etapa 3 — expansão:** desafios, automações avançadas, resumo assistido por IA, cobrança integrada e integrações com dispositivos, conforme uso e necessidade comprovados.

Critérios para validar a primeira etapa: aluno acessa somente seus dados privados; orientação chega ao destinatário correto; conclusão atualiza a fila de Abel; registros persistem entre dispositivos; compartilhamento social respeita a audiência; falhas de rede permitem tentar novamente sem duplicar publicações.

## Formato e impacto técnico

Proposta: começar por uma aplicação web adaptada ao celular, instalável na tela inicial, com painel de gestão no computador. A documentação da [Apple sobre Web Push](https://developer.apple.com/documentation/usernotifications/sending-web-push-notifications-in-web-apps-and-browsers?language=objc) descreve notificações para web apps na tela inicial do iOS 16.4 ou posterior; o [WebKit](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/) explica a necessidade de permissão solicitada por uma ação do usuário.

O HTML local existente é uma etapa da entrada do aluno. Para o sistema funcionar entre pessoas e dispositivos, precisamos de autenticação, banco de dados, armazenamento privado de mídia, servidor para regras e notificações e hospedagem HTTPS. Persistência apenas no navegador não atende esse objetivo. Escolha de serviços, custos e integrações será feita na fase de implementação, após definir o tamanho inicial da turma e o volume de mídia.
