# Administração central

Entre com a conta profissional existente e abra **Minha conta → Criar SUPERADM**. Informe a senha atual para confirmar sua identidade e cadastre nome, e-mail separado e senha da administração central. A criação inicial funciona neste computador e é encerrada após existir um SUPERADM. A conta profissional e seus alunos são preservados.

No painel central, crie um convite de profissional e compartilhe o link individual. O convite vale sete dias. Ao cadastrar a senha, o profissional fica pendente. Use **Aprovar acesso** para liberá-lo. Cada profissional convida e acompanha sua própria equipe; publicações, registros, imagens, exportações e notificações ficam separados por profissional.

**Bloquear acesso** invalida as sessões do profissional e dos alunos de sua equipe. Reativar exige novo login. O SUPERADM gerencia contas e totais; não recebe acesso aos registros pessoais dos alunos.

**Redefinir senha** gera um link de uso único válido por 30 minutos. Um novo link invalida o anterior. A troca invalida as sessões antigas e não altera o estado de aprovação/bloqueio. Nenhuma mensagem é enviada automaticamente. As ações de suporte ficam registradas no histórico.

O sistema permanece local em http://127.0.0.1:8766. Links externos dependem de publicação com HTTPS. Não há credenciais padrão para o SUPERADM.

Validação: test_app.py (15 testes), test_superadmin.py (fluxo entre duas equipes, aprovação, bloqueio, sessões e redefinição), test-super-ui.cjs (painel em 360 e 1440 pixels com dados simulados).
