const params=new URLSearchParams(location.search);
if(params.get('export'))document.body.classList.add('export');
const stage=document.getElementById('stage');
const slides=[...document.querySelectorAll('.slide')];
const dots=document.getElementById('dots');
const DUR=[10];
let cur=0,timer=null,playing=!params.get('s');
slides.forEach((_,i)=>{const d=document.createElement('div');d.className='dot';d.innerHTML='<i></i>';d.onclick=()=>go(i);dots.appendChild(d)});
function fit(){
  const ui=document.body.classList.contains('export')?0:56;
  const s=Math.min(innerWidth/1080,(innerHeight-ui)/1920);
  stage.style.transform=`translate(-50%,calc(-50% - ${ui/2}px)) scale(${s})`;
}
addEventListener('resize',fit);fit();
function go(i){
  clearTimeout(timer);
  cur=(i+slides.length)%slides.length;
  slides.forEach(s=>s.classList.remove('active'));
  void stage.offsetWidth;
  slides[cur].classList.add('active');
  [...dots.children].forEach((d,k)=>{
    d.classList.toggle('done',k<cur);d.classList.remove('cur');void d.offsetWidth;
    if(k===cur){d.style.setProperty('--dur',DUR[k]+'s');d.classList.add('cur')}
  });
  document.body.classList.toggle('paused',!playing);
  if(playing)timer=setTimeout(()=>{if(cur<slides.length-1)go(cur+1);else{playing=false;document.getElementById('play').textContent='▶ Play';document.body.classList.add('paused')}},DUR[cur]*1000);
}
document.getElementById('prev').onclick=()=>go(cur-1);
document.getElementById('next').onclick=()=>go(cur+1);
document.getElementById('loop').onclick=()=>{playing=true;document.getElementById('play').textContent='⏸ Pausa';go(0)};
document.getElementById('play').onclick=e=>{playing=!playing;e.target.textContent=playing?'⏸ Pausa':'▶ Play';go(cur)};
addEventListener('keydown',e=>{
  if(e.key==='ArrowRight')go(cur+1);
  if(e.key==='ArrowLeft')go(cur-1);
  if(e.key===' '){e.preventDefault();document.getElementById('play').click()}
});
go(Math.max(0,(parseInt(params.get('s'))||1)-1));
