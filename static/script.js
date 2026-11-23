const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
// Battery checker
const slider=$('#slider'),lvl=$('#level'),pct=$('#pct'),vd=$('#verdict');
function upd(){const v=+slider.value;lvl.style.width=v+'%';pct.textContent=v+'%';
 const [c,t]=v<35?['#c8102e','Weak. Replacement likely needed soon.']:v<70?['#e59a00','Fair. Get it tested before it leaves you stranded.']:['#2e9e5b','Healthy. Keep it maintained.'];
 lvl.style.background=c;vd.textContent=t}
if(slider){slider.addEventListener('input',upd);upd()}
// Scroll reveal with stagger
$$('.grid,.wgrid,.sgrid2,.sgrid,.stats,.faq').forEach(g=>[...g.children].forEach((e,i)=>e.style.setProperty('--d',(i%6)*.08+'s')));
const rio=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');rio.unobserve(e.target)}}),{threshold:.12});
$$('.rv').forEach(e=>rio.observe(e));
// Count-up
const cio=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;cio.unobserve(e.target);
 const n=+e.target.dataset.n;let i=0;const s=Math.max(1,Math.round(n/50));
 const t=setInterval(()=>{i=Math.min(n,i+s);e.target.textContent=i.toLocaleString('en-IN');if(i>=n)clearInterval(t)},30)}),{threshold:.6});
$$('[data-n]').forEach(e=>cio.observe(e));
// Reviews
const rv=$$('#rev blockquote');let k=0;if(rv.length)setInterval(()=>{rv[k].classList.remove('on');k=(k+1)%rv.length;rv[k].classList.add('on')},5000);
// Booking form
const f=$('#bf'),m=$('#fmsg');
f&&f.addEventListener('submit',async e=>{e.preventDefault();m.textContent='Sending...';const d=Object.fromEntries(new FormData(f));
 try{const r=await fetch('/api/book',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});const j=await r.json();
  if(j.ok){m.textContent='Request received. We will call you shortly.';m.style.color='#9be3b4';f.reset()}else{m.textContent=j.error;m.style.color='#ffb3bc'}
 }catch{m.textContent='Could not send. Please call us directly.';m.style.color='#ffb3bc'}});
const yr=$('#yr');if(yr)yr.textContent=new Date().getFullYear();
// Menu, header shadow, scroll progress
const nv=$('#nav'),mn=$('#menu'),bg=$('#burger'),pr=$('#prog');
bg.addEventListener('click',()=>{const o=mn.classList.toggle('open');bg.setAttribute('aria-expanded',o)});
mn.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>mn.classList.remove('open')));
addEventListener('scroll',()=>{nv.classList.toggle('sc',scrollY>10);pr.style.width=(scrollY/(document.documentElement.scrollHeight-innerHeight)*100)+'%'},{passive:true});
// Service links preselect the form
$$('[data-s]').forEach(a=>a.addEventListener('click',()=>{const s=$('#svcSel');for(const o of s.options)if(o.text===a.dataset.s)s.value=o.text}));
