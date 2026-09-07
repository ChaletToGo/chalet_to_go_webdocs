(() => {
 const dialog=document.querySelector('#site-navigation'), opener=document.querySelector('.menu-toggle');
 opener.addEventListener('click',()=>{dialog.showModal();opener.setAttribute('aria-expanded','true');});
 dialog.querySelector('.nav-close').addEventListener('click',()=>dialog.close());
 dialog.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>dialog.close()));
 dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
 dialog.addEventListener('close',()=>{opener.setAttribute('aria-expanded','false');opener.focus();});
 const full=document.querySelector('.site-fullscreen');
 if(!document.fullscreenEnabled)full.hidden=true;
 full.addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{}});
 document.addEventListener('fullscreenchange',()=>full.setAttribute('aria-pressed',String(Boolean(document.fullscreenElement))));
})();
