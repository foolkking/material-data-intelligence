import { afterEach, describe, expect, it, vi } from "vitest";
import { composeBrillouinZoneImage, encodeBrillouinZonePng } from "./brillouinZoneExport";

function drawingContext() {
  const text: Array<{text:string;x:number;y:number;color:string}> = [];
  const context = {
    font:"",fillStyle:"",strokeStyle:"",lineWidth:1,textAlign:"",textBaseline:"",
    scale:vi.fn(),drawImage:vi.fn(),measureText:vi.fn((value:string)=>({width:value.length*12})),
    beginPath:vi.fn(),moveTo:vi.fn(),lineTo:vi.fn(),stroke:vi.fn(),arc:vi.fn(),fill:vi.fn(),fillRect:vi.fn(),strokeRect:vi.fn(),
    fillText:vi.fn((value:string,x:number,y:number)=>text.push({text:value,x,y,color:context.fillStyle})),
  };
  vi.spyOn(HTMLCanvasElement.prototype,"getContext").mockReturnValue(context as unknown as CanvasRenderingContext2D);
  return {context,text};
}
afterEach(()=>{vi.restoreAllMocks();vi.useRealTimers();});

describe("Brillouin-zone PNG composition",()=>{
  it.each(["light","dark","transparent"] as const)("includes readable labels and unchanged anchors on %s backgrounds",background=>{
    const {context,text}=drawingContext();
    const source=document.createElement("canvas");
    const labels=[{id:"gamma",text:"Γ",x:800,y:600,selected:false},{id:"r",text:"R",x:800,y:600,selected:true}];
    const canvas=composeBrillouinZoneImage(source,{width:1600,height:1200,pixelRatio:2,background},labels);
    expect([canvas.width,canvas.height]).toEqual([3200,2400]);
    expect(context.scale).toHaveBeenCalledWith(2,2);
    expect(context.drawImage).toHaveBeenCalledWith(source,0,0,1600,1200);
    expect(text.map(item=>item.text)).toEqual(["Γ","R"]);
    expect(context.moveTo.mock.calls).toEqual([[800,600],[800,600]]);
    const [first,second]=context.fillRect.mock.calls as number[][];
    expect(first[0]+first[2]<=second[0]||second[0]+second[2]<=first[0]||first[1]+first[3]<=second[1]||second[1]+second[3]<=first[1]).toBe(true);
    expect(text[0].color).toBe(background==="dark"?"#ffd0c8":"#7d2f28");
    expect(text[1].color).toBe(background==="dark"?"#152731":"#ffffff");
  });

  it("fails visibly instead of silently dropping crowded labels",()=>{
    drawingContext();
    const labels=Array.from({length:128},(_,index)=>({id:String(index),text:`point ${index}`,x:128,y:128,selected:false}));
    expect(()=>composeBrillouinZoneImage(document.createElement("canvas"),{width:256,height:256,pixelRatio:1,background:"light"},labels)).toThrow("BZ_EXPORT_LABELS_DO_NOT_FIT");
  });

  it("bounds stalled encoding and releases the output bitmap",async()=>{
    vi.useFakeTimers();
    const canvas=document.createElement("canvas");
    canvas.width=1600;canvas.height=1200;
    canvas.toBlob=vi.fn();
    const result=encodeBrillouinZonePng(canvas);
    const rejected=expect(result).rejects.toThrow("BZ_EXPORT_TIMEOUT");
    await vi.advanceTimersByTimeAsync(15_000);
    await rejected;
    expect([canvas.width,canvas.height]).toEqual([0,0]);
  });
});
