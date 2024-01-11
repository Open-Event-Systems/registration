import { QueueItemComponent } from "#src/features/queue/components/item/QueueItem"
import { Meta, StoryObj } from "@storybook/react"

import "./QueueItem.scss"

const meta: Meta<typeof QueueItemComponent> = {
  component: QueueItemComponent,
  parameters: {
    layout: "centered",
  },
}

export default meta

export const Default: StoryObj<typeof QueueItemComponent> = {
  args: {
    queueItem: {
      id: "1",
      date_created: "2020-01-01T00:00:00+00:00",
      duration: 92,
      first_name: "Example",
      last_name: "Person",
    },
    canHide: true,
  },
}

export const Assigned: StoryObj<typeof QueueItemComponent> = {
  args: {
    queueItem: {
      id: "1",
      date_created: "2020-01-01T00:00:00+00:00",
      duration: 35,
      first_name: "Example",
      last_name: "Person",
      station_id: "1",
    },
    canHide: true,
  },
}

export const Unknown: StoryObj<typeof QueueItemComponent> = {
  args: {
    queueItem: {
      id: "1",
      date_created: "2020-01-01T00:00:00+00:00",
      duration: 122,
      station_id: "1",
    },
    canHide: true,
  },
}
