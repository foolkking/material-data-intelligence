import "@testing-library/jest-dom/vitest";
import {render,screen} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {describe,expect,it} from "vitest";
import {PhononAnimationPreviewPanel} from "../PlannerWorkbench";
import {phononAnimationFixture} from "./phononAnimationTestFixture";

describe("PhononAnimationPreviewPanel",()=>{
  it("integrates the formal product with renderer, inert JSON, and manifest tabs",async()=>{const payload=phononAnimationFixture();const manifest={schema_version:"phase10h5.phonon_animation_manifest.v1",tool_id:"phonon.animation",mode_id:payload.mode.mode.mode_id,artifacts:[],renderer:{included:false,application_owned:true,external_assets:[]},security:payload.security};render(<PhononAnimationPreviewPanel artifacts={[{id:"animation",type:"phonon_animation_json",name:"phonon_animation.json",content:payload},{id:"manifest",type:"phonon_animation_manifest_json",name:"phonon_animation_manifest.json",content:manifest}]}/>);expect(screen.getByTestId("phonon-animation-preview-panel")).toHaveTextContent("Formal phonon.animation product");expect(screen.getByTestId("phonon-animation-fallback")).toHaveTextContent("PHONON_ANIMATION_WEBGL_UNSUPPORTED");await userEvent.click(screen.getByRole("tab",{name:"Animation JSON"}));expect(screen.getByTestId("phonon-animation-json-preview")).toHaveTextContent("phase10h5.phonon_animation.v1");await userEvent.click(screen.getByRole("tab",{name:"Manifest"}));expect(screen.getByTestId("phonon-animation-manifest-preview")).toHaveTextContent("application_owned");});
  it("does not render without an animation artifact",()=>{const{container}=render(<PhononAnimationPreviewPanel artifacts={[]}/>);expect(container).toBeEmptyDOMElement();});
});
