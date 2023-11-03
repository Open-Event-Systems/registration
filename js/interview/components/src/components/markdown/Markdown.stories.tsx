import { Markdown } from "#src/components/markdown/Markdown.js"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof Markdown> = {
  component: Markdown,
}

export default meta

export const Default: StoryObj<typeof Markdown> = {
  args: {
    content: `
#### Example

Example **markdown content**.
    `,
  },
}
