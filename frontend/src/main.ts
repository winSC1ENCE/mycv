import { createApp } from "vue";
import { createPinia } from "pinia";
import { createI18n } from "vue-i18n";

import App from "./App.vue";
import router from "./router";
import en from "./locales/en.json";
import de from "./locales/de.json";

import "./styles/tokens.css";
import "./styles/normal.css";
import "./styles/dog.css";
import "./styles/app.css";

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem("mycv:locale") ?? "en",
  fallbackLocale: "en",
  messages: { en, de },
});

createApp(App).use(createPinia()).use(router).use(i18n).mount("#app");
