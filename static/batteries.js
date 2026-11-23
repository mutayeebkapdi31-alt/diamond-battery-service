const st={brand:'all',cat:'all'},cards=[...document.querySelectorAll('.pcard')],chips=[...document.querySelectorAll('.chip')];
function apply(){let n=0;cards.forEach(c=>{const ok=(st.brand==='all'||c.dataset.brand===st.brand)&&(st.cat==='all'||c.dataset.cats.split(' ').includes(st.cat));
 c.hidden=!ok;if(ok){n++;c.classList.remove('pop');void c.offsetWidth;c.classList.add('pop')}});
 chips.forEach(b=>b.classList.toggle('on',st[b.dataset.f]===b.dataset.v));
 document.getElementById('count').textContent=n+' battery listing'+(n===1?'':'s')+' shown';document.getElementById('none').hidden=n>0}
chips.forEach(b=>b.addEventListener('click',()=>{st[b.dataset.f]=b.dataset.v;apply()}));
document.querySelectorAll('[data-pick]').forEach(a=>a.addEventListener('click',()=>{const[k,v]=a.dataset.pick.split(':');st.brand='all';st.cat='all';st[k]=v;apply()}));
const q=new URLSearchParams(location.search);if(q.get('brand'))st.brand=q.get('brand');if(q.get('cat'))st.cat=q.get('cat');apply();
if(q.get('brand')||q.get('cat'))setTimeout(()=>document.getElementById('products').scrollIntoView(),300);
