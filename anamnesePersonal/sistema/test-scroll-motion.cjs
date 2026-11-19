const {chromium}=require('C:/Users/m/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({headless:true,channel:'msedge'});const errors=[];
for(const width of [320,390,1440]){
 const p=await browser.newPage({viewport:{width,height:844}});p.on('pageerror',e=>errors.push(e.message));
 await p.addInitScript(()=>{window.motionEvents=[];const original=Element.prototype.animate;Element.prototype.animate=function(...args){window.motionEvents.push(this.id||this.className);return original.apply(this,args)}});
 await p.goto('http://127.0.0.1:8766/');await p.locator('#authForm').waitFor();
 await p.evaluate(()=>{document.querySelector('#root').innerHTML='<main class="page"><div class="page-head"><h1>Prévia de movimento</h1></div><div class="stack">'+Array.from({length:12},(_,i)=>'<section class="card" id="card'+i+'" style="min-height:260px"><h2>Registro '+i+'</h2><p>Conteúdo de teste para verificar a entrada suave durante a rolagem.</p></section>').join('')+'</div></main>'});
 await p.waitForFunction(()=>window.motionEvents.includes('card0'));
 assert(!await p.evaluate(()=>window.motionEvents.includes('card8')),'card fora da tela ainda não deve animar');
 await p.locator('#card8').scrollIntoViewIfNeeded();await p.waitForFunction(()=>window.motionEvents.includes('card8'));
 await p.waitForFunction(()=>document.querySelector('#card8').getAnimations().length===0);
 assert.equal(await p.locator('#card8').evaluate(e=>getComputedStyle(e).opacity),'1');
 await p.locator('#card0').scrollIntoViewIfNeeded();await p.locator('#card8').scrollIntoViewIfNeeded();
 assert.equal(await p.evaluate(()=>window.motionEvents.filter(x=>x==='card8').length),1);
 assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'overflow '+width);
 await p.evaluate(()=>{const d=document.querySelector('#modal');d.innerHTML='<div class="card" id="modal-card"><h2>Formulário</h2><label>Nome<input id="test-input"></label></div>';d.showModal()});
 await p.locator('#modal-card').waitFor();await p.locator('#test-input').fill('Teste');
 assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 console.log('PASS '+width+'px: fade ao entrar, sem repetição, modal e sem overflow');await p.close();
}
const r=await browser.newPage({reducedMotion:'reduce'});await r.goto('http://127.0.0.1:8766/');await r.locator('#authForm').waitFor();assert.equal(await r.evaluate(()=>document.getAnimations().length),0);console.log('PASS movimento reduzido');assert.deepEqual(errors,[]);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

