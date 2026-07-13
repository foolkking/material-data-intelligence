import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../../..");
const child=spawn(process.execPath,["apps/web/test/viewer-scene-production-browser-evidence.mjs"],{
  cwd:root,
  env:{...process.env,MDI_FORMAL_VIEWER_REGISTRATION:"1",MDI_PRODUCTION_VIEWER_EVIDENCE_DIR:"docs/phase10f/evidence/phase10f27_structure_viewer_3d_product",MDI_VIEWER_PRODUCTION_EVIDENCE_PORT:process.env.MDI_VIEWER_FORMAL_PRODUCT_PORT||"3059"},
  stdio:"inherit",
});
child.on("exit",(code)=>{
  if(code!==0){process.exit(code??1);return;}
  const snapshots=spawn("uv",["run","python","apps/web/test/generate-viewer-3d-product-evidence.py","docs/phase10f/evidence/phase10f27_structure_viewer_3d_product"],{cwd:root,env:{...process.env,PYTHONIOENCODING:"utf-8"},stdio:"inherit"});
  snapshots.on("exit",(snapshotCode)=>process.exit(snapshotCode??1));
  snapshots.on("error",(error)=>{console.error(error);process.exit(1);});
});
child.on("error",(error)=>{console.error(error);process.exit(1);});
