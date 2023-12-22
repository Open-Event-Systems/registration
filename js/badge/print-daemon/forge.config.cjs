module.exports = {
  packagerConfig: {
    name: "print-daemon",
  },
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
