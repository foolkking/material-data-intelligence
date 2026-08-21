import { redirect } from "next/navigation";

export default function ModelSettingsRoute() {
  redirect("/console?settings=models");
}
