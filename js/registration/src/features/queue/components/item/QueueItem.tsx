import { QueueItem } from "#src/features/queue/types"
import { Box, Menu, Text } from "@mantine/core"
import {
  IconArrowDown,
  IconArrowsMoveHorizontal,
  IconTrash,
} from "@tabler/icons-react"

export type QueueItemProps = {
  queueItem: QueueItem
  canHide?: boolean
  onHide?: () => void
  onAssign?: () => void
  onRemove?: () => void
}

export const QueueItemComponent = (props: QueueItemProps) => {
  const { queueItem, canHide, onHide, onAssign, onRemove } = props
  return (
    <Menu>
      <Menu.Target>
        <Box className="QueueItem-root">
          {((!!queueItem.first_name || !!queueItem.last_name) && (
            <>
              <Text className="QueueItem-firstName" span>
                {queueItem.first_name}
              </Text>
              <Text className="QueueItem-lastName" span>
                {queueItem.last_name}
              </Text>
            </>
          )) || (
            <Text className="QueueItem-unknown" span>
              Unknown
            </Text>
          )}
          <Text className="QueueItem-duration" span>
            {queueItem.duration ? formatTime(queueItem.duration) : "--:--"}
          </Text>
          <Text className="QueueItem-assignment">{queueItem.station_id}</Text>
        </Box>
      </Menu.Target>
      <Menu.Dropdown>
        <Menu.Label>Change</Menu.Label>
        {canHide && (
          <Menu.Item
            leftSection={<IconArrowDown />}
            onClick={() => onHide && onHide()}
          >
            Hide
          </Menu.Item>
        )}
        <Menu.Item
          leftSection={<IconArrowsMoveHorizontal />}
          onClick={() => onAssign && onAssign()}
        >
          Assign
        </Menu.Item>
        <Menu.Item
          leftSection={<IconTrash />}
          c="red"
          onClick={() => onRemove && onRemove()}
        >
          Remove
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
  )
}

const formatTime = (duration: number) => {
  const minutes = Math.floor(duration / 60)
  const seconds = Math.floor(duration % 60)
  const secondsStr = seconds < 10 ? `0${seconds}` : `${seconds}`
  return `${minutes}:${secondsStr}`
}
