import { createRouter, createWebHashHistory } from "vue-router";
import BatchInput from "../views/BatchInput.vue";
import PreviewEdit from "../views/PreviewEdit.vue";
import Dashboard from "../views/Dashboard.vue";

const routes = [
  { path: "/", redirect: "/batch-input" },
  { path: "/batch-input", component: BatchInput },
  { path: "/preview-edit", component: PreviewEdit },
  { path: "/dashboard", component: Dashboard },
];

export const router = createRouter({
  history: createWebHashHistory(),
  routes,
});
