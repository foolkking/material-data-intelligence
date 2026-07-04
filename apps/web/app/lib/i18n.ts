import { enUS } from "./messages/en-US";
import { zhCN } from "./messages/zh-CN";

export type Locale = "zh-CN" | "en-US";
export type MessageKey = keyof typeof zhCN;
type Messages = Record<MessageKey, string>;

export const dictionaries = {
  "zh-CN": zhCN,
  "en-US": enUS
} satisfies Record<Locale, Messages>;

export function createTranslator(locale: Locale) {
  const messages = dictionaries[locale];
  return function t(key: MessageKey): string {
    return messages[key] || zhCN[key] || key;
  };
}
