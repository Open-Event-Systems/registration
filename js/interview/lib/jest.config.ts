import type { JestConfigWithTsJest } from "ts-jest"

const config: JestConfigWithTsJest = {
  clearMocks: true,
  collectCoverage: true,
  coverageDirectory: "coverage",
  coverageProvider: "v8",
  testEnvironment: "jsdom",
  testEnvironmentOptions: {
    customExportConditions: ["node", "test"],
  },
  extensionsToTreatAsEsm: [".ts"],
  transform: {
    "\\.ts$": [
      "ts-jest",
      {
        useESM: true,
        tsconfig: "<rootDir>/src/test/tsconfig.json",
      },
    ],
  },
}

export default config
