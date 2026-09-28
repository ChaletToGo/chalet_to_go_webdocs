const {chromium}=require('C:/Users/rafae/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 const page=await browser.newPage({viewport:{width:794,height:1123},deviceScaleFactor:2});
 await page.goto('file:///'+path.join(__dirname,'chalet-to-go-institucional-a4.html').replace(/\\/g,'/'));
 await page.evaluate(()=>document.fonts.ready);
 await page.pdf({path:path.join(__dirname,'chalet-to-go-institucional-a4.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});
 await page.screenshot({path:path.join(__dirname,'chalet-to-go-institucional-a4.png'),fullPage:true});
 console.log(await page.locator('.page').evaluate(e=>({width:e.clientWidth,height:e.clientHeight,scroll:e.scrollHeight})));
 await browser.close();
})();
