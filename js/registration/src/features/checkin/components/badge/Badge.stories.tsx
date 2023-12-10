import { Badge } from "#src/features/checkin/components/badge/Badge"
import { Meta, StoryObj } from "@storybook/react"

import "./Badge.css"

const meta: Meta<typeof Badge> = {
  component: Badge,
}

export default meta

export const Default: StoryObj<typeof Badge> = {
  args: {
    badgeUrl: "/?path=/settings/about",
  },
}
