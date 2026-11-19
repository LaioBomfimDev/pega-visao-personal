const {chromium}=require('C:/Users/m/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const errors=[],checks=[];const base='http://127.0.0.1:8768';
 const admin=await browser.newContext();const student=await browser.newContext();
 async function api(ctx,path,data){const state=await(await ctx.request.get(base+'/api/session')).json();const r= data===undefined?await ctx.request.get(base+'/api'+path):await ctx.request.post(base+'/api'+path,{data,headers:{'X-CSRF-Token':state.csrf}});assert(r.ok(),path+': '+await r.text());return r.json()}
 await api(admin,'/setup',{name:'Abel Bomfim',email:'mobile-abel@example.test',password:'MobileTeste123!'});
 const invite=await api(admin,'/invites',{name:'Mariana Albuquerque',email:'mariana.albuquerque@example.test',mode:'On-line'});
 await api(student,'/register',{token:new URL(invite.url).searchParams.get('convite'),password:'MobileTeste123!'});
 const uid=(await api(student,'/session')).user.id;
 const long='Acompanhamento_'+ 'evolução'.repeat(18);
 const workout=await api(admin,'/entries',{kind:'workout',target:uid,title:'Treino A · Força e mobilidade',body:long,payload:{exercises:[{name:'Agachamento com halteres e pausa na posição inferior',sets:'3',reps:'10 a 12',rest:'60 a 90 segundos'},{name:long,sets:'4',reps:'12',rest:'60s'}]}});
 await api(admin,'/entries',{kind:'instruction',target:uid,title:long,body:long});
 await api(admin,'/entries',{kind:'post',audience:'all',title:'Cada treino conta',body:long});
 await api(admin,'/entries',{kind:'resource',audience:'all',title:'Preparação para o treino',body:long});
 await api(admin,'/entries',{kind:'appointment',target:uid,title:long,payload:{datetime:'2026-12-10T15:00:00Z',place:long}});
 for(let i=0;i<6;i++)await api(student,'/entries',{kind:'progress',title:'Semana '+(i+1),body:long,payload:{weight:70-i/10,waist:80}});
 const a=await admin.newPage(),s=await student.newPage();for(const page of[a,s])page.on('pageerror',e=>errors.push(e.message));
 async function fit(page,label){await page.evaluate(()=>document.fonts.ready);const fail=await page.evaluate(()=>{const w=document.documentElement.clientWidth;return [...document.querySelectorAll('body,body *')].filter(el=>{const r=el.getBoundingClientRect();if(!r.width||!r.height||el.closest('[hidden]')||getComputedStyle(el).display==='none')return false;if(el instanceof HTMLInputElement||el instanceof HTMLSelectElement||el instanceof HTMLTextAreaElement||el.tagName==='SVG'||el.tagName==='PATH')return false;return r.right>w+1||r.left< -1||el.scrollWidth>el.clientWidth+2&&['auto','scroll'].includes(getComputedStyle(el).overflowX)}).map(el=>({tag:el.tagName,cls:el.className,w:el.clientWidth,sw:el.scrollWidth})).slice(0,8)});assert.deepEqual(fail,[],label);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),label+' root');checks.push(label)}
 async function nav(page,v){let button=page.locator('.nav [data-view="'+v+'"]');if(!await button.isVisible()){await page.locator('.nav [data-view=menu]').click();button=page.locator('.menu-item[data-view="'+v+'"]')}await button.click()}
 for(const width of[320,360,390,430,768,1024,1440]){
  for(const [role,page] of[['admin',a],['student',s]]){
   await page.setViewportSize({width,height:844});await page.goto(base);await page.locator('.shell').waitFor();
   for(const v of role==='admin'?['home','users','feed','workout','progress','calendar','book']:['home','feed','workout','progress','calendar','book']){await nav(page,v);await fit(page,role+' '+v+' '+width)}
   await page.locator('[data-view=bell]').first().click();await fit(page,role+' notifications '+width);
   await page.locator('[data-action=profile]').click();await fit(page,role+' profile '+width);
   await nav(page,'workout');await page.locator('[data-action=detail][data-id="'+workout.id+'"]').click();await fit(page,role+' workout detail '+width);
   if(role==='student'&&width===390){await page.locator('[name=weight_0]').fill('20');await page.locator('[name=done_0]').check();await page.screenshot({path:__dirname+'/mobile-workout.png',fullPage:true});await page.locator('#workoutLog button[type=submit]').click();await page.locator('#modal').waitFor({state:'hidden'})}else await page.locator('[data-action=close]').click();
   if(role==='admin'){
    await page.locator('[data-action=workout]').first().click();await page.locator('[data-action=add-exercise]').click();await fit(page,'builder '+width);await page.locator('[data-action=close]').first().click();
    await nav(page,'users');await page.locator('[data-action=student]').first().click();await fit(page,'student profile '+width);
   }else{
    await nav(page,'progress');if(width===390)await page.screenshot({path:__dirname+'/mobile-progress.png',fullPage:true});await page.locator('[data-action=progress]').first().click();await fit(page,'progress form '+width);await page.locator('[data-action=close]').first().click();
    await page.locator('[data-action=assessment]').click();const frame=page.frameLocator('iframe');await frame.locator('#idade').waitFor();await fit(page,'assessment modal '+width);const metrics=await frame.locator('body').evaluate(()=>({scroll:document.documentElement.scrollWidth,viewport:innerWidth}));assert(metrics.scroll<=metrics.viewport,'iframe overflow '+width);await page.locator('[data-action=close]').click();
   }
  }
 }
 const guest=await browser.newPage({viewport:{width:320,height:740}});await guest.goto(base);await guest.locator('#authForm').waitFor();await fit(guest,'login 320');assert.deepEqual(errors,[]);console.log(JSON.stringify({checks:checks.length,errors,result:'PASS'}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
