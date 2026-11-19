function milestoneCards(items){return `<div class="journey-milestones">${items.map(m=>`<article class="journey-milestone"><span aria-hidden="true">${esc(m.symbol)}</span><div><h3>${esc(m.title)}</h3><p>${esc(m.description)}</p></div></article>`).join('')}</div>`}
function journeyProfileSection(){
  if(admin())return '';
  const j=S.journey||{earned:[],selected:[]};
  return `<section class="card journey-own"><div class="eyebrow">NO SEU TEMPO</div><h2>Minha jornada</h2><p>Cada passo tem seu valor. Pausas não apagam o que você já construiu.</p>${j.earned.length?milestoneCards(j.earned):'<p class="journey-welcome">Sua história já começou. Quando você registrar seu primeiro treino, seu primeiro marco aparecerá aqui.</p>'}<p class="note">${j.shared?'Sua equipe pode ver seu nome do perfil, foto, bio e somente os marcos que você escolheu.':'Sua coleção está privada. Você escolhe se quer mostrar alguns marcos à equipe.'}</p><div class="profile-controls">${j.earned.length?btn('Escolher meus destaques','journey-choose','btn secondary'):''}${j.shared?btn('Deixar jornada privada','journey-hide','text-button'):''}</div><details class="journey-help"><summary>Como estes marcos aparecem?</summary><p>O primeiro treino registrado marca o primeiro passo. Cinco e dez dias com registros reconhecem sua história, sem exigir dias seguidos. Um mês considera pelo menos 30 dias de acompanhamento e um treino registrado. A retomada reconhece um novo registro após sete dias ou mais entre registros — isso não significa que você deixou de treinar. Registros parciais também contam.</p></details></section>`;
}
function journey(){
  return head(admin()?'Jornadas da equipe':'Minha jornada','Cada pessoa tem uma história. Aqui, há espaço para celebrar a sua.')+journeyProfileSection()+`<section class="card journey-team"><div class="eyebrow">UM ESPAÇO PARA SE RECONHECER</div><h2>Histórias da equipe</h2><p class="note">Perfis compartilhados por escolha de cada pessoa, em ordem alfabética. Você não precisa compartilhar o seu para estar aqui.</p><div id="journeyTeam"><p class="note">Carregando os perfis compartilhados…</p></div></section>`;
}
async function loadJourneyTeam(){
  const target=$('#journeyTeam');if(!target)return;
  try{
    const members=await api('/journey/team');if(target!==$('#journeyTeam'))return;
    target.innerHTML=members.length?`<div class="journey-people">${members.map(p=>`<button class="journey-person" data-action="journey-profile" data-key="${esc(p.key)}">${profileAvatar(p.photo_url,p.display_name)}<span><strong>${esc(p.display_name)}</strong><small>Conhecer sua jornada</small></span></button>`).join('')}</div>`:'<p class="journey-welcome">As histórias aparecerão quando as pessoas escolherem compartilhá-las. Cada um no seu tempo.</p>';
  }catch(e){if(target===$('#journeyTeam'))target.textContent=e.message}
}
function showJourneyPicker(){
  const j=S.journey,p=S.profile||{};
  modal('Meus destaques',`<form id="journeyForm"><p>Escolha até três marcos. Todos continuam na sua coleção pessoal.</p><div class="journey-choices">${j.earned.map(m=>`<label><input type="checkbox" name="milestone" value="${esc(m.id)}" ${j.selected.includes(m.id)?'checked':''}><span aria-hidden="true">${esc(m.symbol)}</span><span><strong>${esc(m.title)}</strong><small>${esc(m.description)}</small></span></label>`).join('')}</div><div class="journey-share-preview"><h3>Seu perfil para a equipe</h3>${profileAvatar(p.photo_url,p.display_name||'Participante')}<strong>${esc(p.display_name||'Participante')}</strong>${p.bio?`<p>${esc(p.bio)}</p>`:''}<p class="note">O nome, a foto e a bio são os de Meu perfil. Os marcos exibidos serão somente os selecionados acima.</p></div>${checkField('shared','Quero mostrar meu nome do perfil, foto, bio e os marcos escolhidos aos alunos e ao profissional da minha equipe.',!!j.shared)}<p class="note">Compartilhar é opcional. Não fica aberto na internet. E-mail, peso, medidas, dor e detalhes dos treinos continuam privados. Você pode desligar quando quiser.</p>${endForm('Salvar escolhas')}`);
}
async function journeyAction(action,el){
  if(action==='journey-choose'){showJourneyPicker();return true}
  if(action==='journey-hide'){await api('/journey','POST',{shared:false,selected:S.journey.selected});await load();toast('Sua jornada está privada.');return true}
  if(action==='journey-profile'){
    const p=await api('/journey/profiles/'+encodeURIComponent(el.dataset.key));
    modal('Uma história da nossa equipe',`<div class="public-profile">${profileAvatar(p.photo_url,p.display_name,true)}<h2>${esc(p.display_name)}</h2>${p.bio?`<p class="profile-bio">${esc(p.bio)}</p>`:''}</div><h3 class="section-title">Minha jornada</h3>${milestoneCards(p.highlights)}<p class="note">Marcos escolhidos por esta pessoa. Cada trajetória tem seu próprio tempo.</p>`);return true;
  }
  return false;
}
async function journeySubmit(form){
  if(form.id!=='journeyForm')return false;
  const data=new FormData(form),selected=data.getAll('milestone'),shared=data.has('shared');
  if(selected.length>3)throw Error('Escolha até três marcos para destacar.');
  if(shared&&!selected.length)throw Error('Escolha pelo menos um marco para compartilhar.');
  await api('/journey','POST',{selected,shared,confirmed:shared});$('#modal').close();await load();toast('Suas escolhas foram salvas.');return true;
}
