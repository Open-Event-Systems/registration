import type { StorybookConfig } from "@storybook/react-webpack5"
import path from "path"
import { Configuration } from "webpack"

const config: StorybookConfig = {
  stories: ["../stories/**/*.mdx", "../stories/**/*.stories.@(js|jsx|ts|tsx)"],
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
  webpackFinal(config, options) {
    return {
      ...config,
      resolve: {
        ...config.resolve,
        extensionAlias: {
          ".js": [".tsx", ".ts", ".jsx", ".js"],
        },
      },
    } as Configuration
  },
  // webpackFinal(config, options) {
  //   return {
  //     ...config,
  //     module: {
  //       ...config.module,
  //       rules: [
  //         ...(config.module?.rules ?? []),
  //         {
  //           include: [path.resolve("../lib")],
  //           exclude: /node_modules/,
  //           use: [
  //             {
  //               loader: "babel-loader",
  //               options: {
  //                 presets: ["@babel/preset-env", "@babel/preset-typescript"],
  //               },
  //             },
  //           ],
  //         },
  //       ],
  //     },
  //   }
  // },
}
export default config
