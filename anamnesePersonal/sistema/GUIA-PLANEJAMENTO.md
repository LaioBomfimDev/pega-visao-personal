# Planejamento e acompanhamento

Mantivemos a base atual e adaptamos as ideias do projeto antigo à autenticação, aos alunos e ao histórico existentes. Nenhum banco remoto foi importado.

## Fichas de treino

Em **Treinos → Criar treino**, escolha o aluno e organize dias A/B/C. Cada dia possui nome, dias da semana opcionais e exercícios com séries, repetições, descanso e observações. É possível duplicar dias e adicionar ou remover exercícios. Limites: 8 dias, 40 exercícios por dia e 160 por ficha.

Em **Ver detalhes**, o profissional pode editar, duplicar a ficha ou consultar versões anteriores. Desmarcar “Ficha ativa” arquiva o planejamento e impede novas sessões. Uma edição concorrente é recusada: feche e reabra o editor para carregar a versão mais recente.

O aluno escolhe o dia, marca os exercícios realizados, informa cargas e envia. Esforço de 1 a 10, humor e relato de dor são opcionais. Cada envio cria uma sessão, inclusive quando o mesmo treino se repete. As novas sessões guardam a versão e os exercícios usados naquele momento. Sessões antigas conservam os dados que já possuíam; informações nunca registradas não são reconstruídas.

Os dias da ficha são uma previsão do planejamento. Eles não alteram automaticamente a agenda ou as metas do ranking.

Em **Mostrar planejamento**, escolha fichas ativas, arquivadas ou todas. Fichas arquivadas ficam fora da contagem de treinos disponíveis e das próximas ações do aluno. As sessões e conversas anteriores continuam acessíveis.

O preenchimento de uma sessão é mantido separadamente por dia enquanto esta página permanece aberta, inclusive ao fechar e reabrir a ficha. Enviar a sessão limpa somente o rascunho daquele dia. Recarregar a página ou sair da conta descarta os rascunhos. Eles não são gravados no armazenamento do navegador e não passam para uma nova versão da ficha.

## Avaliações e evolução

Em **Evolução**, use Avaliação periódica, Rotina e bem-estar ou Hábitos alimentares. O profissional seleciona o aluno; o aluno registra para si. Preencha somente o que foi observado, com a data da avaliação. Novos registros podem ser feitos no mesmo mês ou dia, sem substituir os anteriores.

Escolha um indicador para ver as medidas e abra “Ver valores e datas” para os números completos. No painel profissional, selecione primeiro um aluno. Os pontos têm espaçamento por registro, não proporcional ao intervalo de tempo.

A anamnese original, os check-ins e as fotos continuam disponíveis. Os três novos formulários são complementares à anamnese; não reproduzem integralmente os questionários antigos.

## Notas do profissional

Em **Alunos → aluno → Notas privadas**, adicione ou edite observações internas. Somente o profissional responsável acessa essas notas pela aplicação. Alterações preservam a versão anterior no banco. As notas não aparecem ao aluno, nos relatórios PDF/Word ou em sua exportação JSON. O backup local inclui as notas.

## PDF e Word

Abra um treino, anamnese, avaliação ou check-in e use **Baixar PDF** ou **Baixar Word**. O documento reúne o conteúdo do registro; não inclui fotos anexadas, conversas das sessões ou notas internas. Os links exigem login e as mesmas permissões do registro.

## Execução e validação

O sistema principal usa http://127.0.0.1:8766 e, por padrão, os dados em `%LOCALAPPDATA%\AbelAcompanhamento`. Inicie com `.\.venv\Scripts\python.exe app.py` na pasta sistema. Em novas instalações, instale `requirements.txt`.

A demonstração em http://127.0.0.1:8765 usa dados fictícios e banco separado. Suas credenciais estão no README da pasta comparison-preview do workspace da análise.

Antes da atualização foram salvos um ZIP do código no workspace e o backup `abel-20260914-155743.zip` na pasta de backups do banco principal. Não houve publicação na internet.

Validação: 59 execuções de testes aprovadas, incluindo casos herdados pela suíte de privacidade. Cada arquivo de teste deve ser executado em um processo separado. Percurso no navegador: criação e duplicação de dia A/B, avaliação com gráfico, nota privada, registro do treino B com esforço/humor e edição para versão 2 mantendo a sessão da versão 1. Largura conferida na evolução em 390 px e na ficha em 320 px; sem teste em aparelho físico. PDF e Word de ficha e avaliação tiveram conteúdo extraído e verificado.
