'use strict';
let data, currentQueue=[];
const $=id=>document.getElementById(id);
const pct=v=>v==null?'N/A':(v*100).toFixed(1)+'%';
const money=v=>'$'+Math.round(v).toLocaleString('en-US');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function lineChart(points,label){
 const W=500,H=210,L=48,R=15,T=15,B=30,max=Math.max(...points.map(p=>p.v),1)*1.1;
 const x=i=>L+i*(W-L-R)/Math.max(points.length-1,1),y=v=>T+(H-T-B)*(1-v/max);
 let grid=[0,.5,1].map(t=>`<line x1="${L}" x2="${W-R}" y1="${y(max*t)}" y2="${y(max*t)}" stroke="#dce4de"/><text x="${L-8}" y="${y(max*t)+4}" text-anchor="end" font-size="10" fill="#617179">${max*t>=1000?'$'+(max*t/1000).toFixed(0)+'k':'$'+Math.round(max*t)}</text>`).join('');
 let path=points.map((p,i)=>(i?'L':'M')+x(i)+','+y(p.v)).join(' ');
 let marks=points.map((p,i)=>`<circle cx="${x(i)}" cy="${y(p.v)}" r="3.5" fill="#126653"><title>${esc(p.label)}: ${money(p.v)}</title></circle>${(i%2===0||i===points.length-1)?`<text x="${x(i)}" y="${H-5}" text-anchor="middle" font-size="10" fill="#617179">${esc(p.short)}</text>`:''}`).join('');
 return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title>${grid}<path d="${path}" fill="none" stroke="#126653" stroke-width="2.5"/>${marks}</svg>`;
}
function pooled(lo,hi,category='All',channel='All'){
 const rows=data.cohorts.filter(r=>r.category===category&&r.channel===channel&&r.cohort_index>=lo&&r.cohort_index<=hi);
 const n=rows.reduce((t,r)=>t+r.eligible,0),hits=rows.reduce((t,r)=>t+r.repeaters,0);
 return {n,hits,rate:n?hits/n:null};
}
function renderDiagnosis(){
 const category=$('category').value,channel=$('channel').value;
 const ts=data.trends.filter(r=>r.category===category);
 $('spend-chart').innerHTML=lineChart(ts.map((t,i)=>({v:t.spend,label:t.as_of,short:'W'+(i+1)})),'Advertiser spend by fixed 30-day window, '+category);
 $('established-share').textContent=pct(ts.at(-1).established_share);
 const rows=data.cohorts.filter(r=>r.category===category&&r.channel===channel),W=500,H=210,L=35,R=10,T=15,B=32,plot=H-T-B,bw=(W-L-R)/12;
 let svg=[0,.5,1].map(v=>`<line x1="${L}" x2="${W-R}" y1="${T+plot*(1-v)}" y2="${T+plot*(1-v)}" stroke="#dce4de"/><text x="${L-5}" y="${T+plot*(1-v)+4}" text-anchor="end" fill="#617179" font-size="10">${v*100}%</text>`).join('');
 for(let i=0;i<12;i++){
  const r=rows.find(r=>r.cohort_index===i),x=L+i*bw+5;
  if(r&&r.rate!=null){const height=r.rate*plot;svg+=`<rect x="${x}" y="${T+plot-height}" width="${bw-11}" height="${height}" rx="2" fill="${i<5?'#126653':'#c07852'}"><title>${r.cohort}: ${r.repeaters}/${r.eligible} (${pct(r.rate)}); ${r.censored} censored</title></rect>`;}
  else svg+=`<text x="${x+(bw-11)/2}" y="${T+plot-8}" text-anchor="middle" fill="#8b938b" font-size="9">N/A</text>`;
  svg+=`<text x="${x+(bw-11)/2}" y="${H-8}" text-anchor="middle" font-size="9" fill="#617179">${i+1}</text>`;
 }
 $('cohort-chart').innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="First-spend cohort continuation, ${esc(category)}, ${esc(channel)}"><title>Continuation by first-spend cohort; unavailable rates are shown as N/A</title>${svg}</svg>`;
 const early=pooled(0,4,category,channel),late=pooled(5,9,category,channel);
 $('cohort-detail').innerHTML=`C01–05: <strong>${pct(early.rate)}</strong> (${early.hits}/${early.n}) &nbsp;→&nbsp; C06–10: <strong>${pct(late.rate)}</strong> (${late.hits}/${late.n})<details><summary>View each cohort’s denominator</summary>${rows.map(r=>`${r.cohort}: ${r.repeaters}/${r.eligible}; ${r.censored} censored`).join('<br>')}</details>`;
}
function renderEvidence(){
 const v=data.validation[+$('rule').value];
 const items=[['Alerts',v.flagged,'out of '+v.observations+' eligible account-windows'],['Precision',pct(v.precision),v.true_positive+' true / '+v.false_positive+' false alerts'],['Recall',pct(v.recall),v.false_negative+' subsequent zero-spend windows missed'],['Outcome base rate',pct(v.base_rate),v.outcomes+' next-window zero-spend outcomes']];
 $('metrics').innerHTML=items.map(([name,val,detail])=>`<div class="metric"><span>${name}</span><strong>${val}</strong><small>${detail}</small></div>`).join('');
 $('evidence-rows').innerHTML=data.validation.map((r,i)=>`<tr class="${i===+$('rule').value?'active':''}"><td>${esc(r.name)}</td><td>${r.flagged}</td><td>${r.true_positive} / ${r.false_positive}</td><td>${pct(r.precision)}</td><td>${pct(r.recall)}</td><td>${pct(r.flag_overlap)}</td></tr>`).join('');
 $('eval-population').textContent=`${v.observations} eligible account-windows from ${v.unique_accounts} unique accounts. Positive current and prior spend required; latest snapshot excluded because its outcome is unobserved. Percentages are descriptive, not significance tests.`;
 const s=data.stability;
 $('stability').innerHTML=`<p>${s.switches.toLocaleString()} of ${s.adjacent_pairs.toLocaleString()} adjacent account snapshots change stage (${pct(s.switch_rate)}), pooled over all windows.</p><div class="table-scroll"><table><thead><tr><th>From / to</th>${['Onboarding','Growth','Stable','At-risk','Inactive','Observe'].map(x=>`<th>${x}</th>`).join('')}</tr></thead><tbody>${['Onboarding','Growth','Stable','At-risk','Inactive','Observe'].map(from=>`<tr><td>${from}</td>${data.transitions.filter(r=>r.from_stage===from).map(r=>`<td>${pct(r.row_share)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
function renderQueue(){
 const category=$('category').value,motion=$('motion').value,capacity=+$('capacity').value;
 currentQueue=data.queue.filter(r=>(category==='All'||r.category===category)&&(motion==='All'||r.motion===motion));
 const selected=currentQueue.slice(0,capacity),totalValue=currentQueue.reduce((t,r)=>t+r.reference_value,0),selectedValue=selected.reduce((t,r)=>t+r.reference_value,0);
 $('capacity-value').value=capacity;
 $('queue-summary').innerHTML=`<div><strong>${selected.length} / ${currentQueue.length}</strong>candidates selected</div><div><strong>${currentQueue.length-selected.length}</strong>remain outside capacity</div><div><strong>${pct(totalValue?selectedValue/totalValue:null)}</strong>of candidate reference spend covered</div><div><strong>${selected.filter(s=>s.motion==='Activation').length}</strong>activation conversations</div>`;
 $('queue-caption').textContent=`Snapshot ${data.meta.as_of} · ${category} · ${motion}. Channel filter above applies only to the cohort chart.`;
 $('queue-rows').innerHTML=currentQueue.length?currentQueue.map((r,i)=>`<tr><td>${esc(r.account_id)}<small>${esc(r.channel)}</small></td><td>${esc(r.motion)}<small>${esc(r.stage)} · ${esc(r.value_tier)} value tier</small></td><td>${esc(r.category)}</td><td>${money(r.reference_value)}</td><td>${r.days_since_last} days ago</td><td><span class="tag ${i>=capacity?'wait':''}">${i<capacity?'Selected':'Waiting'}</span></td><td><button class="review" data-account="${r.account_id}" aria-label="Review ${r.account_id}">Review ↗</button></td></tr>`).join(''):'<tr><td colspan="7" class="empty">No eligible accounts for these filters. Try another category or motion.</td></tr>';
 $('export').disabled=selected.length===0;
}
function openAccount(id){
 const r=data.queue.find(s=>s.account_id===id),history=data.histories[id];
 const explanation=r.motion==='Activation'?`Observed first spend ${r.days_since_first} days ago; no spend for ${r.days_since_last} days. Account age ${r.tenure_days} days.`:r.reason;
 $('account-detail').innerHTML=`<h2 id="detail-title">${esc(id)}</h2><p class="meta">${esc(r.category)} · ${esc(r.channel)} · ${esc(r.motion)} review</p><div class="detail-stats"><div><strong>${money(r.value)}</strong><span>current 30-day spend</span></div><div><strong>${r.change==null?'N/A':pct(r.change)}</strong><span>change from prior window</span></div><div><strong>${r.active_days}</strong><span>positive-spend days</span></div></div>${lineChart(history.map((h,i)=>({v:h.value,label:h.as_of,short:'W'+((Date.parse(h.as_of)-Date.parse(data.meta.start))/86400000+1)/30})),'Spend history for '+id)}<div class="detail-copy"><h3>Why this account is on the list</h3><p>${esc(explanation)}</p><p>Lifecycle: <strong>${esc(r.stage)}</strong>. Value tier: <strong>${esc(r.value_tier)}</strong>, using the current-spend category threshold of ${money(data.config.value_thresholds[r.category])}. Value is not health.</p><h3>Suggested next conversation</h3><p>${esc(r.suggested_action)}</p><h3>What we still do not know</h3><p>Campaign completion, advertiser efficiency, seasonality, service issues, contact history and account-owner context. The data identify behavior, not its cause.</p><h3>How to check the intervention</h3><p>Agree a repeat-spend outcome window, randomize eligible accounts into intervention and holdout, and log exposure and costs. This account’s future response is not predicted here.</p><p class="note">Owner: unassigned · No outreach has been sent · Synthetic account</p></div>`;
 $('account-dialog').showModal();
}
function exportQueue(){
 const rows=currentQueue.slice(0,+$('capacity').value),fields=['account_id','motion','stage','value_tier','category','channel','value','previous_value','reference_value','active_days','days_since_first','days_since_last','suggested_action','owner','status'];
 const quote=x=>'"'+String(x??'').replace(/"/g,'""')+'"';
 const csv=[fields.join(','),...rows.map(r=>fields.map(f=>quote(r[f])).join(','))].join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='synthetic-merchant-review-'+data.meta.as_of+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
async function init(){
 try{
  const response=await fetch('data.json');if(!response.ok)throw new Error('Data unavailable');data=await response.json();
  $('early-rate').textContent=pct(pooled(0,4).rate);$('late-rate').textContent=pct(pooled(5,9).rate);
  $('rule').innerHTML=data.validation.map((v,i)=>`<option value="${i}" ${i===1?'selected':''}>${esc(v.name)}</option>`).join('');
  $('category').addEventListener('change',()=>{renderDiagnosis();renderQueue();});$('channel').addEventListener('change',renderDiagnosis);$('rule').addEventListener('change',renderEvidence);$('capacity').addEventListener('input',renderQueue);$('motion').addEventListener('change',renderQueue);$('export').addEventListener('click',exportQueue);
  $('queue-rows').addEventListener('click',e=>{const b=e.target.closest('[data-account]');if(b)openAccount(b.dataset.account);});$('close-dialog').addEventListener('click',()=>$('account-dialog').close());
  $('reset').addEventListener('click',()=>{$('category').value='All';$('channel').value='All';$('motion').value='All';$('capacity').value=20;renderDiagnosis();renderQueue();});
  renderDiagnosis();renderEvidence();renderQueue();$('content').hidden=false;$('loading').hidden=true;
 }catch(error){$('loading').textContent='The diagnostic could not load. Please refresh or view the source repository linked above.';console.error(error);}
}
init();
