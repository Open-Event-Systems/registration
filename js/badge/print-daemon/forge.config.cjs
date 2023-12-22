module.exports = {
  packagerConfig: {},
  makers: [],
  plugins: [
    {
      name: "@electron-forge/plugin-webpack",
      config: {
        loggerPort: 9001,
        mainConfig: "./main.config.cjs",
        renderer: {
          config: "./renderer.config.cjs",
          nodeIntegration: true,
          entryPoints: [
            {
              name: "renderer",
              html: "./src/renderer.html",
              js: "./src/renderer.ts",
              preload: {
                js: "./src/preload.ts",
              },
            },
          ],
        },
      },
    },
  ],
}
