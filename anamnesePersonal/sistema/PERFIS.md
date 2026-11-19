# Perfis e foto opcional no ranking

Abra **Mais → Meu perfil** ou toque no avatar do cabeçalho. O usuário pode definir nome de exibição (40 caracteres), bio (160 caracteres), adicionar/trocar foto e removê-la. A foto também aparece no seu próprio cabeçalho e menu lateral.

O perfil começa privado. Em **Editar perfil**, a opção de mostrar foto, nome e bio à equipe começa desmarcada. Compartilhar o perfil não inscreve o usuário em rankings: é necessário também autorizar a participação em um ranking ativo. Sem a autorização do perfil, o ranking mantém apenas apelido e pontuação. Com autorização, a foto acompanha o apelido e o botão abre o perfil escolhido pelo participante.

O acesso ao perfil e à imagem é conferido no servidor em cada requisição: autenticação, equipe, conta ativa, ranking habilitado, participação e autorização do perfil. Nenhum e-mail, nome cadastral, medida ou registro de saúde é incluído na resposta compartilhada. **Deixar perfil privado** revoga o acesso inclusive por URLs anteriores; **Retirar todas as autorizações** também desativa o compartilhamento. Imagens já vistas não podem ser apagadas da memória de quem as viu.

Fotos JPG, PNG e WebP de até 5 MB e 20 megapixels são recortadas pelo centro para 512 × 512 e convertidas em JPEG sem metadados EXIF. São armazenadas no SQLite, fora da pasta estática. Remover a foto elimina os bytes e mantém o restante do perfil. Fotos de registros de acompanhamento continuam separadas.

A tabela `user_profiles` é criada automaticamente ao iniciar o servidor atualizado. Reinicie o sistema para carregar as novas rotas. O formulário de anamnese não foi alterado.

Verificação: `test_profiles.py` cobre autorização, revogação, imagem válida, metadados, exclusão, perfis privados, equipes diferentes e rankings de metas. As suítes existentes de sistema, privacidade e SUPERADM também foram executadas. A interface foi verificada em 320, 390, 768 e 1440 px, com edição e envio reais em uma base de testes isolada.
