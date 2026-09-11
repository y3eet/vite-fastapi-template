import { defineConfig, loadEnv } from "vite";
import { heyApiPlugin } from "@hey-api/vite-plugin";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import path from "path";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    resolve: {
      alias: {
        "@": path.resolve(import.meta.dirname, "./src"),
      },
    },
    plugins: [
      heyApiPlugin({
        config: {
          input: {
            path: env.VITE_API_URL + "/openapi.json",
            watch: true,
          },
          output: "src/client",
          plugins: [
            "@hey-api/client-fetch",
            "@hey-api/typescript",
            "@hey-api/sdk",
            "@tanstack/react-query",
          ],
        },
        vite: { apply: "serve" },
      }),
      tailwindcss(),
      tanstackRouter({ target: "react", autoCodeSplitting: true }),
      react(),
    ],
  };
});
