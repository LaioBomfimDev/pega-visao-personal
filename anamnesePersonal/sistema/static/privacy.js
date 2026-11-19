const weekNames=['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo'];
function checkField(name,label,checked=false){return `<label class="consent-check"><input type="checkbox" name="${name}" ${checked?'checked':''}><span>${label}</span></label>`}
function motivationFeed(compact=false){const list=S.entries.filter(e=>e.kind==='motivation');return `<section class="motivation-feed"><div class="card-head"><div><div class="eyebrow">UMA PALAVRA PARA SEGUIR</div><h2>${compact?'Seu feed de motivação':'Mensagens do profissional'}</h2></div>${admin()?btn('Mensagem de hoje','motivation','btn'):''}</div><p class="note">Mensagens enviadas pelo seu profissional. Sem comentários, reações ou dados de outros alunos.</p><div class="stack" style="margin-top:16px">${list.slice(0,compact?3:100).map(card).join('')||empty('Uma nova dose de motivação','A mensagem do profissional aparecerá aqui.','feed')}</div></section>`}
async function privacyAction(action,el){
 if(action!=='motivation')return false;
 modal('Mensagem motivacional de hoje',`<form id="motivationForm">${field('title','Título','text',true,'','maxlength="180"')}${area('body','Sua mensagem',true)}${checkField('confirmed','Confirmo que esta mensagem não identifica alunos nem contém informações pessoais ou de saúde deles.')}<p class="note">Será enviada ao feed dos seus alunos com notificação interna. Uma mensagem por dia.</p>${endForm('Enviar para meus alunos')}`);return true;
}
async function privacySubmit(form,data){
 if(form.id!=='motivationForm')return false;
 if(!data.confirmed)throw Error('Marque a confirmação antes de enviar.');
 await api('/entries','POST',{kind:'motivation',title:data.title,body:data.body,confirmed:true});$('#modal').close();await load();toast('Mensagem enviada.');return true;
}
