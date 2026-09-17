async page => {
  const base = '/Users/pagemacmini/maplab-ai-handbook/reviews/TASK-RECOVERY-20260917';
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text().slice(0, 300)); });
  page.on('pageerror', error => pageErrors.push(String(error).slice(0, 300)));
  const views = [];
  for (const viewport of [{width:390,height:844},{width:1280,height:800}]) {
    await page.setViewportSize(viewport);
    const response = await page.goto('https://www.maplabkitchen.com/', { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForLoadState('networkidle', {timeout:15000}).catch(() => {});
    await page.evaluate(async () => {
      for(let y=0;y<document.body.scrollHeight;y+=500) {
        window.scrollTo(0,y);
        await new Promise(resolve=>setTimeout(resolve,120));
      }
      window.scrollTo(0,0);
    });
    for (const image of await page.locator('img').all()) {
      await image.scrollIntoViewIfNeeded();
      await page.waitForTimeout(150);
    }
    await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth>0 && (!i.hasAttribute('data-lazy-src') || !(i.currentSrc||i.src).startsWith('data:'))), null, {timeout:15000}).catch(() => {});
    await page.evaluate(() => window.scrollTo(0,0));
    await page.waitForTimeout(800);
    const metrics = await page.evaluate(() => {
      const rect = el => {const b=el.getBoundingClientRect();return {x:b.x,y:b.y,width:b.width,height:b.height};};
      const visible = el => {const s=getComputedStyle(el),b=el.getBoundingClientRect();return s.display!=='none' && s.visibility!=='hidden' && b.width>0 && b.height>0;};
      const leafText = [...document.body.querySelectorAll('*')].filter(el => visible(el) && !['SCRIPT','STYLE','NOSCRIPT'].includes(el.tagName) && el.children.length===0 && el.textContent.trim());
      return {
        url:location.href,title:document.title,bodyClass:document.body.className,
        viewport:{width:innerWidth,height:innerHeight},scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,
        horizontalOverflow:document.documentElement.scrollWidth>innerWidth,
        overflowElements:[...document.body.querySelectorAll('*')].filter(el=>visible(el) && (el.getBoundingClientRect().right>innerWidth+1 || el.getBoundingClientRect().left < -1)).slice(0,12).map(el=>({tag:el.tagName,class:el.className,rect:rect(el)})),
        h1:[...document.querySelectorAll('h1')].map(el=>el.innerText),
        headings:[...document.querySelectorAll('h2,h3')].map(el=>el.innerText),
        canonical:document.querySelector('link[rel=canonical]')?.href,
        draftbarElements:document.querySelectorAll('.draftbar').length,
        images:[...document.images].map(i=>({src:i.currentSrc||i.src,alt:i.alt,complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight})),
        lineCTAs:[...document.querySelectorAll('a[href*="lin.ee"]')].map(el=>({text:el.innerText,href:el.href,class:el.className,rect:rect(el)})),
        internalLinks:[...document.querySelectorAll('a')].filter(el=>el.href.startsWith(location.origin)).map(el=>({text:el.innerText,href:el.href})),
        visibleTextUnder16px:leafText.filter(el=>parseFloat(getComputedStyle(el).fontSize)<16).map(el=>({tag:el.tagName,class:el.className,text:el.textContent.trim().slice(0,80),fontSize:getComputedStyle(el).fontSize})),
        navigationTiming:performance.getEntriesByType('navigation').map(n=>({duration:n.duration,domContentLoaded:n.domContentLoadedEventEnd,responseEnd:n.responseEnd})),
        disclaimer:'Browser timing is a single local run, not a field CWV or mobile-network performance certification.'
      };
    });
    await page.screenshot({path:`${base}/live-${viewport.width}-full.png`,fullPage:true});
    await page.screenshot({path:`${base}/live-${viewport.width}-top.png`});
    await page.getByRole('heading',{name:'怎麼報僺',exact:true}).scrollIntoViewIfNeeded();
    await page.screenshot({path:`${base}/live-${viewport.width}-quote-section.png`});
    const faq=[];
    const summaries=page.locator('details summary');
    for(let i=0;i<await summaries.count();i++) {
      const summary=summaries.nth(i);
      if (await summary.evaluate(el=>el.parentElement.open)) {
        await summary.click();
        await page.waitForFunction(n=>!document.querySelectorAll('details')[n].open, i);
      }
      await summary.click();
      await page.waitForFunction(n=>document.querySelectorAll('details')[n].open, i);
      await page.waitForTimeout(100);
      const openReadback=await summary.evaluate(el=>({question:el.innerText,open:el.parentElement.open,answer:el.parentElement.querySelector('p')?.innerText}));
      await summary.click();
      await page.waitForFunction(n=>!document.querySelectorAll('details')[n].open, i);
      openReadback.closeVerified=await summary.evaluate(el=>!el.parentElement.open);
      await summary.click();
      await page.waitForFunction(n=>document.querySelectorAll('details')[n].open, i);
      faq.push(openReadback);
    }
    await page.getByRole('heading',{name:'常見問題',exact:true}).scrollIntoViewIfNeeded();
    await page.screenshot({path:`${base}/live-${viewport.width}-faq-open.png`});
    views.push({viewport,httpStatus:response?.status(),metrics,faq});
  }
  return {verifiedAt:new Date().toISOString(),scope:'public-read-only; isolated anonymous browser; no external writes',views,consoleErrors:[...new Set(consoleErrors)],pageErrors:[...new Set(pageErrors)]};
}
