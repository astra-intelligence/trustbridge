import { defineConfig } from "vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  resolve: {
    tsconfigPaths: true,
  },
  plugins: [
    tanstackStart({
      spa: { enabled: true },
    }),
    tailwindcss(),
    react(),
  ],
  build: {
    minify: false,
    cssMinify: false,
    outDir: ".output/public",
  },
});
