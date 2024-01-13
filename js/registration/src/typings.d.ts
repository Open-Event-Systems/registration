declare module "config.json" {
  import { Config } from "#src/types/config"
  const value: Config
  export default value
}

declare module "*.svg" {
  const value: string
  export default value
}

declare module "*.module.css" {
  const value: Record<string, string>
  export default value
}

declare module "*.module.scss" {
  const value: Record<string, string>
  export default value
}

declare module "*.scss" {
  const value: string
  export default value
}

declare module "*.css" {
  const value: string
  export default value
}
