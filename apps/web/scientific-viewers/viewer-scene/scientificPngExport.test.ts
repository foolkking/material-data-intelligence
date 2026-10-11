import {afterEach,describe,expect,it,vi} from "vitest";
import {captureScientificCanvas,createScientificPngExporter,decodeScientificImage} from "./scientificPngExport";

afterEach(()=>{vi.restoreAllMocks();vi.useRealTimers();vi.unstubAllGlobals();});
describe("scientific PNG lifecycle",()=>{
  it("copies the frame before encoding and prevents concurrent captures",async()=>{
    let callback!:BlobCallback;
    let encoded:HTMLCanvasElement|undefined;
    const drawImage=vi.fn();
    vi.spyOn(HTMLCanvasElement.prototype,"getContext").mockReturnValue({drawImage} as unknown as CanvasRenderingContext2D);
    vi.spyOn(HTMLCanvasElement.prototype,"toBlob").mockImplementation(function(this:HTMLCanvasElement,next){encoded=this;callback=next;});
    const source=document.createElement("canvas");source.width=1200;source.height=900;
    const capture=vi.fn(()=>captureScientificCanvas(source));
    const exportPng=createScientificPngExporter(capture);
    const pending=exportPng();
    expect(drawImage).toHaveBeenCalledWith(source,0,0);
    source.width=320;source.height=240;
    expect([encoded!.width,encoded!.height]).toEqual([1200,900]);
    await expect(exportPng()).rejects.toThrow("VIEWER_EXPORT_IN_PROGRESS");
    expect(capture).toHaveBeenCalledOnce();
    callback(new Blob(["png"],{type:"image/png"}));
    await expect(pending).resolves.toBeInstanceOf(Blob);
    expect([encoded!.width,encoded!.height]).toEqual([0,0]);
  });
  it("releases a timed-out image and permits retry",async()=>{
    vi.useFakeTimers();
    const canvas=document.createElement("canvas");canvas.toBlob=vi.fn();
    const exporter=createScientificPngExporter(()=>canvas);
    const pending=expect(exporter()).rejects.toThrow("VIEWER_EXPORT_TIMEOUT");
    await vi.advanceTimersByTimeAsync(15_000);await pending;
    canvas.width=10;canvas.height=10;
    canvas.toBlob=callback=>callback(new Blob(["png"]));
    await expect(exporter()).resolves.toBeInstanceOf(Blob);
  });
  it("closes a bitmap that arrives after a decode timeout",async()=>{
    vi.useFakeTimers();let finish!:(bitmap:ImageBitmap)=>void;
    vi.stubGlobal("createImageBitmap",vi.fn(()=>new Promise(resolve=>{finish=resolve;})));
    const pending=expect(decodeScientificImage(new Blob(["png"]))).rejects.toThrow("VIEWER_EXPORT_DECODE_TIMEOUT");
    await vi.advanceTimersByTimeAsync(15_000);await pending;
    const close=vi.fn();finish({close} as unknown as ImageBitmap);
    await Promise.resolve();expect(close).toHaveBeenCalledOnce();
  });
});
