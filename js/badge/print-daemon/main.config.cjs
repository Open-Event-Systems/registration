const config = (env, argv) => {
  return {
    mode: "production",
    entry: "./src/main.ts",
    module: {
      rules: [
        {
          test: /\.ts$/,
          use: "ts-loader",
        },
      ],
    },
    resolve: {
      extensions: [".ts", ".js"],
    },
  }
}

module.exports = config
