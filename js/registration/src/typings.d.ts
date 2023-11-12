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

declare module "*.css" {
  const value: string
  export default value
}
