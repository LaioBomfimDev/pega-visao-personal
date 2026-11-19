# Projeto de anamnese — Abel Bomfim

Documento inicial para desenvolvermos o projeto juntos.

## Pasta de trabalho

A partir desta etapa, os arquivos deste projeto serão acessados em `C:/Users/m/Downloads/AbelPersonal/anamnesePersonal/`.

## O que já existe

Há duas versões da página, ambas com quatro etapas: identificação, objetivos, histórico de treinamento e saúde.

| Critério | index.html + style.css + script.js | anamnese.html |
| --- | --- | --- |
| Apresentação | Tema escuro, interface compacta e navegação fixa na parte inferior | Banner de academia, apresentação da consultoria e cartões claros |
| Organização | Estrutura, estilos e comportamento em arquivos separados | HTML, CSS e JavaScript reunidos no mesmo arquivo |
| Conteúdo | Textos mais curtos e menos alternativas em algumas perguntas | Introdução mais explicativa e alternativas adicionais de objetivos e condições |
| Exportação Word | Resumo parcial; deixa de fora informações coletadas | Exportação mais completa, incluindo contato, rotina, medicamentos e liberação médica |
| Envio por e-mail | EmailJS com valores de exemplo | EmailJS com valores de exemplo |
| Direção sugerida | Base para a evolução do projeto | Referência para conteúdo e relatório |

Recomendação inicial: evoluir o index.html e aproveitar a apresentação e a exportação completa do anamnese.html. A separação dos arquivos facilita ajustes futuros. A preferência visual ainda pode ser discutida; esta recomendação se baseia na leitura do código, sem teste visual ou de envio no navegador.

## Apresentação do projeto — primeiro rascunho

O projeto de anamnese digital de Abel Bomfim é a porta de entrada para um acompanhamento de treino personalizado, tanto na consultoria on-line quanto no atendimento presencial. Sua proposta é conhecer a pessoa antes de organizar o treinamento: entender seus objetivos, sua experiência, sua rotina e as limitações que ela relata.

O aluno preenche um formulário dividido em etapas, com perguntas claras e uma indicação de progresso. Ao concluir, suas respostas devem chegar ao profissional em um relatório organizado, facilitando a análise inicial e a identificação de informações que precisam ser esclarecidas em uma conversa.

A experiência deve ser simples no celular e acolhedora na linguagem. Cada pergunta precisa ter uma finalidade clara, e o aluno deve saber o que acontece depois de enviar suas respostas. O formulário organiza as informações; o planejamento do treino continua dependendo da avaliação do profissional.

## Texto proposto para a abertura da página

### Seu treino começa com a sua história

Seja na consultoria on-line ou no atendimento presencial, seu treino começa com uma conversa sobre você. Quero conhecer seus objetivos, sua rotina, sua experiência e os cuidados que precisam ser considerados no acompanhamento.

Preencha as próximas etapas com atenção. Suas respostas vão me ajudar a entender seu momento e preparar um planejamento alinhado às suas necessidades e à sua disponibilidade.

Ao finalizar, você poderá revisar suas respostas antes de enviá-las.

Observação de implementação: a revisão antes do envio é uma funcionalidade proposta e ainda precisa ser criada. O texto correspondente deve entrar na página junto com essa função.

## Como desenvolver o formulário

1. **Sobre você:** dados de identificação, contato e modalidade de atendimento (consultoria on-line ou presencial), com instruções coerentes — nome completo e nome pelo qual prefere ser chamado não são a mesma informação.
2. **Seus objetivos:** resultados que deseja alcançar, prioridade principal, dificuldades e eventual prazo.
3. **Seu treino e sua rotina:** experiência anterior, frequência atual, dias disponíveis, duração possível de cada sessão, local de treino e equipamentos disponíveis.
4. **Saúde e observações:** informações relatadas pelo aluno, com campos de detalhamento exibidos quando a resposta exigir.
5. **Revisão e envio:** resumo das respostas e possibilidade de corrigir informações antes de concluir.

Modalidade de atendimento, dias disponíveis, duração das sessões, local, equipamentos e revisão final são propostas de ampliação; ainda não existem como campos ou etapa próprios nas páginas atuais.

## Modalidades de atendimento

Decisão confirmada: o projeto atenderá consultoria on-line e atendimento presencial.

A proposta é manter uma anamnese comum para os dois formatos, identificando a modalidade logo no início. Assim, Abel recebe fichas com a mesma organização, e cada aluno responde a perguntas adicionais pertinentes ao seu atendimento.

| Modalidade | Informações adicionais propostas | Finalidade |
| --- | --- | --- |
| Consultoria on-line | Cidade e fuso horário quando necessário, local onde treina, equipamentos disponíveis e disponibilidade para contato | Ajudar a planejar o treino e organizar a comunicação a distância |
| Atendimento presencial | Local pretendido para as sessões e disponibilidade de dias e horários | Apoiar a organização do atendimento e a conversa inicial |

Nos dois formatos, o relatório deverá identificar a modalidade escolhida e reunir todas as respostas. Após o envio confirmado, a página deve explicar o próximo passo correspondente ao serviço. Prazos, canais de acompanhamento e agendamento ainda serão definidos com Abel; preencher o formulário não deverá ser apresentado como confirmação automática de horário.

Esses campos e comportamentos estão documentados como proposta e ainda não foram implementados nas páginas.

## Pendências observadas no código

- Configurar e verificar a entrega real do e-mail. As duas versões usam identificadores de exemplo do EmailJS.
- Separar a confirmação de envio da confirmação de download. Hoje, o modo sem configuração pode gerar um Word e depois exibir uma mensagem que sugere recebimento das informações.
- Completar o Word do index.html com todos os dados coletados, usando a versão anamnese.html como referência.
- Tratar falhas no carregamento das bibliotecas externas e na geração do Word, permitindo nova tentativa sem perder as respostas.
- Revisar validações: presença de um valor numérico não garante valor válido; as respostas de saúde não têm validação específica de etapa.
- Evitar respostas contraditórias, como selecionar “Nenhuma” junto com uma condição de saúde.
- Permitir ampliação da página no celular; o index.html atualmente restringe o zoom no viewport.
- Definir quem recebe as respostas, onde elas ficam armazenadas e como explicar esse uso ao aluno antes de publicar a versão final.

## Decisões para nossa próxima conversa

- A identidade visual deve seguir o tema escuro do index.html ou os cartões claros do anamnese.html?
- Como Abel quer receber e organizar cada ficha: e-mail, documento ou uma área de gestão?
- O prazo de sete dias corridos, presente nas duas páginas, corresponde ao serviço oferecido e a partir de qual momento começa a contar?

## Primeira entrega sugerida

Uma versão única com apresentação revisada, formulário adaptado à rotina do aluno, revisão das respostas, relatório completo e confirmação fiel ao resultado do envio. Recursos como cadastro, painel de alunos e acompanhamento de evolução podem ser definidos depois, conforme a necessidade do atendimento.


## Implementação — 10/09/2026

O index.html agora é a versão principal com cinco etapas, escolha de modalidade, perguntas condicionais de rotina, revisão com edição por seção e exportação completa em Word. Campos ocultos da outra modalidade não entram no relatório. O formulário permite zoom e navegação por teclado.

O envio automático ainda depende da configuração do EmailJS no script.js. Enquanto isso, a conclusão oferece download e informa que nenhuma resposta foi enviada. O template de e-mail deverá incluir a variável `{{relatorio}}`, que contém a ficha completa, incluindo os novos campos. Não foi realizado envio real.

A biblioteca docx 8.2.3 está em vendor, com sua licença. Se ela não carregar, há exportação alternativa em texto. A versão anamnese.html continua como referência histórica.

Verificado em navegador Edge, com tela de 390 × 844: preenchimento, modalidade on-line, mudança para presencial, edição do nome, exclusividade de “Nenhuma”, revisão, ausência de rolagem horizontal e download. O conteúdo do arquivo Word foi conferido para garantir que inclui as correções e exclui as respostas da modalidade desativada.

As seções anteriores descrevem a proposta inicial; este registro atualiza o status das funcionalidades implementadas. Permanecem pendentes a configuração do envio, as definições de uso e armazenamento dos dados e os prazos e canais do atendimento.

## Implementação — setembro de 2026

A primeira versão funcional está em `sistema/`, com servidor próprio na porta 8766, contas reais, SQLite e armazenamento privado de imagens. O formulário original continua disponível separadamente. Veja `sistema/README.md` para abrir, criar a primeira conta, fazer backup e consultar os limites atuais. A proposta completa permanece como roteiro de evolução; recursos previstos nela não devem ser confundidos com funcionalidades já implementadas.
