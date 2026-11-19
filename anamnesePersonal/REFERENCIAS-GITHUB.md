# Referências de código aberto — sistema Abel Bomfim

Consulta: 10/09/2026. Pesquisa em repositórios, documentação e arquivos selecionados; os projetos não foram instalados nem submetidos a auditoria de segurança. Nenhum código foi incorporado à aplicação.

## Seleção

| Projeto | Referência útil | Limite para nosso caso |
| --- | --- | --- |
| [wger](https://github.com/wger-project/wger) | Rotinas, progressão, medidas, galeria de evolução e gestão básica multiusuário | Ainda precisamos desenhar a comunidade e o fluxo de orientações de Abel |
| [Workout.cool](https://github.com/Snouzy/workout-cool) | Catálogo de exercícios, instruções, demonstrações e registro de sessões | O modelo consultado não oferece, por si só, a relação completa personal–aluno que queremos |
| [FitTrackee](https://github.com/SamR1/FitTrackee) | Atividades sociais, curtidas, visibilidade, notificações e moderação | Foco em atividades ao ar livre; a parte social serve como referência para a nossa comunidade |
| [Endurain](https://github.com/endurain-project/endurain) | Feed, perfis, histórico, metas, estatísticas e integrações | Foco em registro de atividades; não substitui nossa gestão de consultoria |
| [Novu](https://github.com/novuhq/novu) | Central de notificações, preferências, regras e agrupamento | É infraestrutura de comunicação, não um sistema de alunos |

## Evidências que refinam a proposta

No [schema do Workout.cool](https://github.com/Snouzy/workout-cool/blob/main/prisma/schema.prisma), o registro de treino separa sessão, exercícios e séries. Há programas por semanas e sessões, favoritos e estado de conclusão. Isso é uma boa referência para distinguir treino prescrito de treino realizado. O papel de usuário contém admin e user; ProgramCoach armazena nome e imagem de apresentação. Esse arquivo não demonstra um vínculo de autorização entre treinador e carteira de alunos. Não tratar o termo “coaching” do README como garantia desse fluxo pronto.

A [documentação de interações do FitTrackee](https://docs.fittrackee.org/en/features/interactions.html) descreve solicitações para seguir, curtidas, controles de visibilidade, bloqueio, moderação e notificações lidas/não lidas. Para Abel, aproveitar as ideias de visibilidade e reações, mantendo comunicação por tarefas. O projeto principal passou para Codeberg; o GitHub é um espelho, conforme seu [README](https://github.com/SamR1/FitTrackee).

O [Endurain](https://docs.endurain.com/) documenta perfis de administrador/usuário, feeds, estatísticas semanais e mensais, metas, notificações e integrações com Strava/Garmin. Referência para o resumo da evolução. A documentação aponta o desenvolvimento no Codeberg; considerar isso ao acompanhar versões.

## Ajustes propostos para nosso produto

1. Feed com filtro entre comunicados de Abel, conquistas compartilhadas e conteúdos salvos.
2. Notificações com lida/não lida; conclusão de tarefa é um estado separado.
3. Cartões de atividade que abrem o treino, a orientação ou a avaliação correspondente.
4. Programas organizados por fases, com comparação entre prescrito e realizado.
5. Histórico por exercício: última carga registrada, séries e instruções anteriores.
6. Resumo semanal visual e calendário de registros.
7. Audiência explícita em cada publicação; anamnese e evolução privada ficam fora do feed por padrão.
8. Biblioteca própria de exercícios, com vídeos de Abel e referências de equipamento/grupo muscular.

Esses ajustes são propostas para o sistema, não confirmação de funcionalidades já implementadas.

## Licenças verificadas

- Workout.cool: [MIT](https://github.com/Snouzy/workout-cool/blob/main/LICENSE).
- wger: AGPL-3.0-or-later para o código; dados de exercícios/ingredientes têm licença Creative Commons por entrada, conforme o [README](https://github.com/wger-project/wger#license).
- Endurain e FitTrackee: AGPL-3.0 identificada nos repositórios; conferir texto e versão de cada componente antes de incorporar.
- Novu: núcleo MIT e partes comerciais. Consultar [LICENSE-MIT](https://github.com/novuhq/novu/blob/next/LICENSE-MIT), [licença Enterprise](https://github.com/novuhq/novu/blob/next/LICENSE-ENTERPRISE) e [licença de pacotes EE](https://github.com/novuhq/novu/blob/next/EE-PACKAGES-LICENSE). Não presumir que todos os recursos do serviço hospedado estão disponíveis no núcleo aberto.

A escolha de reutilizar código exige verificar o arquivo exato, suas dependências e a licença dos materiais incluídos. Nenhuma biblioteca de vídeos foi aprovada para importação nesta pesquisa.

## Sinais de manutenção

Consulta à API pública do GitHub: nenhum dos cinco repositórios estava marcado como arquivado. Datas de última movimentação (`pushed_at`), que podem incluir branches e não equivalem à última versão estável:

- Workout.cool: 31/07/2026.
- wger: 06/09/2026.
- Endurain: 09/09/2026.
- FitTrackee: 09/09/2026.
- Novu: 10/09/2026.

Esses dados indicam movimentação, não estabilidade ou qualidade comprovada.

## Recomendação

Usar wger e Workout.cool como referências para treino e registro; FitTrackee e Endurain para comunidade e evolução; estudar Novu como opção para notificações. Desenvolver a experiência específica de Abel com relação personal–aluno, permissões de arquivos, anamnese, check-ins e orientações sem chat. Antes de escolher uma base para adaptação, comparar o esforço de alterar um desses projetos com implementar somente os módulos necessários.
