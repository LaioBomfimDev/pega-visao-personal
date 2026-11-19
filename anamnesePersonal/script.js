'use strict';
// Configure estes três valores e inclua {{relatorio}} no template do EmailJS.
const EMAILJS_PUBLIC_KEY = 'SUA_PUBLIC_KEY';
const EMAILJS_SERVICE_ID = 'SUA_SERVICE_ID';
const EMAILJS_TEMPLATE_ID = 'SEU_TEMPLATE_ID';
const emailConfigured = ![EMAILJS_PUBLIC_KEY, EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID].some(v => /^(SUA_|SEU_)/.test(v));
const $ = id => document.getElementById(id);
const radio = name => document.querySelector(`input[name="${name}"]:checked`)?.value || '';
const checked = name => [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(el => el.value);
const value = id => $(id).disabled ? '' : $(id).value.trim();
let currentStep = 1;
let busy = false;
let exportedBlob;
let exportedName;
const titles = ['Sobre você', 'Seus objetivos', 'Treino e rotina', 'Saúde e observações'];
const fields = [
 [['modalidade','Modalidade','radio'],['nomeCompleto','Nome completo'],['idade','Idade'],['peso','Peso (kg)'],['altura','Altura (cm)'],['telefone','WhatsApp'],['email','E-mail'],['profissao','Profissão']],
 [['objetivo','Objetivos','check'],['outroObjText','Outro objetivo'],['descObjetivo','Objetivo principal'],['prazoEvento','Prazo ou evento']],
 [['diasDisponiveis','Dias disponíveis'],['duracaoSessao','Duração da sessão (minutos)'],['localTreino','Local de treino'],['cidade','Cidade e estado'],['fusoHorario','Fuso horário'],['equipamentos','Equipamentos'],['horarioContato','Horário para contato'],['horarioPresencial','Horários presenciais'],['treinaAtual','Treina atualmente?','radio'],['tempoTreino','Tempo de prática'],['freqTreino','Frequência atual'],['acompanhamento','Acompanhamento anterior','radio'],['lesao','Histórico de lesão','radio'],['descLesao','Descrição da lesão'],['exercicioDor','Exercícios que causam desconforto']],
 [['condicao','Condições diagnosticadas','check'],['outroSaudeText','Outra condição'],['medicamento','Medicamentos'],['senteDor','Sente dores atualmente?','radio'],['localDor','Local da dor'],['painScale','Intensidade da dor (0–10)'],['liberadoMedico','Liberação médica','radio'],['observacoes','Observações']]
];
function conditional(container, visible) {
 container.hidden = !visible;
 container.querySelectorAll('input,textarea,select').forEach(el => el.disabled = !visible);
}
function syncConditions() {
 conditional($('onlineFields'), radio('modalidade') === 'On-line');
 conditional($('presencialFields'), radio('modalidade') === 'Presencial');
 for (const [id, visible] of [
  ['tempoTreino',radio('treinaAtual') === 'Sim'],['freqTreino',radio('treinaAtual') === 'Sim'],
  ['descLesao',radio('lesao') === 'Sim'],['localDor',radio('senteDor') === 'Sim'],['painScale',radio('senteDor') === 'Sim']
 ]) conditional($(id).closest('.field-group'), visible);
 for (const [id, checkbox] of [['outroObjText','outroObjCb'],['outroSaudeText','outroSaudeCb']]) {
  $(id).disabled = !$(checkbox).checked;
  $(id).required = $(checkbox).checked;
 }
 $('descLesao').required = radio('lesao') === 'Sim';
 $('localDor').required = radio('senteDor') === 'Sim';
}
function clearError() { $('formError').hidden = true; }
function error(message, input) {
 $('formError').textContent = message;
 $('formError').hidden = false;
 (input || $('formError')).focus();
}
function validate(step) {
 syncConditions();
 for (const input of $(`step${step}`).querySelectorAll('input,textarea,select')) {
  if (input.disabled) continue;
  if ((input.required && !input.value.trim()) || !input.checkValidity()) {
   error('Confira o campo indicado e preencha um valor válido.', input); return false;
  }
 }
 const groups = {1:['modalidade'],2:['objetivo'],3:['treinaAtual','lesao'],4:['condicao','senteDor','liberadoMedico']};
 for (const name of groups[step] || []) {
  if (!checked(name).length) { error('Selecione uma resposta para a pergunta indicada.',document.querySelector(`input[name="${name}"]`)); return false; }
 }
 if (step === 1 && !/^\+?[\d\s().-]+$/.test(value('telefone'))) { error('Informe um telefone válido.', $('telefone')); return false; }
 if (step === 1 && (value('telefone').replace(/\D/g,'').length < 10 || value('telefone').replace(/\D/g,'').length > 15)) { error('Inclua o DDD no telefone (10 a 15 dígitos).', $('telefone')); return false; }
 clearError(); return true;
}
function collect() {
 return fields.map((section,i) => ({title:titles[i], rows:section.filter(([id,,type]) => type || !$(id).disabled).map(([id,label,type]) => ({id,label,value:(type === 'radio' ? radio(id) : type === 'check' ? checked(id).join(', ') : value(id)) || 'Não informado'}))}));
}
function renderReview() {
 $('reviewContent').replaceChildren();
 for (const [i,section] of collect().entries()) {
  const card = document.createElement('section'); card.className = 'review-card';
  const heading = document.createElement('h3'); heading.textContent = section.title;
  const edit = document.createElement('button'); edit.type = 'button'; edit.className = 'edit-button'; edit.textContent = 'Editar'; edit.setAttribute('aria-label',`Editar ${section.title}`); edit.addEventListener('click',()=>goToStep(i+1));
  card.append(heading,edit);
  const dl = document.createElement('dl');
  for (const row of section.rows) { const dt = document.createElement('dt'); dt.textContent = row.label; const dd = document.createElement('dd'); dd.textContent = row.value; dl.append(dt,dd); }
  card.append(dl); $('reviewContent').append(card);
 }
 $('deliveryNote').textContent = emailConfigured ? 'Ao enviar, suas respostas serão encaminhadas a Abel Bomfim por e-mail para análise do seu acompanhamento. Você também poderá baixar uma cópia da ficha.' : 'O envio automático ainda não está disponível. Ao concluir, você baixará sua ficha. Depois, compartilhe o arquivo com Abel pelo canal combinado. Nada será enviado automaticamente.';
}
function goToStep(step) {
 if (busy || step < 1 || step > 5) return;
 if (step > currentStep && !validate(currentStep)) return;
 clearError();
 currentStep = step;
 document.querySelectorAll('.step-pane').forEach((el,i)=>el.classList.toggle('active',i === step-1));
 document.querySelectorAll('.step-dot').forEach((el,i)=>{el.classList.toggle('active',i === step-1);el.classList.toggle('completed',i < step-1);});
 $('progressFill').style.width = `${step * 20}%`;
 $('lblStep').textContent = step;
 $('btnPrev').style.visibility = step === 1 ? 'hidden' : 'visible';
 $('btnNext').textContent = step === 5 ? (emailConfigured ? 'Enviar respostas' : 'Baixar ficha') : step === 4 ? 'Revisar' : 'Avançar';
 if (step === 5) renderReview();
 const heading = $(`step${step}`).querySelector('h2'); heading.tabIndex = -1; heading.focus({preventScroll:true}); window.scrollTo({top:0,behavior:'smooth'});
}
function saveBlob() {
 const url = URL.createObjectURL(exportedBlob);
 const link = document.createElement('a'); link.href = url; link.download = exportedName; document.body.append(link); link.click(); link.remove(); setTimeout(()=>URL.revokeObjectURL(url),30000);
}
async function makeReport(sections) {
 const text = ['ANAMNESE — ABEL BOMFIM',...sections.flatMap(s=>['',s.title,...s.rows.map(r=>`${r.label}: ${r.value}`)])].join('\n');
 const stem = `Anamnese_${value('nomeCompleto').replace(/[^\p{L}\p{N}_-]/gu,'_')}`;
 if (!window.docx) return {blob:new Blob([text],{type:'text/plain;charset=utf-8'}),name:stem+'.txt',text};
 const {Document,Packer,Paragraph,HeadingLevel} = window.docx;
 const doc = new Document({creator:'Abel Bomfim',title:'Ficha de anamnese',sections:[{children:[new Paragraph({text:'ANAMNESE — ABEL BOMFIM',heading:HeadingLevel.HEADING_1}),...sections.flatMap(s=>[new Paragraph({text:s.title,heading:HeadingLevel.HEADING_2}),...s.rows.map(r=>new Paragraph({text:`${r.label}: ${r.value}`}))])]}]});
 return {blob:await Packer.toBlob(doc),name:stem+'.docx',text};
}
async function submitForm() {
 if (busy) return;
 for(let step=1;step<=4;step++) { goToStep(step); if(!validate(step)) return; }
 goToStep(5);
 busy = true; $('btnNext').disabled = true; $('btnPrev').disabled = true;
 document.querySelectorAll('.edit-button').forEach(el=>el.disabled=true);
 $('btnNext').textContent = 'Preparando…';
 let sent = false;
 try {
  const sections = collect();
  const report = await makeReport(sections);
  exportedBlob = report.blob; exportedName = report.name;
  if (emailConfigured) {
   if (!window.emailjs) throw new Error('email-unavailable');
   $('btnNext').textContent = 'Enviando…';
   const params = Object.fromEntries(sections.flatMap(s=>s.rows.map(r=>[r.id,r.value])));
   params.nome = params.nomeCompleto; params.intensidadeDor = params.painScale || 'Não se aplica'; params.relatorio = report.text;
   await window.emailjs.send(EMAILJS_SERVICE_ID,EMAILJS_TEMPLATE_ID,params,{publicKey:EMAILJS_PUBLIC_KEY});
   sent = true;
  }
  document.querySelector('.main-container').hidden = true;
  document.querySelector('.bottom-nav').hidden = true;
  $('successScreen').classList.add('show');
  $('successTitle').textContent = sent ? 'Respostas enviadas!' : 'Sua ficha está pronta';
  $('successMessage').textContent = sent ? `Abel recebeu suas respostas para o atendimento ${radio('modalidade') === 'Presencial' ? 'presencial' : 'on-line'}. Combine os próximos passos pelo WhatsApp. Você pode baixar uma cópia abaixo.` : `Sua ficha está pronta para baixar${exportedName.endsWith('.txt') ? ' em texto, pois o gerador de Word não carregou' : ' em Word'}. Nenhuma informação foi enviada a Abel. Baixe o arquivo e compartilhe pelo canal combinado.`;
  $('downloadAgain').textContent = 'Baixar minha ficha';
  $('successTitle').focus();
  saveBlob();
 } catch (err) {
  if (sent) { $('successMessage').textContent += ' Se o download não começou, use o botão abaixo.'; }
  else error('Não foi possível concluir. Suas respostas continuam aqui. Verifique a conexão e tente novamente.');
 } finally {
  busy = false; $('btnNext').disabled = false; $('btnPrev').disabled = false;
  document.querySelectorAll('.edit-button').forEach(el=>el.disabled=false);
  $('btnNext').textContent = emailConfigured ? 'Enviar respostas' : 'Baixar ficha';
 }
}
$('btnNext').addEventListener('click',()=>currentStep === 5 ? submitForm() : goToStep(currentStep+1));
$('btnPrev').addEventListener('click',()=>goToStep(currentStep-1));
$('anamneseForm').addEventListener('submit',e=>{e.preventDefault();if(currentStep === 5) submitForm();else goToStep(currentStep+1);});
$('downloadAgain').addEventListener('click',saveBlob);
$('anamneseForm').addEventListener('change',e=>{
 if(e.target.name === 'condicao' && e.target.checked) document.querySelectorAll('input[name="condicao"]').forEach(el=>{if(el !== e.target && (e.target.value === 'Nenhum' || el.value === 'Nenhum')) el.checked = false;});
 syncConditions();
});
$('painScale').addEventListener('input',()=>{$('painVal').textContent=$('painScale').value;$('painScale').style.setProperty('--val',`${Number($('painScale').value)*10}%`);});
// Add accessible names to existing grouped questions without changing their wording.
for(const name of ['objetivo','treinaAtual','acompanhamento','lesao','condicao','senteDor','liberadoMedico']) {
 const input = document.querySelector(`input[name="${name}"]`); const group = input.closest('.field-group'); const label = group.querySelector('label'); label.id = `${name}Label`; group.setAttribute('role','group'); group.setAttribute('aria-labelledby',label.id);
}
$('outroObjCb').setAttribute('aria-label','Outro objetivo'); $('outroObjText').setAttribute('aria-label','Descreva o outro objetivo');
$('outroSaudeCb').setAttribute('aria-label','Outra condição'); $('outroSaudeText').setAttribute('aria-label','Descreva a outra condição');
$('painScale').setAttribute('aria-label','Intensidade da dor de zero a dez');
$('nomeCompleto').autocomplete='name';$('telefone').autocomplete='tel';$('email').autocomplete='email';
syncConditions();
