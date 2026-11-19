'use strict';
// Planning and evaluation UI. Domain validation remains on the server.
let planDraft = null;
let selectedPlanDay = null;
let privateNotes = [];
let chartMetric = 'weight';
let planStatus = 'active';
const sessionDrafts = new Map();
const sessionDraftKey = form => [S.user?.id,form.dataset.id,form.dataset.version,form.dataset.dayId].join(':');
function resetStudioState(){sessionDrafts.clear();planDraft=null;selectedPlanDay=null;privateNotes=[];planStatus='active'}
function rememberSession(form){
  if(!form||admin())return;
  sessionDrafts.set(sessionDraftKey(form),Object.fromEntries(new FormData(form)));
}
function restoreSession(form){
  if(!form||admin())return;
  const draft=sessionDrafts.get(sessionDraftKey(form));if(!draft)return;
  for(const control of form.elements){
    if(!control.name||control.disabled)continue;
    if(control.type==='checkbox')control.checked=Object.hasOwn(draft,control.name);
    else if(control.type==='radio')control.checked=draft[control.name]===control.value;
    else if(Object.hasOwn(draft,control.name))control.value=draft[control.name];
  }
  if(draft.rpe||draft.mood||draft.pain||draft.pain_details)form.querySelector('.studio-feedback').open=true;
}
function planStatusFilter(){
  return `<label class="field"><span>Mostrar planejamento</span><select id="planStatus">${[['active','Fichas ativas e orientações'],['archived','Fichas arquivadas'],['all','Todas as fichas e orientações']].map(([value,label])=>`<option value="${value}" ${planStatus===value?'selected':''}>${label}</option>`).join('')}</select></label>`;
}
function visiblePlanning(e){
  if(!['workout','instruction'].includes(e.kind)||S.student&&e.target!==S.student)return false;
  const archived=e.kind==='workout'&&e.payload.active===false;
  return planStatus==='all'||(planStatus==='archived'?archived:!archived);
}
const measureLabels = {weight:'Peso (kg)',waist:'Cintura (cm)',arm:'Braço (cm)',hip:'Quadril (cm)',thigh:'Coxa (cm)',fat:'Gordura (%)',muscle:'Massa muscular (kg)',pain_score:'Dor percebida (0 a 10)'};
const newExercise = () => ({name:'',sets:'3',reps:'12',rest:'60s',notes:''});
const newPlanDay = (i=0) => ({id:crypto.randomUUID(),title:`Treino ${String.fromCharCode(65+i)}`,weekdays:[],exercises:[newExercise()]});
const planDays = e => e.payload.days || [{id:'legacy',title:'Treino A',weekdays:[],exercises:e.payload.exercises||[]}];
const localToday = () => new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const calendarDate = value => /^\d{4}-\d{2}-\d{2}$/.test(value||'') ? value.split('-').reverse().join('/') : date(value);

function reportButtons(e){
  if(!['workout','assessment','progress','checkin'].includes(e.kind))return '';
  return `<div class="studio-downloads"><a class="btn secondary small" href="/api/entries/${e.id}/report.pdf">Baixar PDF</a><a class="btn secondary small" href="/api/entries/${e.id}/report.docx">Baixar Word</a></div>`;
}

function studioCardExtras(e){
  let html='';
  if(e.kind==='workout')html=`<div class="plan-tags"><span class="badge">${e.payload.active===false?'Arquivada':'Ativa'} · versão ${e.payload.version||1}</span>${planDays(e).map(d=>`<span class="badge">${esc(d.title)} · ${d.exercises.length} exercícios</span>`).join('')}</div>`;
  if(e.payload.template_id)html+=`<p class="note">Avaliação de ${calendarDate(e.payload.measured_at)} · ${esc(e.payload.template_title)}</p>`;
  return html;
}

function studioEditor(entry=null,duplicate=false){
  if(!S.users.length)return toast('Convide um aluno e aguarde a ativação para começar.');
  planDraft=entry?{id:duplicate?null:entry.id,target:entry.target,title:entry.title+(duplicate?' (cópia)':''),body:entry.body,version:entry.payload.version||1,active:entry.payload.active!==false,days:structuredClone(planDays(entry))}:{id:null,target:S.student||'',title:'Minha ficha de treino',body:'',version:1,active:true,days:[newPlanDay()]};
  if(duplicate)planDraft.days.forEach(d=>d.id=crypto.randomUUID());
  renderPlanEditor();
}

function renderPlanEditor(){
  const d=planDraft;
  modal(d.id?'Editar ficha':'Nova ficha de treino',`<form id="planForm"><div class="studio-intro"><span class="badge">${d.id?'Versão '+d.version:'Planejamento'}</span><p>Organize os dias, ajuste os exercícios e escolha quando cada treino está previsto.</p></div>
    ${d.id?`<p class="note">Aluno: ${esc(S.users.find(u=>u.id===d.target)?.name||'')}</p>`:select('target','Aluno','<option value="">Selecione um aluno</option>'+S.users.map(u=>`<option value="${u.id}" ${u.id===Number(d.target)?'selected':''}>${esc(u.name)}</option>`).join(''))}
    ${field('title','Título da ficha','text',true,d.title,'maxlength="180"')}
    <label class="field"><span>Orientações gerais</span><textarea name="body" maxlength="4000">${esc(d.body)}</textarea></label>
    <label class="consent-check"><input type="checkbox" name="active" ${d.active?'checked':''}><span>Ficha ativa para o aluno</span></label>
    <div class="plan-builder">${d.days.map((day,di)=>`<section class="plan-day-editor" data-day="${di}"><div class="studio-row"><span class="studio-day-number">${String(di+1).padStart(2,'0')}</span><div class="grow">${field('day_title_'+di,'Nome do dia','text',true,day.title,'maxlength="100"')}</div></div>
      <div class="studio-tools">${btn('Duplicar dia','plan-day-copy','btn secondary small',`data-day="${di}"`)}${btn('Remover dia','plan-day-remove','btn secondary small',`data-day="${di}" ${d.days.length===1?'disabled':''}`)}</div>
      <fieldset class="plan-weekdays"><legend>Dias previstos · opcional</legend>${weekNames.map((name,i)=>`<label><input type="checkbox" name="weekday_${di}_${i}" ${day.weekdays.includes(i)?'checked':''}><span>${name.slice(0,3)}</span></label>`).join('')}</fieldset>
      <div class="plan-exercises">${day.exercises.map((x,xi)=>`<section class="plan-exercise" data-exercise="${xi}"><div class="studio-row"><h3>Exercício ${xi+1}</h3>${btn('Remover','plan-ex-remove','text-button',`data-day="${di}" data-exercise="${xi}" aria-label="Remover exercício ${xi+1} de ${esc(day.title)}" ${day.exercises.length===1?'disabled':''}`)}</div>
        ${field(`ex_${di}_${xi}_name`,'Nome do exercício','text',true,x.name,'maxlength="180"')}
        <div class="studio-three">${[['sets','Séries'],['reps','Repetições'],['rest','Descanso']].map(([key,label])=>field(`ex_${di}_${xi}_${key}`,label,'text',false,x[key],'maxlength="180"')).join('')}</div>
        ${field(`ex_${di}_${xi}_notes`,'Observações do exercício','text',false,x.notes||'','maxlength="500"')}</section>`).join('')}</div>
      ${btn('Adicionar exercício','plan-ex-add','btn secondary',`data-day="${di}"`)}</section>`).join('')}</div>
    ${btn('Adicionar dia de treino','plan-day-add','btn secondary full')}
    <p class="note">As sessões já realizadas mantêm os exercícios e a versão utilizados. Arquivar a ficha preserva seu histórico.</p>${endForm(d.id?'Salvar nova versão':'Salvar ficha')}</form>`);
}

function collectPlan(){
  const form=$('#planForm');if(!form||!planDraft)return;
  const data=new FormData(form);
  planDraft.title=data.get('title');planDraft.body=data.get('body');planDraft.active=data.has('active');
  if(!planDraft.id)planDraft.target=Number(data.get('target'));
  planDraft.days.forEach((day,di)=>{
    day.title=data.get('day_title_'+di);day.weekdays=weekNames.flatMap((_,i)=>data.has(`weekday_${di}_${i}`)?[i]:[]);
    day.exercises.forEach((x,xi)=>['name','sets','reps','rest','notes'].forEach(key=>x[key]=data.get(`ex_${di}_${xi}_${key}`)||''));
  });
}

function structuredFeedback(){
  return `<details class="studio-feedback"><summary>Esforço, humor e desconforto · opcional</summary><div class="form-grid">
    ${field('rpe','Esforço percebido (1 a 10)','number',false,'','min="1" max="10" step="1"')}
    <label class="field"><span>Humor após o treino</span><select name="mood"><option value="">Prefiro não informar</option><option value="bem">Bem</option><option value="normal">Normal</option><option value="cansado">Cansado</option></select></label></div>
    <label class="consent-check"><input type="checkbox" name="pain"><span>Senti dor ou desconforto</span></label>
    <label class="field"><span>Onde e como foi o desconforto?</span><textarea name="pain_details" maxlength="500" placeholder="Preencha se marcou a opção acima"></textarea></label></details>`;
}

function sessionFeedbackSummary(d){
  return `${d.plan_version?`<p class="session-version">Ficha usada: versão ${d.plan_version}${d.day_title?' · '+esc(d.day_title):''}</p>`:''}<div class="session-feedback-summary">${d.rpe?`<span>Esforço ${d.rpe}/10</span>`:''}${d.mood?`<span>Humor: ${esc({bem:'Bem',normal:'Normal',cansado:'Cansado'}[d.mood]||d.mood)}</span>`:''}${d.pain?'<span>Dor ou desconforto relatado</span>':''}</div>${d.pain&&d.pain_details?`<p class="session-note">${esc(d.pain_details)}</p>`:''}`;
}

function studioWorkoutDetail(e,requestedDay){
  const days=planDays(e),weekday=(new Date(localToday()+'T12:00:00Z').getUTCDay()+6)%7;
  const chosen=days.find(d=>d.id===requestedDay)||days.find(d=>d.weekdays.includes(weekday))||days[0];
  selectedPlanDay={entry:e.id,day:chosen.id,version:e.payload.version||1};
  const archived=e.payload.active===false;
  modal(esc(e.title),`<div class="studio-intro"><span class="badge">${archived?'Arquivada':'Ativa'} · versão ${e.payload.version||1}</span><p class="post-body">${esc(e.body)}</p></div>
    ${reportButtons(e)}<div class="plan-day-tabs" aria-label="Dias da ficha">${days.map(d=>`<button class="${d.id===chosen.id?'selected':''}" data-action="plan-select-day" data-id="${e.id}" data-day-id="${esc(d.id)}" aria-pressed="${d.id===chosen.id}"><strong>${esc(d.title)}</strong><small>${d.weekdays.length?d.weekdays.map(i=>weekNames[i].slice(0,3)).join(' · '):'Dias a combinar'}</small></button>`).join('')}</div>
    <h3>${esc(chosen.title)}</h3><p class="note">${chosen.weekdays.length?'Previsto para '+chosen.weekdays.map(i=>weekNames[i]).join(', '):'Combine os dias de treino com seu profissional.'}</p>
    <form id="workoutLog" data-id="${e.id}" data-day-id="${esc(chosen.id)}" data-version="${e.payload.version||1}"><div class="exercise-list">${chosen.exercises.map((x,i)=>`<section class="exercise"><div class="exercise-title"><span class="exercise-number">${String(i+1).padStart(2,'0')}</span><div><strong>${esc(x.name)}</strong><p>${esc(x.sets)} séries · ${esc(x.reps)} repetições</p><small>Descanso: ${esc(x.rest)}</small>${x.notes?`<p>${esc(x.notes)}</p>`:''}</div></div>
      <label class="exercise-load"><span>Carga (kg)</span><input type="number" inputmode="decimal" name="weight_${i}" min="0" max="1000" step="0.1" aria-label="Carga de ${esc(x.name)}" ${admin()||archived?'disabled':''}></label><label class="exercise-done"><input type="checkbox" name="done_${i}" aria-label="Concluir ${esc(x.name)}" ${admin()||archived?'disabled':''}><span>Realizado</span></label></section>`).join('')}</div>
    ${!admin()&&!archived?workoutFeeling()+structuredFeedback()+'<button class="btn" type="submit">Enviar meu treino</button><p class="note">Trocar de dia ou fechar a ficha mantém o preenchimento nesta página. Recarregar a página ou sair da conta descarta o que ainda não foi enviado.</p>':''}</form>
    ${archived?'<p class="notice">Esta ficha foi arquivada. Os registros anteriores continuam disponíveis abaixo.</p>':''}
    ${admin()?`<div class="studio-tools">${btn('Editar ficha','plan-edit','btn',`data-id="${e.id}"`)}${btn('Duplicar ficha','plan-copy','btn secondary',`data-id="${e.id}"`)}${btn('Histórico de versões','plan-versions','btn secondary',`data-id="${e.id}"`)}</div><form id="receiptForm" data-id="${e.id}" data-status="Avaliado">${area('body','Sua avaliação ou orientação',true)}<button class="btn" type="submit">Salvar devolutiva</button></form>`:`<form id="receiptForm" data-id="${e.id}" data-status="Solicitou revisão">${area('body','Precisa de ajuste? Conte ao seu profissional.',true)}<button class="btn secondary" type="submit">Solicitar revisão</button></form>`}
    ${e.receipts.filter(r=>r.status==='Avaliado').map(r=>`<div class="review-note"><strong>Orientação do profissional</strong><p>${esc(r.body)}</p></div>`).join('')}${sessionHistory(e)}`);
  if(!archived)restoreSession($('#workoutLog'));
}

function evaluationActions(){
  return `<section class="studio-evaluations"><div><div class="eyebrow">EVOLUÇÃO EM PERSPECTIVA</div><h2>Avaliações periódicas</h2><p>Compare momentos da sua jornada, com registros que permanecem no histórico.</p></div><div class="evaluation-options">${(S.evaluationTemplates||[]).map(t=>`<button data-action="evaluation" data-template="${esc(t.id)}"><strong>${esc(t.title)}</strong><span>${esc(t.description)}</span><b>Registrar avaliação →</b></button>`).join('')}</div></section>`;
}

function studioProgress(){
  const list=S.entries.filter(e=>['progress','checkin','assessment'].includes(e.kind)&&(!S.student||e.target===S.student));
  return head('Evolução','Cada registro ajuda a entender sua jornada.',!admin()?'progress':null,'Novo registro')+targetFilter()+evaluationActions()+
    (!admin()?`<div class="studio-tools">${btn('Check-in da semana','checkin','btn secondary')}${btn('Preencher anamnese','assessment','btn secondary')}</div>`:'')+
    ((!admin()||S.student)?evolutionChart(list):'<p class="notice">Selecione um aluno para comparar suas medidas no gráfico.</p>')+
    `<h2 class="section-title">Histórico de registros</h2><div class="stack">${list.map(card).join('')||empty('Sua história começa aqui','Registre a primeira avaliação para acompanhar as próximas etapas.','progress')}</div>`;
}

function evolutionChart(list){
  const points=list.filter(e=>e.kind==='progress'&&e.payload[chartMetric]!==undefined&&e.payload[chartMetric]!==''&&Number.isFinite(Number(e.payload[chartMetric])))
    .map(e=>({id:e.id,date:e.payload.measured_at||e.created.slice(0,10),value:Number(e.payload[chartMetric])})).sort((a,b)=>a.date.localeCompare(b.date)||a.id-b.id);
  let graphic=empty('Ainda sem medidas neste indicador','Os valores registrados nas avaliações aparecerão aqui.','progress');
  if(points.length){
    const values=points.map(p=>p.value),low=Math.min(...values),high=Math.max(...values),pad=Math.max((high-low)*.2,1),min=Math.max(0,low-pad),max=high+pad;
    const coords=points.map((p,i)=>[50+(points.length===1?.5:i/(points.length-1))*520,170-(p.value-min)/(max-min)*140]);
    graphic=`<div class="chart-summary"><strong>${values.at(-1).toLocaleString('pt-BR')}</strong><span>${esc(measureLabels[chartMetric])}<small>${calendarDate(points.at(-1).date)} · ${points.length} registros</small></span></div>
      <svg class="evolution-svg" viewBox="0 0 620 210" role="img" aria-label="${esc(measureLabels[chartMetric])} ao longo de ${points.length} avaliações. Valores na tabela abaixo."><path d="M50 30V170H570" fill="none" stroke="#d7cbbc"/><text x="4" y="37">${max.toFixed(1)}</text><text x="4" y="172">${min.toFixed(1)}</text><polyline points="${coords.map(p=>p.join(',')).join(' ')}" fill="none" stroke="#bd4c14" stroke-width="3"/>${coords.map(([x,y],i)=>`<circle cx="${x}" cy="${y}" r="5" fill="#bd4c14"><title>${calendarDate(points[i].date)}: ${points[i].value}</title></circle>`).join('')}<text x="50" y="200">${calendarDate(points[0].date)}</text><text x="570" y="200" text-anchor="end">${calendarDate(points.at(-1).date)}</text></svg>
      <p class="note">Pontos ordenados por avaliação. O gráfico não representa uma meta nem uma interpretação clínica.</p><details><summary>Ver valores e datas</summary><div class="measure-history">${points.map(p=>`<div><span>${calendarDate(p.date)}</span><strong>${p.value.toLocaleString('pt-BR')}</strong>${btn('Abrir registro','detail','text-button',`data-id="${p.id}"`)}</div>`).join('')}</div></details>`;
  }
  return `<section class="card studio-chart"><div class="card-head"><h2>Suas medidas ao longo do tempo</h2></div><label class="field"><span>Indicador</span><select id="chartMetric">${Object.entries(measureLabels).map(([k,label])=>`<option value="${k}" ${k===chartMetric?'selected':''}>${label}</option>`).join('')}</select></label>${graphic}</section>`;
}

function showEvaluation(templateId){
  const t=S.evaluationTemplates.find(t=>t.id===templateId);if(!t)return;
  if(admin()&&!S.users.length)return toast('Convide um aluno primeiro.');
  modal(esc(t.title),`<form id="evaluationForm" data-template="${esc(t.id)}"><p>${esc(t.description)}</p>${admin()?studentSelect():''}${field('measured_at','Data da avaliação','date',true,localToday(),`max="${localToday()}" min="1900-01-01"`)}<div class="form-grid">${t.fields.map(f=>f.type==='number'?field(f.id,f.label,'number',false,'',`min="${f.min}" max="${f.max}" step="0.1"`):`<label class="field"><span>${esc(f.label)}</span><textarea name="${esc(f.id)}" maxlength="1500"></textarea></label>`).join('')}</div>${area('body','Observações')}<p class="note">Preencha apenas o que sabe ou mediu. Você pode fazer novas avaliações no mesmo mês; todas permanecem no histórico privado.</p>${endForm('Salvar avaliação')}`);
}

async function showPrivateNotes(uid){
  privateNotes=await api(`/students/${uid}/notes`);
  modal('Notas privadas do profissional',`<p class="notice">Somente você, profissional responsável, acessa estas notas. Elas não aparecem para o aluno nem nos relatórios compartilháveis.</p><form id="coachNoteForm" data-student="${uid}"><label class="field"><span>Nova nota</span><textarea name="body" required maxlength="5000"></textarea></label><button class="btn" type="submit">Adicionar nota</button></form><div class="stack studio-notes">${privateNotes.map(n=>`<article class="card"><p class="post-body">${esc(n.body)}</p><small>${sessionWhen(n.updated)} · versão ${n.version}</small>${btn('Editar nota','note-edit','text-button',`data-id="${n.id}" data-student="${uid}"`)}</article>`).join('')||empty('Nenhuma nota ainda','Registre aqui observações internas do acompanhamento.')}</div>`);
}

function evaluationDetail(e){
  if(!e.payload.template_id)return '';
  return `<section class="studio-evaluation-detail"><h3>${esc(e.payload.template_title)}</h3><p>${calendarDate(e.payload.measured_at)}</p>${(e.payload.sections||[]).flatMap(s=>s.rows).map(r=>`<div class="measure-row"><span>${esc(r.label)}</span><strong>${esc(r.value)}</strong></div>`).join('')}</section>`;
}

async function studioAction(action,el){
  const id=Number(el.dataset.id);
  if(action.startsWith('plan-day-')||action.startsWith('plan-ex-')){
    collectPlan();const di=Number(el.dataset.day),xi=Number(el.dataset.exercise);
    if(action==='plan-day-add'){if(planDraft.days.length>=8)throw Error('Limite de 8 dias.');planDraft.days.push(newPlanDay(planDraft.days.length))}
    if(action==='plan-day-copy'){if(planDraft.days.length>=8)throw Error('Limite de 8 dias.');const copy=structuredClone(planDraft.days[di]);copy.id=crypto.randomUUID();copy.title=copy.title.slice(0,90)+' (cópia)';planDraft.days.splice(di+1,0,copy)}
    if(action==='plan-day-remove'&&planDraft.days.length>1)planDraft.days.splice(di,1);
    if(action==='plan-ex-add'){if(planDraft.days[di].exercises.length>=40)throw Error('Limite de 40 exercícios por dia.');planDraft.days[di].exercises.push(newExercise())}
    if(action==='plan-ex-remove'&&planDraft.days[di].exercises.length>1)planDraft.days[di].exercises.splice(xi,1);
    renderPlanEditor();return true;
  }
  if(action==='plan-edit'||action==='plan-copy'){studioEditor(S.entries.find(e=>e.id===id),action==='plan-copy');return true}
  if(action==='plan-select-day'){studioWorkoutDetail(S.entries.find(e=>e.id===id),el.dataset.dayId);return true}
  if(action==='plan-versions'){
    const versions=await api(`/entries/${id}/versions`);
    modal('Histórico da ficha',`<p class="note">Cada alteração preserva a versão anterior. As sessões guardam a ficha utilizada no registro.</p>${versions.map(v=>`<details class="card"><summary>Versão ${v.payload.version||1} · ${esc(v.title)} · ${sessionWhen(v.saved_at)}</summary><p>${esc(v.body)}</p>${planDays({payload:v.payload}).map(d=>`<h3>${esc(d.title)}</h3>${d.exercises.map(x=>`<p>${esc(x.name)} · ${esc(x.sets)} × ${esc(x.reps)} · ${esc(x.rest)}<br>${esc(x.notes||'')}</p>`).join('')}`).join('')}</details>`).join('')||empty('Primeira versão','Quando a ficha for editada, a versão anterior aparecerá aqui.')}`);return true;
  }
  if(action==='evaluation'){showEvaluation(el.dataset.template||'monthly');return true}
  if(action==='private-notes'){await showPrivateNotes(id);return true}
  if(action==='note-edit'){
    const n=privateNotes.find(n=>n.id===id);if(!n)return true;
    modal('Editar nota privada',`<form id="coachNoteForm" data-student="${el.dataset.student}" data-id="${id}" data-version="${n.version}"><label class="field"><span>Nota</span><textarea name="body" required maxlength="5000">${esc(n.body)}</textarea></label>${endForm('Salvar nota')}`);return true;
  }
  if(action==='edit'&&S.entries.find(e=>e.id===id)?.kind==='workout'){studioEditor(S.entries.find(e=>e.id===id));return true}
  return false;
}

async function studioSubmit(form,data){
  if(form.id==='planForm'){
    collectPlan();const d=planDraft,payload={days:d.days,active:d.active};
    if(d.id)await api(`/entries/${d.id}/edit`,'POST',{title:d.title,body:d.body,payload,expected_version:d.version});
    else await api('/entries','POST',{kind:'workout',title:d.title,body:d.body,target:d.target,payload});
    $('#modal').close();planDraft=null;await load();toast('Ficha salva. As sessões anteriores foram preservadas.');return true;
  }
  if(form.id==='workoutLog'){
    const e=S.entries.find(e=>e.id===Number(form.dataset.id)),day=planDays(e).find(d=>d.id===form.dataset.dayId);
    if(!day)throw Error('Reabra a ficha para escolher um dia.');
    const logs=day.exercises.map((x,i)=>({name:x.name,weight:data['weight_'+i]||'',done:!!data['done_'+i]}));
    if(!logs.some(x=>x.done))throw Error('Marque ao menos um exercício realizado.');
    await api(`/entries/${e.id}/receipt`,'POST',{status:'Concluído',body:JSON.stringify({logs,day_id:day.id,plan_version:Number(form.dataset.version),note:data.note||'',feeling:data.feeling||'',rpe:data.rpe?Number(data.rpe):null,mood:data.mood||'',pain:!!data.pain,pain_details:data.pain_details||''})});
    sessionDrafts.delete(sessionDraftKey(form));$('#modal').close();await load();toast('Sessão registrada para '+day.title+'.');return true;
  }
  if(form.id==='evaluationForm'){
    const t=S.evaluationTemplates.find(t=>t.id===form.dataset.template),values=Object.fromEntries(t.fields.map(f=>[f.id,data[f.id]||'']));
    await api('/evaluations','POST',{template_id:t.id,target:Number(data.target)||undefined,measured_at:data.measured_at,body:data.body||'',values});
    $('#modal').close();await load();toast('Avaliação salva no histórico.');return true;
  }
  if(form.id==='coachNoteForm'){
    await api(`/students/${form.dataset.student}/notes${form.dataset.id?'/'+form.dataset.id:''}`,'POST',{body:data.body,version:Number(form.dataset.version)});
    await showPrivateNotes(Number(form.dataset.student));toast('Nota privada salva.');return true;
  }
  return false;
}

document.addEventListener('change',e=>{if(e.target.id==='chartMetric'){chartMetric=e.target.value;render()}});
document.addEventListener('change',e=>{if(e.target.id==='planStatus'){planStatus=e.target.value;render()}});
for(const eventName of ['input','change'])document.addEventListener(eventName,e=>{if(e.target.form?.id==='workoutLog')rememberSession(e.target.form)});
