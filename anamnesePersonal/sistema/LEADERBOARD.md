# Ranking, conquistas e compartilhamento

O aluno encontra **Ranking** diretamente na barra inferior. A página reúne o pódio, sua posição, lista da equipe, desafios, conquistas privadas e preferências de participação. O profissional continua responsável por ativar o ranking e definir os dias de treino; cada aluno autoriza a própria participação.

Há duas sequências distintas, identificadas na tela:

- **Seu ritmo:** dias consecutivos com treino registrado, calculados no horário de Brasília. O dia atual não encerra uma sequência iniciada ontem. Mostra os últimos sete dias, o recorde e o registro do dia. É privado.
- **Constância da equipe:** mantém a regra já autorizada do plano do profissional. Descansos planejados preservam a sequência. Empates recebem a mesma posição. O pódio só destaca participantes com pontuação positiva.

Conquistas são liberadas aos 1, 5, 10, 25 e 50 dias registrados, com progresso até a próxima. Registros múltiplos no mesmo dia contam uma vez. Sessões parciais também contam como presença, sem serem apresentadas como treinos completos. Não é necessário participar do ranking para usar as conquistas ou compartilhar um treino.

Em **Treinos → Ver detalhes → Sessões e conversas → Compartilhar meu treino**, o aluno revisa um cartão PNG de 1080 × 1350. Pode editar ou retirar o nome, atualizar a prévia, baixar a imagem ou abrir o compartilhamento nativo quando o navegador permitir. O cartão contém apenas nome escolhido, data, exercícios realizados/total e indicação de completo/parcial. Não inclui cargas, comentários, sensações, fotos privadas ou mensagens. Nenhum destino é escolhido automaticamente. Se o navegador não oferecer compartilhamento de arquivos, o download permanece disponível.

As imagens são geradas no navegador e não publicadas em servidor. A autorização da foto de perfil no ranking continua independente. A anamnese permanece intacta.

Validação: `test_engagement.py` cobre dias únicos, fuso, intervalo sem registro, recorde, datas futuras e isolamento. Também passaram as suítes de privacidade, perfil e acompanhamento e o fluxo no navegador com pódio, conquista, edição de prévia e download, em 320–1440 px. A folha nativa de compartilhamento depende do navegador/dispositivo e não foi acionada para enviar conteúdo real nos testes.
