import path from "path"
import HtmlWebpackPlugin from "html-webpack-plugin"
import { Configuration, DefinePlugin } from "webpack"
import MiniCssExtractPlugin from "mini-css-extract-plugin"
import "webpack-dev-server"

const config = (env: Record<string, unknown>, argv: Record<string, unknown>): Configuration => {
  const prod = argv.mode !== "development"

  return {
    mode: prod ? "production" : "development",
    entry: {
      selfservice: "./src/features/selfservice/index.tsx",
      receipt: "./src/features/receipt/index.tsx",
    },
    output: {
      publicPath: "/", // TODO: make configurable
      filename: prod ? "assets/js/[name].[contenthash].bundle.js" : undefined,
      path: path.resolve("./dist"),
      clean: prod,
    },
    module: {
      rules: [
        // babel-loader for all non-js source files, or js files in the project
        {
          oneOf: [
            {
              test: /\.(tsx?|jsx)$/,
              use: {
                loader: "babel-loader",
                options: {
                  presets: [
                    "@babel/preset-env",
                    [
                      "@babel/preset-react",
                      {
                        runtime: "automatic",
                      },
                    ],
                    "@babel/preset-typescript",
                  ],
                  plugins: ["@babel/plugin-transform-runtime"],
                },
              },
            },
            {
              test: /\.js$/,
              exclude: /node_modules/,
              use: "babel-loader",
            },
          ],
        },

        // css files
        {
          test: /\.css$/,
          use: [MiniCssExtractPlugin.loader, "css-loader"],
        },
        {
          test: /\.s[ca]ss$/,
          use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"],
        },

        // config.json
        {
          test: /config(\.example)?\.json$/,
          type: "asset/resource",
          generator: {
            filename: "config.json",
          },
        },

        // resources

        // svg files -> SVGO
        {
          test: /\.svg$/,
          exclude: /node_modules/,
          use: "svgo-loader",
          type: "asset/resource",
        },
      ],
    },
    resolve: {
      extensions: [".tsx", ".ts", "..."],
      extensionAlias: {
        ".js": [".tsx", ".ts", ".js"],
      },
      alias: {
        // overridable theme file
        "#src/config/theme$": [
          path.resolve("./theme.ts"),
          path.resolve("./src/config/theme.ts"),
        ],

        // logo
        "logo.svg$": [
          path.resolve("./logo.svg"),
          path.resolve("./resources/example-logo.svg"),
        ],

        // config.json
        "config.json$": [
          path.resolve("./config.json"),
          path.resolve("./config.example.json"),
        ],
      },
    },
    plugins: [
      // env vars
      new DefinePlugin({
        "process.env.DELAY": JSON.stringify(process.env.DELAY),
      }),
      new MiniCssExtractPlugin(),
      // html page for each entry point
      new HtmlWebpackPlugin({
        title: "Registration",
        template: "./src/index.html",
        chunks: ["selfservice"],
        filename: "index.html",
      }),
      new HtmlWebpackPlugin({
        title: "Receipt",
        template: "./src/index.html",
        chunks: ["receipt"],
        filename: "receipt/index.html",
      }),
    ],
    // source map config
    devtool: prod ? false : "eval-cheap-source-map",
    devServer: {
      historyApiFallback: {
        rewrites: [
          { from: /^\/receipt(\/|$)/, to: "/receipt/index.html" },
          { from: /^\//, to: "/index.html" },
        ],
      },
      port: 9000,
    },
    cache: {
      // cache on filesystem for CI and to reduce memory usage
      type: "filesystem",
      cacheDirectory: path.resolve("./.cache/webpack"),
    },
    optimization: {
      splitChunks: {
        chunks: prod ? "all" : undefined,
      },
    },
  }
}

export default config
