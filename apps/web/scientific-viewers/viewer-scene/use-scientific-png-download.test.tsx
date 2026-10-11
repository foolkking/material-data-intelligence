import {act,fireEvent,render,screen,waitFor} from "@testing-library/react";
import {afterEach,describe,expect,it,vi} from "vitest";
import {useScientificPngDownload} from "./use-scientific-png-download";

function Harness({identity,create,onError}:{identity:string;create:()=>Promise<Blob>;onError:()=>void}){
  const png=useScientificPngDownload(identity);
  return <button disabled={png.busy} onClick={()=>void png.download(create,`${identity}.png`,onError)}>{png.busy?"busy":"download"}</button>;
}
afterEach(()=>vi.restoreAllMocks());
describe("scientific PNG download ownership",()=>{
  it("blocks duplicate clicks and discards old files without changing a new pending export",async()=>{
    const createUrl=vi.fn(()=>"blob:png");Object.defineProperty(URL,"createObjectURL",{configurable:true,value:createUrl});
    Object.defineProperty(URL,"revokeObjectURL",{configurable:true,value:vi.fn()});
    const click=vi.spyOn(HTMLAnchorElement.prototype,"click").mockImplementation(()=>{});
    let first!:(blob:Blob)=>void;let second!:(blob:Blob)=>void;
    const create=vi.fn(()=>new Promise<Blob>(resolve=>{first=resolve;}));
    const next=vi.fn(()=>new Promise<Blob>(resolve=>{second=resolve;}));
    const onError=vi.fn();
    const view=render(<Harness identity="first" create={create} onError={onError}/>);
    fireEvent.click(screen.getByRole("button"));fireEvent.click(screen.getByRole("button"));expect(create).toHaveBeenCalledOnce();
    view.rerender(<Harness identity="second" create={next} onError={onError}/>);
    fireEvent.click(screen.getByRole("button"));
    await act(async()=>first(new Blob(["old"])));
    expect(createUrl).not.toHaveBeenCalled();expect(screen.getByRole("button")).toBeDisabled();
    await act(async()=>second(new Blob(["current"])));
    expect(createUrl).toHaveBeenCalledOnce();expect(click).toHaveBeenCalledOnce();expect(onError).not.toHaveBeenCalled();
    expect(screen.getByRole("button")).toBeEnabled();
  });
  it("shows a current failure and restores the export action",async()=>{
    const onError=vi.fn();render(<Harness identity="field" create={async()=>{throw Error("encoding");}} onError={onError}/>);
    fireEvent.click(screen.getByRole("button"));
    await waitFor(()=>expect(onError).toHaveBeenCalledOnce());expect(screen.getByRole("button")).toBeEnabled();
  });
});
