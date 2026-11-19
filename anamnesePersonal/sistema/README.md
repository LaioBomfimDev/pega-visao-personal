> Atualização: rankings removidos por completo da aplicação. Jornada e destaques opcionais no perfil permanecem. Rotas antigas não fornecem classificações nem permitem reativá-las. Validação atual: 56 execuções aprovadas.

# Abel Acompanhamento — primeira versão funcional

Sistema local para Abel e seus alunos, com dados persistentes e contas individuais.

## Abrir

Execute `iniciar.ps1` nesta pasta e acesse http://127.0.0.1:8766.
Se o Windows impedir a execução do script, abra um terminal nesta pasta e execute `.\.venv\Scripts\python.exe app.py`.
No primeiro acesso, crie a conta de Abel com seu nome, e-mail e senha de pelo menos 10 caracteres. Não há senha padrão.
Em **Alunos → Convidar aluno**, informe os dados e copie o convite. O sistema não envia e-mails; o convite é pessoal, de uso único e vale sete dias.

## O que funciona

- Contas de Abel e alunos, com modalidade on-line ou presencial.
- Feed de motivação do profissional, rankings opcionais e conversas privadas vinculadas às sessões.
- Treinos com exercícios, séries, repetições e descanso. O aluno registra carga, execução e observações a cada sessão; o histórico é preservado.
- Orientações individuais, confirmação de leitura, conclusão e solicitação de ajustes.
- Anamnese integrada, check-in semanal, medidas, fotos privadas e devolutivas de Abel.
- Agenda de sessões e biblioteca de conteúdos.
- Notificações internas, atualizadas a cada 30 segundos enquanto o sistema está aberto.
- Edição de título/observações e de horário/local de sessões, com versão anterior preservada no banco.
- Exportação JSON dos dados de perfil e registros do aluno (não inclui arquivos de mídia nem todo o histórico operacional).
- Alteração de senha e backup local.

Fotos e anamnese são privadas para aluno e Abel. Apenas publicações e conteúdos criados pelo professor podem ter público coletivo. As contas usadas nos testes ficam em uma base temporária separada.

## Dados e backup

A base SQLite, a chave de sessão e as imagens ficam em `%LOCALAPPDATA%\AbelAcompanhamento`, fora da pasta do site antigo. Não sirva essa pasta com um servidor de arquivos.

Para backup, pare o sistema e execute:

```powershell
.\.venv\Scripts\python.exe manage.py backup
```

O ZIP fica na subpasta `backups` dos dados. Guarde uma cópia em local protegido. Para restaurar, com o sistema parado, preserve a pasta atual e extraia o backup em uma pasta vazia; configure `ABEL_DATA_DIR` para essa pasta antes de iniciar. Não sobreponha arquivos de uma base em uso. O backup contém dados privados e a chave de sessão.

Se esquecer a senha, no computador onde o sistema roda:

```powershell
.\.venv\Scripts\python.exe manage.py reset-password seu@email.com
```

## Limites desta entrega

Esta execução é local, acessível neste computador. Para alunos acessarem de fora, falta configurar hospedagem, domínio e HTTPS. As notificações ainda não são push de celular. Vídeos, pagamentos, IA, integração com relógios, recuperação de senha por e-mail e backups automáticos são etapas futuras. A agenda registra sessões, sem bloqueio automático de conflitos. O editor permite alterar exercícios e dias da ficha, preservando versões e sessões anteriores.

## Validação

Execute `.\.venv\Scripts\python.exe test_app.py`. Os testes usam dados temporários: autenticação, autorização, CSRF, isolamento entre alunos, mídia, notificações e histórico de treinos. Os arquivos `test-ui.cjs` e `test-extra.cjs` registram os fluxos de navegador realizados com dados fictícios em servidor separado na porta 8767; requerem Playwright disponível e uma base de teste vazia para o primeiro teste. As imagens `test-desktop.png` e `test-mobile.png` são capturas de dados fictícios.

Dependências fixadas em `requirements.txt`. Tecnologia: Flask, Waitress, SQLite e Pillow, interface HTML/CSS/JavaScript. Os projetos pesquisados no GitHub serviram como referência de produto; nenhum código deles foi incorporado.

## Ajustes para celular

Interface adaptada para uso a partir de 320 px: cinco atalhos fixos com menu Mais, formulários em tela inteira, exercícios em cartões, campos com fonte de 16 px, áreas de toque maiores e textos longos com quebra de linha. O zoom do navegador continua disponível. A anamnese incorporada também foi ajustada.

Validação em navegador Edge/Chromium: 162 verificações de largura em 320, 360, 390, 430, 768, 1024 e 1440 px, nas visões de professor e aluno. Preenchimento completo da anamnese e upload em 320 px; registro de carga e foco em campos com emulação de toque em 390 px. Os testes de layout estão em `test-mobile.cjs`, `test-mobile-assessment.cjs` e `test-mobile-focus.cjs`, usam uma base temporária na porta 8768 e dados fictícios. São verificações de navegador, não testes em aparelhos físicos.


## Atualização de planejamento — 14/09/2026

A atualização de 15/09 acrescenta [Minha jornada](GUIA-JORNADA.md): marcos no perfil e até três destaques compartilháveis com a equipe, mediante escolha explícita, sem depender do ranking. O atalho principal agora é Jornada; rankings ficam em uma área opcional separada. Validação acumulada desta versão: 64 execuções aprovadas, incluindo `test_journey.py` e repetições herdadas.

Consulte [GUIA-PLANEJAMENTO.md](GUIA-PLANEJAMENTO.md) para usar fichas A/B/C, avaliações periódicas, gráficos, notas privadas e PDF/Word. As fichas antigas continuam disponíveis como um único dia até serem editadas.

Validação: 59 execuções aprovadas nas suítes test_app.py, test_planning.py, test_superadmin.py, test_privacy.py, test_profiles.py, test_coaching.py e test_engagement.py. Execute cada arquivo em um processo Python separado: cada suíte inicializa sua própria base temporária.
