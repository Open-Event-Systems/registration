import path from "path"
import HtmlWebpackPlugin from "html-webpack-plugin"
import { Configuration, DefinePlugin, Module, NormalModule } from "webpack"
import MiniCssExtractPlugin from "mini-css-extract-plugin"
import "webpack-dev-server"
import CssMinimizerPlugin from "css-minimizer-webpack-plugin"


const config = (env: Record<string, unknown>, argv: Record<string, unknown>): Configuration => {
  const prod = argv.mode !== "development"

  return {
    mode: prod ? "production" : "development",
    entry: {
      main: "./src/routes/index.tsx",
      receipt: "./src/features/receipt/index.tsx",
    },
    output: {
      publicPath: "/", // TODO: make configurable
      filename: prod ? "assets/js/[name].[contenthash].js" : undefined,
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
            // do transpile tanstack
            {
              test: /@tanstack.*\.js$/,
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
          ],
        },

        // css files
        {
          test: /\.css$/,
          use: [MiniCssExtractPlugin.loader, "css-loader"],
        },
        {
          oneOf: [
            {
              test: [
                path.resolve("./theme.scss"),
                path.resolve("./src/config/theme.scss"),
              ],
              use: "sass-loader",
              type: "asset/resource",
              generator: {
                filename: "theme.css"
              }
            },
            {
              test: /\.s[ca]ss$/,
              use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"],
            },
          ]
        },

        // resources

        // consistent name for logo
        {
          test: [
            path.resolve("./logo.svg"),
            path.resolve("./resources/example-logo.svg"),
          ],
          generator: {
            filename: "logo.svg",
          }
        },

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

        // overridable theme styles
        "#src/config/theme.scss$": [
          path.resolve("./theme.scss"),
          path.resolve("./src/config/theme.scss"),
        ],

        // logo
        "logo.svg$": [
          path.resolve("./logo.svg"),
          path.resolve("./resources/example-logo.svg"),
        ],

        // overridable config file
        "#src/config/config$": [
          path.resolve("./config.ts"),
          path.resolve("./src/config/config.ts"),
        ],
      },
    },
    plugins: [
      // env vars
      new DefinePlugin({
        "process.env.DELAY": JSON.stringify(process.env.DELAY),
      }),
      new MiniCssExtractPlugin({
        ...(prod ? {
          filename: "assets/css/[name].[contenthash].css",
        } : {})
      }),
      // html page for each entry point
      new HtmlWebpackPlugin({
        title: "Registration",
        template: "./src/index.html",
        chunks: ["main"],
        filename: "index.html",
        inject: false
      }),
      new HtmlWebpackPlugin({
        title: "Receipt",
        template: "./src/index.html",
        chunks: ["receipt"],
        filename: "receipt/index.html",
        inject: false
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
      client: {
        overlay: {
          runtimeErrors: (error) => {
            if ("status" in error && error.status == 404) {
              return false
            }
            return true
          }
        }
      },
      port: 9000,
    },
    cache: {
      // cache on filesystem for CI and to reduce memory usage
      type: "filesystem",
      cacheDirectory: path.resolve("./.cache/webpack"),
    },
    optimization: {
      minimizer: [
        "...",
        new CssMinimizerPlugin(),
      ],
      splitChunks: {
        chunks: prod ? "all" : undefined,
        cacheGroups: {
          // specific names for config/theme
          config: {
            test: (module: Module) => {
              return module instanceof NormalModule && module.rawRequest == "#src/config/config"
            },
            usedExports: false,
            enforce: true,
            name: "config",
            filename: "config.js"
          },
          theme: {
            test: (module: Module) => {
              return module instanceof NormalModule && module.rawRequest == "#src/config/theme"
            },
            usedExports: false,
            enforce: true,
            name: "theme",
            filename: "theme.js"
          },
        }
      },
    },
  }
}

export default config
