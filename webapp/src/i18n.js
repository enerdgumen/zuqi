import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import resources from "./i18n.json";

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    detection: {
      order: ['querystring', 'path', 'subdomain', 'localStorage', 'navigator'],
    },
    keySeparator: false,
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
