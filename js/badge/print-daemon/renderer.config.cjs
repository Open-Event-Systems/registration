const config = (env, argv) => {
  return {
    mode: "production",
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
