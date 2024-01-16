import { QueueItemComponent } from "#src/features/queue/components/item/QueueItem"
import { Station } from "#src/features/queue/components/station/Station"
import { Meta, StoryObj } from "@storybook/react"

import "../item/QueueItem.scss"
import "./Station.scss"

const meta: Meta<typeof Station> = {
  component: Station,
  parameters: {
    layout: "centered",
  },
}

export default meta

export const Default: StoryObj<typeof Station> = {
  args: {
    stationId: "Station 1",
  },
  render(args) {
    return (
      <Station {...args}>
        <QueueItemComponent
          queueItem={{
            id: "1",
            first_name: "Example",
            last_name: "Person",
            date_created: "2020-01-01T00:00:00+00:00",
            station_id: "1",
          }}
        />
        <QueueItemComponent
          queueItem={{
            id: "2",
            first_name: "Example",
            last_name: "Person 2",
            date_created: "2020-01-01T00:00:00+00:00",
            station_id: "1",
            duration: 42,
          }}
        />
      </Station>
    )
  },
}

export const Empty: StoryObj<typeof Station> = {
  args: {
    stationId: "Station 2",
  },
  render(args) {
    return <Station {...args}></Station>
  },
}
