import { defineConfig } from "vite";

console.log("NODE_ENV", process.env.NODE_ENV);
export default defineConfig({
  base: "./",
  define: {
    __DEV__: process.env.NODE_ENV !== "production",
  },
});
