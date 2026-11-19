# Minha jornada

Os marcos pessoais ficam em **Meu perfil → Minha jornada** e no atalho **Jornada**. A coleção mostra apenas os marcos já alcançados, com linguagem de cuidado e participação. Não há posições, raridades, conquistas bloqueadas ou cobrança por uma próxima conquista.

O primeiro treino registrado, cinco e dez dias com registros, um mês de acompanhamento com pelo menos um treino e a retomada dos registros após um intervalo são os marcos iniciais. Várias sessões no mesmo dia contam uma vez; sessões parciais contam. O cálculo usa o dia em Brasília. Uma pausa não remove os marcos anteriores. A retomada descreve um intervalo nos registros, sem presumir ausência de treino.

## Compartilhar com a equipe

Em **Escolher meus destaques**, selecione até três marcos. A opção de compartilhar começa desligada. É preciso marcar explicitamente a autorização para mostrar nome do perfil, foto, bio e os marcos selecionados aos alunos e ao profissional da mesma equipe. A prévia do nome, foto e bio aparece antes de salvar. Sem nome de perfil, o nome exibido é “Participante”, preservando o nome cadastral.

Os perfis autorizados aparecem em **Jornada → Histórias da equipe**, em ordem alfabética. Não há pontuação, posição, curtidas ou contagem pública de treinos. Peso, cargas, dor, medidas, anamnese, conversas e e-mail não fazem parte dessa resposta pública da equipe.

**Deixar jornada privada** retira o perfil dessa área e bloqueia as URLs de perfil e foto da jornada para novas consultas. A coleção pessoal e os destaques selecionados permanecem. Conteúdo já visto ou salvo por outra pessoa não pode ser recolhido.

Esse compartilhamento exige autenticação; não é um perfil aberto na internet. Cada equipe acessa apenas seus participantes ativos. Uma pessoa não precisa participar do ranking nem compartilhar sua própria jornada para ver os perfis que colegas autorizaram.

## Compartilhamento do perfil

Os rankings foram removidos do sistema, incluindo participação, pódios, pontuações e acesso por rotas antigas. A única área de compartilhamento de conquistas é Minha jornada, com escolha explícita dos destaques.

Editar nome, foto ou bio no Meu perfil atualiza esses dados na jornada quando o aluno autorizou compartilhá-la. Os formulários informam essa condição. As autorizações antigas de ranking não autorizam a jornada e não permitem acesso aos antigos perfis compartilhados.

## Validação de 15/09/2026

64 execuções de testes aprovadas, incluindo repetições herdadas pela suíte de privacidade. O novo `test_journey.py` cobre privacidade inicial, autorização explícita, limite e seleção de marcos, isolamento de equipes, bloqueio de usuários, revogação de acesso a fotos e perfis, datas, pausas e contagem por dia. Execute cada arquivo de testes em um processo separado.

No navegador, foi validado com conta fictícia: abrir a coleção no perfil, escolher um destaque, autorizar a equipe, abrir o perfil compartilhado e desligar o compartilhamento. Nenhuma conta real foi inscrita automaticamente.


Após a remoção: 56 execuções de testes passaram. Os testes antigos de funcionamento dos rankings foram substituídos por verificações de retirada, incluindo uma base com autorizações antigas ativas. A jornada, fotos privadas, sessões e avaliações continuam cobertas.
