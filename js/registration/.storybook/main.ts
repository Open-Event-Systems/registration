import type { StorybookConfig } from "@storybook/react-webpack5"
import path from "path"

const config: StorybookConfig = {
  stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|ts|tsx)"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
  ],
  framework: {
    name: "@storybook/react-webpack5",
    options: {},
  },
  docs: {
    autodocs: "tag",
  },
  webpackFinal: (config) => {
    return {
      ...config,
      cache: {
        type: "filesystem",
        cacheDirectory: path.resolve("./.cache/storybook-webpack"),
      },
      module: {
        rules: [
          ...(config.module?.rules ?? []),
          {
            test: /\.s[ac]ss$/,
            use: ["style-loader", "css-loader", "sass-loader"],
          },

          {
            test: /\.svg$/,
            exclude: /node_modules/,
            use: "svgo-loader",
            type: "asset/resource",
          },

          // babel-loader for all non-js source files
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
            ],
          },
        ],
      },
      resolve: {
        ...config.resolve,
        extensionAlias: {
          ".js": [".tsx", ".ts", ".jsx", ".js"],
        },
        alias: {
          ...config.resolve?.alias,

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
          "config.json$": path.resolve("./config.json"),
        },
      },
    }
  },
}
export default config
