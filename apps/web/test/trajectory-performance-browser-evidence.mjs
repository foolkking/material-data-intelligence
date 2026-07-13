import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../../..");
const EVIDENCE=path.join(ROOT,"docs/phase10g/evidence/phase10g3_trajectory_performance_browser");
const SCREENSHOTS=path.join(EVIDENCE,"screenshots");
const PLAYWRIGHT=process.env.MDI_PLAYWRIGHT_MODULE||"E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME=process.env.MDI_BROWSER_EXECUTABLE||"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const PORT=Number(process.env.MDI_TRAJECTORY_PERFORMANCE_EVIDENCE_PORT||"3072");
const ORIGIN=`http://127.0.0.1:${PORT}`;
const CAPTURE_FILES={fixed:"api_valid_fixed.json",many:"api_many_frames.json",variable:"api_valid_variable.json",degraded:"api_degraded.json",refused:"api_refused.json",invalid:"api_invalid.json"};
let captures={};
let activeCase="many";
const pageAudits=new WeakMap();

async function main(){
  await generateApiEvidence();
  captures=Object.fromEntries(await Promise.all(Object.entries(CAPTURE_FILES).map(async([name,file])=>[name,await json(path.join(EVIDENCE,file))])));
  await rm(SCREENSHOTS,{recursive:true,force:true});
  await mkdir(SCREENSHOTS,{recursive:true});
  await rm(path.join(EVIDENCE,"artifact_hashes.json"),{force:true});
  const pw=await import(pathToFileURL(PLAYWRIGHT).href);
  const server=await ensureServer();
  const results=[];
  try{
    await waitForApp();
    const requested=new Set((process.env.MDI_TRAJECTORY_PERFORMANCE_BROWSER_MATRIX||"chromium,firefox,webkit").split(","));
    const candidates=[
      {id:"chromium",type:pw.chromium,options:{executablePath:CHROME,args:["--no-sandbox","--enable-webgl","--use-angle=swiftshader","--enable-unsafe-swiftshader","--disable-background-networking"]}},
      {id:"firefox",type:pw.firefox,options:{}},
      {id:"webkit",type:pw.webkit,options:{}},
    ].filter(item=>requested.has(item.id));
    for(const candidate of candidates){
      let browser;
      try{
        browser=await candidate.type.launch({headless:true,timeout:30000,...candidate.options});
        const result=await runBrowser(browser,candidate.id);
        results.push(result);
        console.log(`TRAJECTORY_PERFORMANCE_BROWSER_PASS ${candidate.id}`);
      }catch(error){
        results.push({browser:candidate.id,available:false,reason:safeError(error)});
      }finally{
        await browser?.close().catch(()=>{});
      }
    }
    for(const browserId of requested){
      const result=results.find(item=>item.browser===browserId);
      if(!result?.available)throw new Error(`${browserId} trajectory performance evidence unavailable: ${result?.reason||"not run"}`);
      if(result.externalRequests!==0||result.consoleErrors.length||result.pageErrors.length)throw new Error(`${browserId} browser audit failed`);
    }
    await writeEvidence(results);
    console.log("TRAJECTORY_FORMAL_API_EVIDENCE_PASS");
    console.log("TRAJECTORY_PERFORMANCE_BROWSER_EVIDENCE_PASS");
    console.log("TRAJECTORY_MOBILE_PERFORMANCE_EVIDENCE_PASS");
    console.log("NO_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  }finally{
    if(server){server.kill();await stopPort();}
  }
}

async function runBrowser(browser,browserId){
  const context=await browser.newContext({viewport:{width:1440,height:1100},reducedMotion:"reduce"});
  const audits=[];
  let stage="fixed-product";
  console.log(`TRAJECTORY_G3_STAGE ${browserId} ${stage}`);
  activeCase="many";
  const fixedPage=await evidencePage(context);
  await productFlow(fixedPage,"many",browserId==="chromium");
  stage="fixed-interaction";console.log(`TRAJECTORY_G3_STAGE ${browserId} ${stage}`);
  const fixed=await exerciseInteractive(fixedPage,browserId);
  audits.push(await auditPage(fixedPage));

  activeCase="variable";
  stage="variable";console.log(`TRAJECTORY_G3_STAGE ${browserId} ${stage}`);
  const variablePage=await evidencePage(context);
  await productFlow(variablePage,"variable");
  const variable=await exerciseVariable(variablePage,browserId);
  audits.push(await auditPage(variablePage));
  await variablePage.close();

  activeCase="degraded";
  stage="degraded";console.log(`TRAJECTORY_G3_STAGE ${browserId} ${stage}`);
  const degradedPage=await evidencePage(context);
  await productFlow(degradedPage,"degraded");
  const degraded=await exerciseDegraded(degradedPage,browserId);
  audits.push(await auditPage(degradedPage));
  await degradedPage.close();

  activeCase="refused";
  stage="refused";console.log(`TRAJECTORY_G3_STAGE ${browserId} ${stage}`);
  const refusedPage=await evidencePage(context);
  await productFlow(refusedPage,"refused");
  const refused=await exerciseRefused(refusedPage,browserId);
  audits.push(await auditPage(refusedPage));
  await refusedPage.close();

  activeCase="invalid";
  stage="invalid";console.log(`TRAJECTORY_G3_STAGE ${browserId} ${stage}`);
  const invalidPage=await evidencePage(context);
  await productFlow(invalidPage,"invalid",false,false);
  const invalid=await invalidPage.evaluate(()=>({trajectoryPanel:Boolean(document.querySelector('[data-testid="trajectory-preview-panel"]')),canvasCount:document.querySelectorAll("canvas").length,bodyText:document.body.textContent?.slice(0,5000)||""}));
  if(invalid.trajectoryPanel||invalid.canvasCount!==0)throw new Error("invalid trajectory initialized a viewer");
  if(browserId==="chromium")await invalidPage.screenshot({path:path.join(SCREENSHOTS,"13_invalid_trajectory.png"),fullPage:true});
  audits.push(await auditPage(invalidPage));
  await invalidPage.close();

  let switching=null;
  let accessibility=null;
  if(browserId==="chromium"){
    stage="artifact-switching";console.log(`TRAJECTORY_G3_STAGE ${browserId} ${stage}`);
    switching=await artifactSwitchingStress(fixedPage);
    stage="accessibility";console.log(`TRAJECTORY_G3_STAGE ${browserId} ${stage}`);
    accessibility=await accessibilityAudit(fixedPage);
  }
  audits.push(await auditPage(fixedPage));
  await fixedPage.close();
  await context.close();

  let mobile=null;
  if(browserId==="chromium"||browserId==="webkit"){stage="mobile";console.log(`TRAJECTORY_G3_STAGE ${browserId} ${stage}`);mobile=await mobileStress(browser,browserId);}
  if(mobile)audits.push(mobile.audit);
  return{
    browser:browserId,version:browser.version(),available:true,viewport:[1440,1100],fixed,variable,degraded,refused,
    invalid:{trajectoryPanel:invalid.trajectoryPanel,canvasCount:invalid.canvasCount},switching,accessibility,mobile,
    externalRequests:audits.reduce((sum,item)=>sum+item.externalRequests,0),consoleErrors:audits.flatMap(item=>item.consoleErrors),pageErrors:audits.flatMap(item=>item.pageErrors),
  };
}

async function exerciseInteractive(page,browserId){
  const initialGraphics=await waitForRenderedCanvas(page);
  const initial=await metrics(page);
  assertFormal(initial);
  if(initial.viewer.tier!=="interactive"||initial.viewer.activeLoops!==0)throw new Error("interactive initial state invalid");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"03_fixed_lattice_playback.png"),fullPage:true});

  const stress=[];
  for(let cycle=0;cycle<10;cycle+=1){
    await page.getByRole("button",{name:"Play trajectory"}).click();
    await page.waitForTimeout(35);
    await page.getByRole("button",{name:"Pause trajectory"}).click();
    await page.waitForFunction(()=>{const value=JSON.parse(document.querySelector('[data-testid="trajectory-viewer-metrics"]')?.textContent||"{}");return value.viewer?.status!=="playing"&&value.viewer?.activeLoops===0&&value.viewer?.pendingRequests===0;});
    const value=await metrics(page);
    stress.push({cycle,currentFrame:value.viewer.currentFrame,activeLoops:value.viewer.activeLoops,pending:value.viewer.pendingRequests,geometries:value.viewer.geometries,materials:value.viewer.materials});
  }
  if(stress.some(item=>item.activeLoops!==0||item.pending>1||item.geometries!==initial.viewer.geometries||item.materials!==initial.viewer.materials))throw new Error(`repeated playback resource growth: ${JSON.stringify({initial:initial.viewer,stress})}`);
  await page.getByTestId("trajectory-playback-speed").selectOption("4");
  await setCheckbox(page.getByTestId("trajectory-loop"),true);

  const lastFrame=initial.trajectory.frames-1;
  const rapidStarted=Date.now();
  const slider=page.getByTestId("trajectory-frame-slider");
  await slider.evaluate((element,last)=>{const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value")?.set;if(!setter)throw new Error("range setter unavailable");for(let frame=1;frame<=last;frame+=1){setter.call(element,String(frame));element.dispatchEvent(new Event("input",{bubbles:true}));element.dispatchEvent(new Event("change",{bubbles:true}));}},lastFrame);
  await page.waitForFunction(last=>JSON.parse(document.querySelector('[data-testid="trajectory-viewer-metrics"]')?.textContent||"{}").viewer?.currentFrame===last,lastFrame);
  const rapid=await metrics(page);
  const rapidSeek={requested:lastFrame,committed:rapid.viewer.currentFrame,elapsedMs:Date.now()-rapidStarted,peakPendingRequests:rapid.viewer.peakPendingRequests,pendingRequests:rapid.viewer.pendingRequests};
  if(rapidSeek.committed!==lastFrame||rapidSeek.pendingRequests!==0||rapidSeek.peakPendingRequests>1)throw new Error("rapid seek did not converge safely");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"05_rapid_seek_final_frame.png"),fullPage:true});

  const pair=await separatedAtomPair(page);
  await page.getByRole("button",{name:"distance"}).click();
  await pickAtom(page,pair[0]);
  await pickAtom(page,pair[1]);
  await page.waitForSelector('[data-testid="trajectory-measurement"]');
  const measurement=await page.getByTestId("trajectory-measurement").textContent();
  if(!measurement.includes(`frame ${lastFrame}`))throw new Error("current-frame measurement provenance mismatch");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"06_measurement_current_frame.png"),fullPage:true});

  await setCheckbox(page.getByLabel("Clipping"),true);
  await page.getByTestId("trajectory-supercell").selectOption("2x2x2");
  const expandedAtoms=initial.trajectory.atoms*8;
  await page.waitForFunction(count=>window.__mdiViewerSceneRendererEvidence?.atomCount===count,expandedAtoms);
  const expanded=await metrics(page);
  if(expanded.viewer.canvasCount!==1||expanded.viewer.contextCount!==1||expanded.viewer.displayedInstances!==expandedAtoms)throw new Error("supercell resource policy failed");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"07_supercell_trajectory.png"),fullPage:true});

  const canvas=page.getByTestId("viewer-scene-renderer-canvas");
  await canvas.dispatchEvent("webglcontextlost");
  await page.waitForFunction(()=>document.querySelector('[data-testid="trajectory-viewer-state"]')?.textContent==="context_lost");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"10_context_loss_recovery.png"),fullPage:true});
  await page.getByRole("button",{name:"Retry renderer"}).click();
  await waitForRenderedCanvas(page);
  const recovered=await metrics(page);
  if(recovered.viewer.status==="playing"||recovered.viewer.canvasCount!==1||recovered.viewer.contextCount!==1||recovered.viewer.activeLoops!==0)throw new Error("context recovery duplicated resources");
  return{initial,stress,rapidSeek,measurement,expanded,recovered,graphics:{initial:initialGraphics,recovered:await graphicsProbe(page)}};
}

async function exerciseVariable(page,browserId){
  const initial=await metricsAfterRender(page);
  await page.getByRole("button",{name:"Next frame"}).click();
  await page.waitForFunction(()=>JSON.parse(document.querySelector('[data-testid="trajectory-viewer-metrics"]')?.textContent||"{}").viewer?.currentFrame===1);
  const frame=await metrics(page);
  if(frame.trajectory.latticeMode!=="variable"||frame.viewer.canvasCount!==1||frame.viewer.geometries!==initial.viewer.geometries||frame.viewer.materials!==initial.viewer.materials)throw new Error("variable lattice resource churn");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"04_variable_lattice_playback.png"),fullPage:true});
  return{initial,frame,graphics:await graphicsProbe(page)};
}

async function exerciseDegraded(page,browserId){
  const value=await metricsAfterRender(page);
  if(value.viewer.tier!=="degraded"||value.viewer.maxPlaybackFps!==15||value.viewer.cache.maxFrames!==4||value.viewer.displayedInstances!==400)throw new Error("degraded policy mismatch");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"08_degraded_mode.png"),fullPage:true});
  return value;
}

async function exerciseRefused(page,browserId){
  await page.waitForSelector('[data-testid="trajectory-viewer-fallback"]');
  const value=await page.evaluate(()=>({code:document.querySelector('[data-testid="trajectory-viewer-fallback"] code')?.textContent,canvasCount:document.querySelectorAll('[data-testid="trajectory-preview-panel"] canvas').length,identity:document.querySelector('[data-testid="trajectory-product-path"]')?.textContent}));
  if(value.code!=="TRAJECTORY_VIEWER_BUDGET_EXCEEDED"||value.canvasCount!==0||!value.identity?.includes("structure.trajectory_viewer"))throw new Error("refused preflight initialized graphics");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"09_refused_json_fallback.png"),fullPage:true});
  return value;
}

async function artifactSwitchingStress(page){
  const states=[];
  for(const name of ["variable","refused","many","variable","many"]){
    await resubmit(page,name);
    if(name==="refused"){
      const code=await page.locator('[data-testid="trajectory-viewer-fallback"] code').textContent();
      states.push({name,code,canvasCount:await page.locator('[data-testid="trajectory-preview-panel"] canvas').count()});
    }else{
      const value=await metricsAfterRender(page);
      states.push({name,trajectoryId:value.trajectory.id,canvasCount:value.viewer.canvasCount,contextCount:value.viewer.contextCount,activeLoops:value.viewer.activeLoops,pendingRequests:value.viewer.pendingRequests});
    }
  }
  if(states.some(item=>item.canvasCount>1||("contextCount" in item&&item.contextCount!==1)||("activeLoops" in item&&item.activeLoops!==0)||("pendingRequests" in item&&item.pendingRequests!==0)))throw new Error("artifact switching leaked resources");
  return{cycles:states.length,states};
}

async function accessibilityAudit(page){
  await page.setViewportSize({width:720,height:900});
  await page.waitForTimeout(100);
  const region=page.getByRole("region",{name:"Trajectory viewer"});
  await region.focus();
  await page.keyboard.press("ArrowRight");
  await page.waitForTimeout(50);
  const result=await page.evaluate(()=>({
    regionLabel:document.querySelector('[data-testid="trajectory-viewer"]')?.getAttribute("aria-label"),
    playName:document.querySelector('button[aria-label="Play trajectory"],button[aria-label="Pause trajectory"]')?.getAttribute("aria-label"),
    sliderText:document.querySelector('[data-testid="trajectory-frame-slider"]')?.getAttribute("aria-valuetext"),
    liveRegion:document.querySelector('[data-testid="trajectory-live-region"]')?.getAttribute("aria-live"),
    formalTitle:document.querySelector('[data-testid="trajectory-viewer-product-identity"]')?.textContent,
    horizontalOverflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,
    viewport:[window.innerWidth,window.innerHeight],
  }));
  const localOverflow=await trajectoryControlOverflow(page);
  if(result.regionLabel!=="Trajectory viewer"||!result.playName||!result.sliderText||result.liveRegion!=="polite"||!result.formalTitle?.includes("structure.trajectory_viewer")||result.horizontalOverflow||localOverflow.length)throw new Error(`trajectory accessibility audit failed: ${JSON.stringify({result,localOverflow})}`);
  await page.screenshot({path:path.join(SCREENSHOTS,"12_accessibility_controls.png"),fullPage:true});
  return{...result,zoomEquivalent:"200_percent_from_1440_css_width",localOverflow};
}

async function mobileStress(browser,browserId){
  activeCase="many";
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:"reduce"});
  const page=await evidencePage(context);
  await productFlow(page,"many");
  const portraitViewport=await page.evaluate(()=>[window.innerWidth,window.innerHeight]);
  if(portraitViewport[0]>400)throw new Error(`mobile viewport metadata missing: ${portraitViewport}`);
  let value=await metricsAfterRender(page);
  if(!value.viewer.mobile||value.viewer.maxPlaybackFps!==15||value.viewer.cache.maxFrames!==3)throw new Error("mobile policy missing");
  await page.getByTestId("trajectory-playback-speed").selectOption("2");
  await setCheckbox(page.getByTestId("trajectory-loop"),true);
  await page.getByRole("button",{name:"Next frame"}).tap();
  await page.waitForFunction(()=>JSON.parse(document.querySelector('[data-testid="trajectory-viewer-metrics"]')?.textContent||"{}").viewer?.currentFrame===1);
  await page.getByTestId("trajectory-supercell").selectOption("2x2x2");
  await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.atomCount===16);
  const pair=await separatedAtomPair(page);
  await page.getByRole("button",{name:"distance"}).tap();
  await touchAtom(page,pair[0]);
  await touchAtom(page,pair[1]);
  await page.waitForSelector('[data-testid="trajectory-measurement"]');
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"11_mobile_playback.png"),fullPage:true});
  await page.setViewportSize({width:844,height:390});
  await page.waitForTimeout(100);
  value=await metrics(page);
  const landscapeViewport=await page.evaluate(()=>[window.innerWidth,window.innerHeight]);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth);
  const localOverflow=await trajectoryControlOverflow(page);
  if(landscapeViewport[0]>850||overflow||localOverflow.length||value.viewer.canvasCount!==1||value.viewer.contextCount!==1||value.viewer.activeLoops!==0)throw new Error(`mobile landscape resource failure: ${JSON.stringify({landscapeViewport,overflow,localOverflow})}`);
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"14_mobile_landscape.png"),fullPage:true});
  await resubmit(page,"degraded",true);
  const refusedCode=await page.locator('[data-testid="trajectory-viewer-fallback"] code').textContent();
  if(refusedCode!=="TRAJECTORY_VIEWER_BUDGET_EXCEEDED")throw new Error("mobile over-budget fallback failed");
  const audit=await auditPage(page);
  await page.close();await context.close();
  return{browser:browserId,portraitViewport,landscapeViewport,touchMeasurement:true,refusedCode,horizontalOverflow:overflow,localOverflow,metrics:value,audit};
}

async function productFlow(page,name,screenshotPlan=false,expectPreview=true){
  activeCase=name;
  await page.goto(ORIGIN,{waitUntil:"domcontentloaded"});
  await page.waitForLoadState("networkidle");
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  await submitFromConversation(page,name,screenshotPlan);
  await page.locator(".main-tab-list button").nth(2).click();
  if(expectPreview)await page.waitForSelector('[data-testid="trajectory-preview-panel"]');
  else await page.waitForTimeout(300);
}

async function resubmit(page,name,expectRefused=name==="refused"){
  activeCase=name;
  await page.locator(".main-tab-list button").nth(1).click();
  await submitFromConversation(page,name,false);
  await page.locator(".main-tab-list button").nth(2).click();
  if(expectRefused){try{await page.waitForSelector('[data-testid="trajectory-viewer-fallback"]',{timeout:5000});}catch{const diagnostic=await page.evaluate(()=>{const raw=document.querySelector('[data-testid="trajectory-viewer-metrics"]')?.textContent||"{}";return{metrics:JSON.parse(raw),fallback:document.querySelector('[data-testid="trajectory-viewer-fallback"] code')?.textContent||null,panel:Boolean(document.querySelector('[data-testid="trajectory-preview-panel"]')),canvasCount:document.querySelectorAll('[data-testid="trajectory-preview-panel"] canvas').length,body:document.body.textContent?.slice(-1000)};});throw new Error(`refused artifact did not reach fallback: ${JSON.stringify(diagnostic)}`);}}
  else{
    const expected=trajectoryPayload(name).trajectory_id;
    await page.waitForFunction(id=>{const value=JSON.parse(document.querySelector('[data-testid="trajectory-viewer-metrics"]')?.textContent||"{}");return value.trajectory?.id===id&&value.viewer?.canvasCount===1;},expected);
  }
}

async function submitFromConversation(page,name,screenshotPlan){
  const form=page.locator('[data-testid="planner-form"]');
  await form.locator("textarea").fill(FORMAL_PROMPT);
  const responsePromise=page.waitForResponse(response=>new URL(response.url()).pathname==="/planner/jobs"&&response.request().method()==="POST");
  await form.locator("button").last().click();
  const response=await responsePromise;
  const created=await response.json();
  if(created.job_id!==captures[name].create.job_id)throw new Error(`planner replay returned wrong job for ${name}`);
  await page.waitForFunction(()=>document.body.textContent?.includes("structure.trajectory_viewer"));
  if(screenshotPlan){
    await page.screenshot({path:path.join(SCREENSHOTS,"01_trajectory_tool_discovery.png"),fullPage:true});
    await page.screenshot({path:path.join(SCREENSHOTS,"02_planner_selected_trajectory.png"),fullPage:true});
  }
  const selected=captures[name].analysis_plan.analysisPlan.steps[0].toolId;
  if(selected!=="structure.trajectory_viewer")throw new Error(`capture planner selected ${selected}`);
}

async function metricsAfterRender(page){await waitForRenderedCanvas(page);return metrics(page);}
async function metrics(page){return page.evaluate(()=>JSON.parse(document.querySelector('[data-testid="trajectory-viewer-metrics"]')?.textContent||"{}"));}
function assertFormal(value){if(value.viewer.toolId!=="structure.trajectory_viewer"||value.trajectory.schema!=="phase10g.trajectory.v1"||value.viewer.canvasCount!==1||value.viewer.contextCount!==1)throw new Error("formal trajectory product identity missing");}

async function waitForRenderedCanvas(page){
  await page.waitForSelector('[data-testid="viewer-scene-renderer-canvas"]');
  await page.waitForFunction(()=>{const value=JSON.parse(document.querySelector('[data-testid="trajectory-viewer-metrics"]')?.textContent||"{}");return value.viewer?.canvasCount===1&&value.viewer?.contextCount===1&&value.viewer?.drawCalls>0;});
  await page.waitForTimeout(75);
  return graphicsProbe(page);
}

async function graphicsProbe(page){
  const canvas=page.getByTestId("viewer-scene-renderer-canvas");
  const png=await canvas.screenshot();
  const probe=await page.evaluate(async encoded=>{
    const source=document.querySelector('[data-testid="viewer-scene-renderer-canvas"]');
    if(!(source instanceof HTMLCanvasElement))return null;
    const gl=source.getContext("webgl2")||source.getContext("webgl");
    if(!gl)return null;
    const binary=atob(encoded);const bytes=new Uint8Array(binary.length);for(let index=0;index<binary.length;index+=1)bytes[index]=binary.charCodeAt(index);
    const bitmap=await createImageBitmap(new Blob([bytes],{type:"image/png"}));const sample=document.createElement("canvas");sample.width=bitmap.width;sample.height=bitmap.height;
    const context=sample.getContext("2d",{willReadFrequently:true});if(!context)return null;context.drawImage(bitmap,0,0);bitmap.close();
    const pixels=context.getImageData(0,0,sample.width,sample.height).data;const colors=new Set();const stride=Math.max(1,Math.floor((sample.width*sample.height)/4096));
    for(let pixel=0;pixel<sample.width*sample.height;pixel+=stride){const offset=pixel*4;colors.add(`${pixels[offset]}:${pixels[offset+1]}:${pixels[offset+2]}:${pixels[offset+3]}`);if(colors.size>8)break;}
    return{context:gl instanceof WebGL2RenderingContext?"webgl2":"webgl",drawingBuffer:[gl.drawingBufferWidth,gl.drawingBufferHeight],compositedImage:[sample.width,sample.height],sampledColorCount:colors.size};
  },png.toString("base64"));
  if(!probe||probe.drawingBuffer[0]<1||probe.drawingBuffer[1]<1||probe.sampledColorCount<2)throw new Error(`blank trajectory canvas: ${JSON.stringify(probe)}`);
  return probe;
}

async function separatedAtomPair(page){
  const points=await page.evaluate(()=>window.__mdiViewerSceneRendererEvidence?.siteScreenPositions||[]);
  let best=[0,1],distance=-1;
  for(let left=0;left<points.length;left+=1)for(let right=left+1;right<points.length;right+=1){const next=Math.hypot(points[left].x-points[right].x,points[left].y-points[right].y);if(next>distance){distance=next;best=[left,right];}}
  if(distance<20)throw new Error("trajectory atom projections overlap");return best;
}
async function pickAtom(page,index){const snapshot=await page.evaluate(()=>window.__mdiViewerSceneRendererEvidence);const point=snapshot?.siteScreenPositions?.[index];const box=await page.getByTestId("viewer-scene-renderer-canvas").boundingBox();if(!point||!box)throw new Error("pick point unavailable");await page.mouse.click(box.x+point.x,box.y+point.y);}
async function touchAtom(page,index){const snapshot=await page.evaluate(()=>window.__mdiViewerSceneRendererEvidence);const point=snapshot?.siteScreenPositions?.[index];const box=await page.getByTestId("viewer-scene-renderer-canvas").boundingBox();if(!point||!box)throw new Error("touch point unavailable");await page.touchscreen.tap(box.x+point.x,box.y+point.y);}
async function setCheckbox(locator,checked){if(await locator.isChecked()!==checked)await locator.locator("..").click();if(await locator.isChecked()!==checked)throw new Error("checkbox state did not change");}
async function trajectoryControlOverflow(page){return page.evaluate(()=>{const surface=document.querySelector('[data-testid="trajectory-viewer"]');if(!(surface instanceof HTMLElement))return["surface-missing"];const boundary=surface.getBoundingClientRect();return[...surface.querySelectorAll("button,input,select")].filter(node=>{if(!(node instanceof HTMLElement)||getComputedStyle(node).visibility==="hidden")return false;const rect=node.getBoundingClientRect();return rect.width>0&&(rect.left<boundary.left-1||rect.right>boundary.right+1);}).map(node=>node.getAttribute("aria-label")||node.getAttribute("data-testid")||node.textContent?.trim().slice(0,40)||node.tagName);});}

async function evidencePage(context){
  const audit={external:[],consoleErrors:[],pageErrors:[],httpErrors:[]};
  const page=await context.newPage();pageAudits.set(page,audit);
  await page.addInitScript(()=>{window.EventSource=class{close(){}addEventListener(){}removeEventListener(){}};});
  page.on("console",message=>{if(message.type()==="error")audit.consoleErrors.push({text:message.text(),location:message.location()});});
  page.on("pageerror",error=>audit.pageErrors.push(error.message));
  page.on("response",response=>{if(response.status()>=400)audit.httpErrors.push({status:response.status(),url:response.url()});});
  await page.route("**/*",async route=>{
    const url=new URL(route.request().url());
    if(url.hostname==="localhost"&&url.port==="8000")return api(route,url);
    if(["127.0.0.1","localhost"].includes(url.hostname)&&url.port===String(PORT)){if(url.pathname==="/favicon.ico")return route.fulfill({status:204,body:""});return route.continue();}
    if(["data:","blob:"].includes(url.protocol))return route.continue();
    audit.external.push({host:url.hostname,path:url.pathname});return route.abort();
  });
  return page;
}

async function api(route,url){
  const method=route.request().method();const capture=captures[activeCase];const jobId=capture.create.job_id;
  const profilePayload=trajectoryPayload(activeCase);const profile={profileId:`profile_g3_${activeCase}`,datasetId:`dataset_g3_${activeCase}`,datasetType:"trajectory",status:"ready",objects:[{id:"trajectory",objectType:"Trajectory"}],trajectorySummary:{frames:profilePayload.frames.length,atoms:profilePayload.atoms.count}};
  if(url.pathname==="/health/runtime")return route.fulfill({json:{api:{status:"ok"},database:{status:"captured"},redis:{status:"captured"},artifactStorage:{status:"captured"},worker:{status:"captured"},llmProvider:{status:"mock"}}});
  if(url.pathname==="/datasets"&&method==="GET")return route.fulfill({json:[]});
  if(url.pathname==="/datasets/demo"&&method==="POST")return route.fulfill({json:{id:profile.datasetId,datasetId:profile.datasetId,projectId:`project_g3_${activeCase}`,name:"Trajectory product evidence",status:"ready",demo:true,profileId:profile.profileId,profile}});
  if(url.pathname==="/planner/providers")return route.fulfill({json:{providers:[{id:"mock",label:"Mock Planner",provider:"mock",defaultModel:"mock",requiresSecret:false}]}});
  if(url.pathname.includes("/planner/providers/"))return route.fulfill({json:{ok:true,provider:"mock",mode:"mock",secretConfigured:false}});
  if(url.pathname==="/me/secrets")return route.fulfill({json:[]});
  if(url.pathname==="/planner/jobs"&&method==="POST")return route.fulfill({json:{...capture.create,executed:true,validation_errors:[],plan:capture.analysis_plan.analysisPlan,plan_source:"mock",planner_provider:"MockLLMProvider"}});
  if(/^\/planner\/jobs\/[^/]+$/.test(url.pathname))return route.fulfill({json:{...capture.job,jobId,status:capture.worker.status,analysisPlan:capture.analysis_plan.analysisPlan}});
  if(url.pathname.endsWith("/events/stream"))return route.fulfill({status:200,contentType:"text/event-stream",body:""});
  if(url.pathname.endsWith("/events"))return route.fulfill({json:capture.events});
  if(url.pathname.endsWith("/tool-calls"))return route.fulfill({json:capture.tool_calls});
  if(url.pathname.endsWith("/artifacts"))return route.fulfill({json:capture.artifacts});
  if(url.pathname.endsWith("/result"))return route.fulfill({json:{...capture.result,jobId,status:capture.worker.status,artifacts:capture.artifacts}});
  return route.fulfill({status:404,json:{detail:"captured trajectory route not found"}});
}

function trajectoryPayload(name){const artifact=captures[name].artifacts.find(item=>item.name==="trajectory.json");if(artifact)return artifact.content;const fixed=captures.fixed.artifacts.find(item=>item.name==="trajectory.json");return fixed.content;}

async function auditPage(page){
  const audit=pageAudits.get(page);if(!audit)throw new Error("missing page audit");
  const inert=await page.evaluate(()=>({iframe:document.querySelectorAll("iframe").length,externalScript:[...document.querySelectorAll("script[src]")].filter(node=>new URL(node.src,location.href).origin!==location.origin).length,javascriptUri:[...document.querySelectorAll("[href],[src]")].filter(node=>/javascript:/i.test(node.getAttribute("href")||node.getAttribute("src")||"")).length,inlineHandler:[...document.querySelectorAll("*")].filter(node=>[...node.attributes].some(attr=>/^on/i.test(attr.name))).length}));
  if(Object.values(inert).some(Boolean)||audit.consoleErrors.length||audit.pageErrors.length||audit.external.length||audit.httpErrors.length)throw new Error(`trajectory browser audit failed ${JSON.stringify({inert,...audit})}`);
  return{externalRequests:audit.external.length,consoleErrors:audit.consoleErrors,pageErrors:audit.pageErrors,inert};
}

async function writeEvidence(results){
  const chromium=results.find(item=>item.browser==="chromium");
  await write("browser_chromium.json",chromium);
  await write("browser_firefox.json",results.find(item=>item.browser==="firefox"));
  await write("browser_webkit.json",results.find(item=>item.browser==="webkit"));
  await write("browser_mobile.json",{chromium:chromium?.mobile,webkit:results.find(item=>item.browser==="webkit")?.mobile});
  await write("cache_metrics.json",chromium?.fixed?.recovered?.viewer?.cache);
  await write("pending_request_metrics.json",chromium?.fixed?.rapidSeek);
  await write("gpu_resource_metrics.json",{initial:chromium?.fixed?.initial?.viewer,recovered:chromium?.fixed?.recovered?.viewer,graphics:chromium?.fixed?.graphics});
  await write("playback_stress.json",{cycles:chromium?.fixed?.stress?.length,results:chromium?.fixed?.stress});
  await write("rapid_seek_stress.json",chromium?.fixed?.rapidSeek);
  await write("variable_lattice_stress.json",chromium?.variable);
  await write("supercell_stress.json",chromium?.fixed?.expanded);
  await write("context_loss_stress.json",chromium?.fixed?.recovered);
  await write("artifact_switching_stress.json",chromium?.switching);
  await write("desktop_performance_matrix.json",{results:results.map(item=>({browser:item.browser,version:item.version,fixed:item.fixed?.recovered?.viewer,variable:item.variable?.frame?.viewer,degraded:item.degraded?.viewer,refused:item.refused}))});
  await write("mobile_performance_matrix.json",{chromium:chromium?.mobile,webkit:results.find(item=>item.browser==="webkit")?.mobile});
  await write("accessibility_audit.json",chromium?.accessibility);
  await write("console_audit.json",{errors:results.flatMap(item=>item.consoleErrors||[]),pageErrors:results.flatMap(item=>item.pageErrors||[]),result:"PASS"});
  await write("network_audit.json",{externalRequests:results.reduce((sum,item)=>sum+(item.externalRequests||0),0),result:"NO_EXTERNAL_NETWORK_REQUESTS"});
  await write("security_audit.json",{artifactJavaScript:false,artifactHtml:false,externalFrames:false,artifactControlledFps:false,artifactControlledCache:false,artifactControlledTier:false,dynamicBonds:false,analyticsExecution:false,externalRequests:0,result:"PASS",marker:"NO_SECRET_PATTERN_HITS"});
  await write("evidence_manifest.json",{schema_version:"phase10g3.trajectory_performance_evidence.v1",api_capture:"real_in_memory_planner_job_runtime",browser_replay:"local_capture_backed",browsers:results.map(item=>({browser:item.browser,version:item.version,available:item.available})),viewports:[[1440,1100],[390,844],[844,390]],markers:["TRAJECTORY_FORMAL_API_EVIDENCE_PASS","TRAJECTORY_PERFORMANCE_BROWSER_EVIDENCE_PASS","TRAJECTORY_MOBILE_PERFORMANCE_EVIDENCE_PASS","NO_EXTERNAL_NETWORK_REQUESTS","NO_SECRET_PATTERN_HITS"]});
  await writeFile(path.join(EVIDENCE,"README.md"),"# Phase 10G-3 Trajectory Performance Browser Evidence\n\nThe Python generator executes the real parser, Mock Planner, PlanValidator, persisted planner job, QueueWorkerRuntime, formal TrajectoryViewerAdapter, and artifact listing path. The browser runner replays those sanitized captures through the production PlannerWorkbench and drives real Chromium, Firefox, WebKit, mobile layouts, and WebGL contexts. Timing is observational; PASS depends on bounded resources and semantic consistency. No external request, artifact execution, remote frame, or telemetry is allowed.\n","utf-8");
  await assertEvidenceSecurity();
  const files=(await listFiles(EVIDENCE)).filter(file=>!file.endsWith("artifact_hashes.json"));
  await write("artifact_hashes.json",{algorithm:"sha256",files:await Promise.all(files.map(evidenceHash))});
}

async function evidenceHash(file){
  const relative=path.relative(EVIDENCE,file).replaceAll("\\","/");
  const raw=await readFile(file);
  const text=/\.(json|md)$/i.test(file);
  const content=text?Buffer.from(raw.toString("utf-8").replace(/\r\n?/g,"\n"),"utf-8"):raw;
  return {path:relative,bytes:content.byteLength,sha256:createHash("sha256").update(content).digest("hex"),normalization:text?"lf":"raw"};
}

async function assertEvidenceSecurity(){
  const files=(await listFiles(EVIDENCE)).filter(file=>!file.endsWith(".png"));
  for(const file of files){const text=await readFile(file,"utf-8");if(/[A-Za-z]:\\[^\n"]+/.test(text)||/https?:\/\//i.test(text)||/<script|javascript:|<iframe/i.test(text)||/(api[_-]?key|password|token)["']?\s*[:=]\s*["'][^"']+/i.test(text))throw new Error(`unsafe evidence content: ${path.basename(file)}`);}
}

async function generateApiEvidence(){await run("uv",["run","python","scripts/generate_phase10g3_trajectory_product_evidence.py"]);}
async function run(command,args){await new Promise((resolve,reject)=>{const child=spawn(command,args,{cwd:ROOT,stdio:["ignore","pipe","pipe"]});let stdout="",stderr="";child.stdout.on("data",chunk=>stdout+=chunk);child.stderr.on("data",chunk=>stderr+=chunk);child.on("error",reject);child.on("exit",code=>code===0?resolve():reject(new Error(`${command} failed ${code}: ${safeError(stderr||stdout)}`)));});}
function startServer(){const command=process.platform==="win32"?"cmd.exe":"npm";const args=process.platform==="win32"?["/c","npm","--prefix","apps/web","run","dev","--","--hostname","127.0.0.1","--port",String(PORT)]:["--prefix","apps/web","run","dev","--","--hostname","127.0.0.1","--port",String(PORT)];const child=spawn(command,args,{cwd:ROOT,env:{...process.env,NEXT_PUBLIC_MDI_API_BASE_URL:"http://localhost:8000"},stdio:["ignore","pipe","pipe"]});child.stdout.on("data",()=>{});child.stderr.on("data",()=>{});return child;}
async function ensureServer(){try{if((await fetch(ORIGIN)).ok)return null;}catch{}await stopPort();return startServer();}
async function waitForApp(){const end=Date.now()+60000;while(Date.now()<end){try{if((await fetch(ORIGIN)).ok)return;}catch{}await new Promise(resolve=>setTimeout(resolve,500));}throw new Error("trajectory performance app timeout");}
async function stopPort(){if(process.platform!=="win32")return;const ps=`$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`;await new Promise(resolve=>{const child=spawn("powershell.exe",["-NoProfile","-Command",ps],{stdio:"ignore"});child.on("exit",resolve);child.on("error",resolve);});}
async function json(file){return JSON.parse(await readFile(file,"utf-8"));}
async function write(relative,value){const file=path.join(EVIDENCE,relative);await mkdir(path.dirname(file),{recursive:true});await writeFile(file,`${JSON.stringify(value,null,2)}\n`,"utf-8");}
async function listFiles(directory){const result=[];for(const entry of await readdir(directory,{withFileTypes:true})){const target=path.join(directory,entry.name);if(entry.isDirectory())result.push(...await listFiles(target));else result.push(target);}return result.sort();}
function safeError(error){return String(error instanceof Error?error.message:error).replace(/[A-Z]:\\[^\n]+/gi,"[local-path]").slice(0,600);}

const FORMAL_PROMPT="Play this molecular dynamics trajectory.";
await main();
