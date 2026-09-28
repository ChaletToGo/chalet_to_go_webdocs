const {chromium}=require('C:/Users/rafae/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 const page=await browser.newPage({viewport:{width:794,height:1123},deviceScaleFactor:3.125});
 await page.goto('file:///'+path.join(__dirname,'chalet-to-go-campanha-a4.html').replace(/\\/g,'/'));
 await page.evaluate(()=>document.fonts.ready);
 // Flatten only the photo and CSS gradient to opaque RGB, retaining live text and SVGs.
 await page.locator('.hero-copy').evaluate(e=>e.style.visibility='hidden');
 await page.locator('.inset').evaluate(e=>e.style.visibility='hidden');
 const hero=await page.locator('.hero').screenshot({type:'png',path:path.join(__dirname,'chalet-to-go-hero-degrade-rgb.png'),omitBackground:false});
 await page.evaluate(async data=>{
   const img=document.querySelector('.scene');
   img.src=data;img.style.objectFit='fill';
   await img.decode();
   document.querySelector('.shade').remove();
   document.querySelector('.hero-copy').style.visibility='visible';
   document.querySelector('.inset').style.visibility='visible';
 },'data:image/png;base64,'+hero.toString('base64'));
 await page.pdf({path:path.join(__dirname,'chalet-to-go-campanha-a4-corrigido.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});
 await page.screenshot({path:path.join(__dirname,'chalet-to-go-campanha-a4-corrigido.png'),fullPage:true});
 await browser.close();
})();
